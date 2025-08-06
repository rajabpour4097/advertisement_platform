from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Resume, Topic
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model




class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل کاربر'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'custom-class'}))
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # اجازه ورود به کاربران غیرفعال با is_active=False
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password, 
                check_active=False  # این پارامتر به authenticate اضافه می‌شود
            )
            
            if self.user_cache is None:
                raise ValidationError(
                    '',
                    code='invalid_login'
                )
            
            # بررسی وضعیت کاربر مشاور
            if self.user_cache.user_type == 'mentor' and not self.user_cache.is_active:
                raise ValidationError(
                    'حساب کاربری شما هنوز توسط مدیر تایید نشده است.',
                    code='inactive_mentor'
                )
                
        return self.cleaned_data


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, check_active=True, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            if check_active:
                if user.is_active:
                    return user
            else:
                return user  # برگرداندن کاربر حتی اگر غیرفعال باشد
        return None


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        

class ResumeForm(forms.ModelForm):
    file = forms.FileField(label='فایل رزومه', required=False)

    class Meta:
        model = Resume
        fields = [
            'title', 'dealer_type', 'service_area', 'describe', 
            'specialty_categories', 'services', 'socialmedia_and_sites',
            'tools_and_platforms', 'file', 'portfolios', 'partner_brand',
            'bank_account'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'dealer_type': forms.Select(attrs={'class': 'form-control'}),
            'describe': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'services': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'socialmedia_and_sites': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tools_and_platforms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'partner_brand': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تنظیم انتخاب‌های نوع مجری تبلیغات (فقط والدین)
        self.fields['dealer_type'].queryset = Topic.objects.filter(parent__isnull=True)
        self.fields['dealer_type'].empty_label = "انتخاب کنید..."
        
        # تنظیم انتخاب‌های دسته‌های تخصصی (ابتدا خالی)
        self.fields['specialty_categories'].queryset = Topic.objects.none()
        
        # اگر instance موجود است، دسته‌های تخصصی مربوطه را بارگذاری کن
        if 'instance' in kwargs and kwargs['instance'] and kwargs['instance'].dealer_type:
            self.fields['specialty_categories'].queryset = Topic.objects.filter(
                parent=kwargs['instance'].dealer_type
            )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file

        allowed_types = [
            'application/pdf', 
            'application/zip',
            'application/x-zip-compressed'
        ]
        
        if file.content_type not in allowed_types:
            raise forms.ValidationError('فقط فایل‌های PDF یا ZIP مجاز هستند.')

        if file.size > 10 * 1024 * 1024:  # 10 مگابایت محدودیت حجم
            raise forms.ValidationError('حداکثر حجم فایل ۱۰ مگابایت است.')

        return file

class ResumeReviewForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['status', 'manager_comment']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_status'
            }),
            'manager_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'نظر یا توضیحات مدیر در مورد رزومه...',
                'id': 'id_manager_comment'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # فقط وضعیت‌های مربوط به بررسی مدیر را نمایش دهید
        self.fields['status'].choices = [
            ('under_review', 'در حال بررسی'),
            ('needs_editing', 'نیاز به ویرایش'),
            ('approved', 'تایید شده'),
            ('rejected', 'رد شده'),
        ]
        
        # اجباری کردن کامنت برای وضعیت‌های خاص
        self.fields['manager_comment'].help_text = 'برای وضعیت "نیاز به ویرایش" و "رد شده" نوشتن توضیحات الزامی است.'
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        manager_comment = cleaned_data.get('manager_comment')
        
        # اجباری کردن کامنت برای وضعیت‌های خاص
        if status in ['needs_editing', 'rejected']:
            if not manager_comment or not manager_comment.strip():
                raise forms.ValidationError(
                    f'برای وضعیت "{dict(self.fields["status"].choices)[status]}" نوشتن توضیحات الزامی است.'
                )
        
        return cleaned_data
