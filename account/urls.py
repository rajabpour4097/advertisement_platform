from django.urls import path
from account.views import (
    AccountView,
    PasswordChange,
    PasswordChangeDone, 
    PortfolioCreateView,
    PortfolioDeleteView, 
    PortfolioEditView, 
    PortfolioListView,
    ProfileView
    )


app_name = 'account'

urlpatterns = [
    path('', AccountView.as_view(), name='home'),
    path('profile/', ProfileView.as_view(), name='profile'), 
    path('password_change/', PasswordChange.as_view(), name='password_change'), 
    path('password_change/done/', PasswordChangeDone.as_view(), name='password_change_done'), 
    path('portfolios/', PortfolioListView.as_view(), name='portfolios'), 
    path('portfolios/create', PortfolioCreateView.as_view(), name='portfoliocreate'), 
    path('portfolios/edit/<int:pk>', PortfolioEditView.as_view(), name='portfolioedit'), 
    path('portfolios/delete/<int:pk>', PortfolioDeleteView.as_view(), name='portfoliodelete'), 
]