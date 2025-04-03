from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Message
from .forms import MessageForm
from django.http import JsonResponse
from django.views.generic.edit import DeleteView
from django.views.generic import View

class InboxView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'messages/inbox.html'
    context_object_name = 'messages'
    
    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Message.objects.filter(
            receiver=self.request.user,
            is_read=False
        ).count()
        return context
    

class SentView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'messages/sent.html'
    context_object_name = 'messages'
    
    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)
    

class ComposeView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'messages/compose.html'
    success_url = reverse_lazy('messages:sent')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.sender = self.request.user
        messages.success(self.request, 'پیام با موفقیت ارسال شد.')
        return super().form_valid(form)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'messages/detail.html'
    
    def get_queryset(self):
        # کاربر فقط می‌تواند پیام‌های خودش را ببیند
        return Message.objects.filter(
            Q(sender=self.request.user) |
            Q(receiver=self.request.user)
        )
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # علامت‌گذاری پیام به عنوان خوانده شده
        if self.object.receiver == request.user and not self.object.is_read:
            self.object.is_read = True
            self.object.save()
        return response

class MessageDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            message = Message.objects.get(pk=pk)
            # بررسی دسترسی کاربر
            if message.sender == request.user or message.receiver == request.user:
                message.delete()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'شما اجازه حذف این پیام را ندارید'
                })
        except Message.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'پیام یافت نشد'
            })