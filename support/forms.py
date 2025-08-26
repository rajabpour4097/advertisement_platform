from django import forms
from .models import Ticket, TicketMessage, TicketRating, SupportDepartment, SupportSubject, LiveChatSession, LiveChatMessage


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['department', 'subject', 'title', 'priority', 'attachment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # limit active departments/subjects
        self.fields['department'].queryset = SupportDepartment.objects.filter(is_active=True)
        self.fields['subject'].queryset = SupportSubject.objects.filter(is_active=True)


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4})
        }


class TicketRatingForm(forms.ModelForm):
    class Meta:
        model = TicketRating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'توضیح اختیاری'})
        }


class LiveChatStartForm(forms.ModelForm):
    class Meta:
        model = LiveChatSession
        fields = ['department']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = SupportDepartment.objects.filter(is_active=True)


class LiveChatMessageForm(forms.ModelForm):
    class Meta:
        model = LiveChatMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'پیام خود را بنویسید...'})
        }
