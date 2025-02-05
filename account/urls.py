from django.urls import path
from django.contrib.auth import views as auth_views

from account.views import AccountView


app_name = 'account'

urlpatterns = [
    path('', AccountView.as_view(), name='home'),
 
]