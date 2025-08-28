"""Support ticket views (live chat removed)."""

from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    Ticket, TicketMessage, TicketRating,
    SupportDepartment, SupportSubject
)
from .forms import (
    TicketCreateForm, TicketMessageForm, TicketRatingForm
)

from account.utils.send_notification import send_notification


def _pick_supporter_for_department(department: SupportDepartment):
    """Return the supporter in the department with the lowest number of open/answering tickets.

    If no supporters are attached or all inactive, returns None.
    """
    supporters = department.supporters.filter(is_active=True, is_supporter=True)
    if not supporters.exists():
        return None
    # Count only this department's tickets that are not closed (open / waiting / answering)
    open_statuses = ['open', 'waiting', 'answering']
    supporters = supporters.annotate(
        active_tickets=Count(
            'assigned_tickets',
            filter=Q(assigned_tickets__department=department) & Q(assigned_tickets__status__in=open_statuses)
        )
    ).order_by('active_tickets', 'id')
    return supporters.first()


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'support/ticket_list.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        user = self.request.user
        qs = Ticket.objects.select_related('department', 'subject', 'supporter')
        if user.is_supporter:
            # Only tickets assigned to supporter OR unassigned in their departments
            dept_ids = user.departments.values_list('id', flat=True)
            qs = qs.filter(
                Q(supporter=user) | (Q(supporter__isnull=True) & Q(department_id__in=dept_ids))
            )
        else:
            qs = qs.filter(user=user)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-modified_at')


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketCreateForm
    template_name = 'support/ticket_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        supporter = _pick_supporter_for_department(form.instance.department)
        if supporter:
            form.instance.supporter = supporter
        self.object = form.save()
        # create initial message
        message_text = (self.request.POST.get('first_message') or self.request.POST.get('message') or '').strip()
        if message_text:
            TicketMessage.objects.create(
                ticket=self.object,
                sender=self.request.user,
                message=message_text,
                is_staff_reply=False
            )
        if supporter:
            send_notification(
                sender=self.request.user,
                recipient=supporter,
                verb='تیکت جدید',
                description=f'تیکت جدید #{self.object.id} به شما منتسب شد.'
            )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('support:ticket_detail', args=[self.object.pk])


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'support/ticket_detail.html'
    context_object_name = 'ticket'

    def dispatch(self, request, *args, **kwargs):
        ticket = self.get_object()
        user = request.user
        if user.is_supporter:
            # supporter can view only their assigned tickets or unassigned in their departments
            dept_ids = user.departments.values_list('id', flat=True)
            if not (ticket.supporter == user or (ticket.supporter is None and ticket.department_id in dept_ids)):
                return redirect('support:ticket_list')
        else:
            if ticket.user != user:
                return redirect('support:ticket_list')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        ticket = self.object
        form = TicketMessageForm(request.POST, request.FILES)
        if form.is_valid() and ticket.status != 'closed':
            msg = form.save(commit=False)
            msg.ticket = ticket
            msg.sender = request.user
            msg.is_staff_reply = request.user.is_supporter
            msg.save()
            # notify other side
            target = ticket.supporter if not request.user.is_supporter else ticket.user
            if target:
                send_notification(
                    sender=request.user,
                    recipient=target,
                    verb='پیام جدید تیکت',
                    description=f'پیام جدید در تیکت #{ticket.id}'
                )
            # update ticket status
            if request.user.is_supporter and ticket.status == 'open':
                ticket.status = 'answering'
                ticket.save(update_fields=['status', 'modified_at'])
            elif not request.user.is_supporter and ticket.status in ['waiting', 'answering']:
                ticket.status = 'answering'
                ticket.save(update_fields=['status', 'modified_at'])
            return redirect('support:ticket_detail', pk=ticket.pk)
        context = self.get_context_data(object=self.object, form=form)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = TicketMessageForm()
        # backward compatibility for templates expecting message_form
        context['message_form'] = context['form']
        # ordered messages for template (chronological)
        context['ordered_messages'] = self.object.messages.select_related('sender').order_by('created_at')
        # permission for posting new message
        user = self.request.user
        if self.object.status == 'closed':
            can_post = False
        elif user.is_supporter:
            can_post = True
        else:
            # user: block if their own message is the last one (منتظر پاسخ پشتیبان)
            last = context['ordered_messages'].last() if context['ordered_messages'].exists() else None
            can_post = (last is None) or (last.sender_id != user.id)
        context['can_post_message'] = can_post
        context['can_rate'] = (
            self.object.status == 'closed' and
            self.request.user == self.object.user and
            not hasattr(self.object, 'rating') and
            self.object.supporter is not None
        )
        return context


