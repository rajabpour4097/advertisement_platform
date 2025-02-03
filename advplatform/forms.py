from django import forms
from django.contrib.auth.forms import AuthenticationForm



class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'custom-class'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'custom-class'}))
