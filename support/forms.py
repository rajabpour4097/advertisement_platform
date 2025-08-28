from django import forms
from .models import Ticket, TicketMessage, TicketRating, SupportDepartment, SupportSubject
from django.contrib.auth import get_user_model


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


"""Live chat forms removed."""


class TicketReassignForm(forms.Form):
    supporter = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label='پشتیبان جدید'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        User = get_user_model()
        qs = User.objects.filter(is_supporter=True, is_active=True)
        if user and hasattr(user, 'departments'):
            dept_ids = user.departments.values_list('id', flat=True)
            qs = qs.filter(departments__in=dept_ids).distinct()
            # معمولاً خود پشتیبان جاری نیازی نیست در لیست باشد
            qs = qs.exclude(pk=user.pk)
        self.fields['supporter'].queryset = qs
        self.fields['supporter'].help_text = 'انتخاب پشتیبان برای واگذاری (اختیاری)'
