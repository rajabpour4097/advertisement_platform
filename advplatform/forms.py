from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Resume
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
    file = forms.FileField(label='فایل رزومه', required=True)

    class Meta:
        model = Resume
        fields = ['title', 'describe', 'file']
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file

        allowed_types = [
            'application/pdf', 
            'image/jpeg', 
            'image/png',
            'application/zip',
            'application/x-zip-compressed'
        ]
        
        if file.content_type not in allowed_types:
            raise forms.ValidationError('فقط فایل‌های PDF، عکس (JPG/PNG) یا ZIP مجاز هستند.')

        if file.size > 10 * 1024 * 1024:  # 10 مگابایت محدودیت حجم
            raise forms.ValidationError('حداکثر حجم فایل ۱۰ مگابایت است.')

        return file


class ResumeReviewForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['status', 'manager_comment']
