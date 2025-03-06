from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser




class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل کاربر'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'custom-class'}))
    
    def get_invalid_login_error(self):
        
        error_message = super().get_invalid_login_error().message
        error_message += " اگر حساب شما فعال نشده است، منتظر تأیید مدیریت باشید."
        
        return forms.ValidationError(
            error_message,
            code="invalid_login",
            params={"username": self.username_field.verbose_name},
        )
    

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'