def ticket_close_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    if user != ticket.user and user != ticket.supporter:
        return redirect('support:ticket_list')
    if ticket.status != 'closed':
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
    ticket.save(update_fields=['status', 'closed_at', 'modified_at'])
    return redirect('support:ticket_detail', pk=pk)


def ticket_claim_view(request, pk):
    """Supporter claims an unassigned ticket from their department."""
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user
    if not user.is_authenticated or not user.is_supporter:
        return redirect('support:ticket_list')
    dept_ids = user.departments.values_list('id', flat=True)
    if ticket.supporter is not None or ticket.department_id not in dept_ids:
        return redirect('support:ticket_detail', pk=pk)
    with transaction.atomic():
        # re-fetch with lock
        locked = Ticket.objects.select_for_update().get(pk=pk)
        if locked.supporter is None:
            locked.supporter = user
            locked.status = 'answering'
            locked.save(update_fields=['supporter', 'status', 'modified_at'])
            send_notification(
                sender=user,
                recipient=locked.user,
                verb='تیکت منتسب شد',
                description=f'تیکت #{locked.id} به پشتیبان {user.get_full_name() or user.username} منتسب شد.'
            )
    return redirect('support:ticket_detail', pk=pk)


from .forms import TicketReassignForm

def ticket_reassign_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user
    if not user.is_authenticated or not user.is_supporter:
        return redirect('support:ticket_list')
    # only current supporter or staff can reassign
    if ticket.supporter != user and not (user.is_staff or user.is_superuser):
        return redirect('support:ticket_detail', pk=pk)
    if request.method == 'POST':
        form = TicketReassignForm(request.POST, user=user)
        if form.is_valid():
            new_supporter = form.cleaned_data['supporter']
            if new_supporter and new_supporter != ticket.supporter:
                old_supporter = ticket.supporter
                ticket.supporter = new_supporter
                ticket.status = 'answering'
                ticket.save(update_fields=['supporter', 'status', 'modified_at'])
                # notifications
                if old_supporter:
                    send_notification(
                        sender=user,
                        recipient=old_supporter,
                        verb='تیکت واگذار شد',
                        description=f'تیکت #{ticket.id} به {new_supporter.get_full_name() or new_supporter.username} واگذار شد.'
                    )
                send_notification(
                    sender=user,
                    recipient=new_supporter,
                    verb='تیکت جدید',
                    description=f'تیکت #{ticket.id} به شما واگذار شد.'
                )
                send_notification(
                    sender=user,
                    recipient=ticket.user,
                    verb='واگذاری تیکت',
                    description=f'تیکت #{ticket.id} به پشتیبان جدید واگذار شد.'
                )
            return redirect('support:ticket_detail', pk=pk)
    else:
        form = TicketReassignForm(user=user)
    return render(request, 'support/ticket_reassign.html', {'ticket': ticket, 'form': form})


def ticket_rate_view(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if not request.user.is_authenticated or request.user != ticket.user:
        return redirect('support:ticket_list')
    if ticket.status != 'closed' or ticket.supporter is None or hasattr(ticket, 'rating'):
        return redirect('support:ticket_detail', pk=pk)
    if request.method == 'POST':
        form = TicketRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.ticket = ticket
            rating.supporter = ticket.supporter
            rating.user = request.user
            rating.save()
            send_notification(
                sender=request.user,
                recipient=ticket.supporter,
                verb='امتیاز جدید',
                description=f'کاربر برای تیکت #{ticket.id} امتیاز {rating.score} ثبت کرد.'
            )
            return redirect('support:ticket_detail', pk=pk)
    else:
        form = TicketRatingForm()
    return render(request, 'support/ticket_rate.html', {'ticket': ticket, 'form': form})

