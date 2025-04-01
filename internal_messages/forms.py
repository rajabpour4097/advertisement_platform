from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'body']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['receiver'].queryset = Message.get_allowed_receivers(user)
            
        # اضافه کردن کلاس‌های bootstrap
        self.fields['receiver'].widget.attrs.update({
            'class': 'form-control select2',  # از select2 برای جستجو استفاده می‌کنیم
            'placeholder': 'انتخاب گیرنده'
        })
        self.fields['subject'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'موضوع پیام'
        })
        self.fields['body'].widget.attrs.update({
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'متن پیام'
        })