from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Max
from .models import Ticket, TicketMessage, TicketRating, LiveChatSession, LiveChatMessage, SupportDepartment, SupportSubject, SupporterPresence
from .forms import (
    TicketCreateForm, TicketMessageForm, TicketRatingForm,
    LiveChatStartForm, LiveChatMessageForm
)


class TicketListView(LoginRequiredMixin, ListView):
    template_name = 'support/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.select_related('department', 'subject', 'supporter')
        if user.is_staff or user.is_am:
            # staff can filter
            dept = self.request.GET.get('department')
            supporter = self.request.GET.get('supporter')
            status = self.request.GET.get('status')
            if dept:
                qs = qs.filter(department_id=dept)
            if supporter:
                qs = qs.filter(supporter_id=supporter)
            if status:
                qs = qs.filter(status=status)
        else:
            qs = qs.filter(user=user)
        return qs


class TicketCreateView(LoginRequiredMixin, CreateView):
    template_name = 'support/ticket_create.html'
    model = Ticket
    form_class = TicketCreateForm
    success_url = reverse_lazy('support:ticket_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        # auto assign supporter based on department if only one supporter or round-robin can be added later
        department = form.cleaned_data['department']
        supporter = department.supporters.filter(is_active=True).order_by('id').first()
        if supporter:
            form.instance.supporter = supporter
        response = super().form_valid(form)
        # create initial message
        first_message = self.request.POST.get('first_message')
        if first_message:
            TicketMessage.objects.create(
                ticket=self.object,
                sender=self.request.user,
                message=first_message,
                is_staff_reply=False
            )
            self.object.last_response_time = self.object.created_at
            self.object.save(update_fields=['last_response_time'])
        return response


class TicketDetailView(LoginRequiredMixin, DetailView):
    template_name = 'support/ticket_detail.html'
    model = Ticket
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['message_form'] = TicketMessageForm()
        if self.object.is_closed() and self.object.supporter and not hasattr(self.object, 'rating') and self.request.user == self.object.user:
            ctx['rating_form'] = TicketRatingForm()
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # posting a message
        form = TicketMessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.ticket = self.object
            msg.sender = request.user
            msg.is_staff_reply = request.user.is_supporter or request.user.is_staff or request.user.is_am
            msg.save()
            self.object.last_response_time = timezone.now()
            # update status
            if msg.is_staff_reply:
                self.object.status = 'waiting'
            else:
                self.object.status = 'answering'
            self.object.save(update_fields=['last_response_time', 'status'])
        return redirect('support:ticket_detail', pk=self.object.pk)


def ticket_close_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user != ticket.user and not (request.user.is_supporter or request.user.is_staff or request.user.is_am):
        return HttpResponseForbidden()
    ticket.status = 'closed'
    ticket.closed_at = timezone.now()
    ticket.save(update_fields=['status', 'closed_at'])
    return redirect('support:ticket_detail', pk=pk)


def ticket_rate_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user != ticket.user or not ticket.is_closed() or not ticket.supporter:
        return HttpResponseForbidden()
    if hasattr(ticket, 'rating'):
        return redirect('support:ticket_detail', pk=pk)
    if request.method == 'POST':
        form = TicketRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.ticket = ticket
            rating.supporter = ticket.supporter
            rating.user = request.user
            rating.save()
            # update supporter rank simple average
            from django.db.models import Avg
            avg_rank = TicketRating.objects.filter(supporter=ticket.supporter).aggregate(a=Avg('score'))['a'] or 0
            ticket.supporter.rank = round(avg_rank)
            ticket.supporter.save(update_fields=['rank'])
    return redirect('support:ticket_detail', pk=pk)


# ---- Live Chat Views ----
class LiveChatHistoryListView(LoginRequiredMixin, ListView):
    template_name = 'support/livechat_history.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        user = self.request.user
        qs = LiveChatSession.objects.select_related('department', 'supporter')\
            .annotate(last_time=Max('messages__created_at'))
        # فقط برای نقش های مجاز (is_staff, is_am, is_supporter) قابل مشاهده است
        if user.is_supporter or user.is_staff or user.is_am:
            return qs
        # کاربران عادی اجازه دسترسی ندارند (برمی گردیم queryset خالی)
        return qs.none()

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and (request.user.is_supporter or request.user.is_staff or request.user.is_am)):
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden('دسترسی مجاز نیست')
        return super().dispatch(request, *args, **kwargs)


def livechat_start_view(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = LiveChatStartForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            dept = session.department
            # انتخاب پشتیبان: اول آنلاین ها سپس کمترین تعداد سشن فعال
            dept_supporters = dept.supporters.filter(is_active=True, is_supporter=True)
            # annotate presence
            online_ids = [p.supporter_id for p in SupporterPresence.objects.filter(supporter__in=dept_supporters) if p.is_online]
            candidates = dept_supporters
            if online_ids:
                candidates = candidates.filter(id__in=online_ids)
            # annotate active sessions count
            from django.db.models import Count, Q
            candidates = candidates.annotate(active_sessions=Count('assigned_live_chats', filter=Q(assigned_live_chats__is_active=True)))\
                                 .order_by('active_sessions', 'id')
            supporter = candidates.first()
            if supporter:
                session.supporter = supporter
            session.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'session_id': session.id})
            return redirect('support:livechat_history')
    else:
        form = LiveChatStartForm()
    from django.shortcuts import render
    return render(request, 'support/livechat_start.html', {'form': form})


def livechat_send_message(request, session_id):
    session = get_object_or_404(LiveChatSession, pk=session_id)
    if request.user not in [session.user, session.supporter] and not (request.user.is_staff or request.user.is_am):
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = LiveChatMessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.session = session
            msg.sender = request.user
            msg.is_supporter = request.user.is_supporter or request.user.is_staff or request.user.is_am
            msg.save()
            return JsonResponse({'ok': True, 'message_id': msg.id, 'created_at': msg.created_at})
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
    return JsonResponse({'ok': False}, status=405)


def livechat_messages(request, session_id):
    session = get_object_or_404(LiveChatSession, pk=session_id)
    if request.user not in [session.user, session.supporter] and not (request.user.is_staff or request.user.is_am):
        return HttpResponseForbidden()
    since = request.GET.get('since')  # ISO datetime string
    msgs = session.messages.select_related('sender').order_by('id')
    if since:
        from django.utils.dateparse import parse_datetime
        dt = parse_datetime(since)
        if dt:
            msgs = msgs.filter(created_at__gt=dt)
    data = []
    for m in msgs:
        data.append({
            'id': m.id,
            'sender': m.sender.get_full_name(),
            'is_supporter': m.is_supporter,
            'message': m.message,
            'created_at': m.created_at.isoformat(),
            'attachment': m.attachment.url if m.attachment else None,
        })
    return JsonResponse({'ok': True, 'messages': data})


def livechat_departments(request):
    # return list of active departments for widget
    depts = SupportDepartment.objects.filter(is_active=True).values('id', 'name')
    return JsonResponse({'ok': True, 'departments': list(depts)})


def livechat_ping(request):
    if not request.user.is_authenticated or not request.user.is_supporter:
        return JsonResponse({'ok': False}, status=403)
    presence, _ = SupporterPresence.objects.get_or_create(supporter=request.user)
    # auto last_seen updated by save (auto_now)
    return JsonResponse({'ok': True, 'online': presence.is_online})
