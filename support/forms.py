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
        # Set widget ids (names unchanged)
        self.fields['department'].widget.attrs.update({'id': 'id_department_select'})
        self.fields['subject'].widget.attrs.update({'id': 'id_subject_select'})

        # Populate subject queryset based on selected department (POST or initial)
        subj_field = self.fields['subject']
        dept_val = None
        if self.data.get('department'):
            dept_val = self.data.get('department')
        elif self.initial.get('department'):
            dept_val = self.initial.get('department')
        elif getattr(self.instance, 'department_id', None):
            dept_val = self.instance.department_id

        if dept_val:
            try:
                dept_id = int(dept_val)
            except (TypeError, ValueError):
                dept_id = None
            if dept_id:
                subj_field.queryset = SupportSubject.objects.filter(department_id=dept_id, is_active=True)
                # ensure not disabled when we have options
                attrs = subj_field.widget.attrs
                if 'disabled' in attrs:
                    attrs.pop('disabled', None)
        else:
            subj_field.queryset = SupportSubject.objects.none()
            # keep disabled until department is selected
            subj_field.widget.attrs['disabled'] = 'disabled'

    
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
