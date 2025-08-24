from django import forms
from .models import IssueReport


class IssueReportForm(forms.ModelForm):
    class Meta:
        model = IssueReport
        fields = ['description', 'attachment', 'page_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'شرح مشکل را وارد کنید...'}),
            'page_url': forms.HiddenInput(),
        }
