from django.urls import path
from account.views import (
    AccountView, 
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
    path('portfolios/', PortfolioListView.as_view(), name='portfolios'), 
    path('portfolios/create', PortfolioCreateView.as_view(), name='portfoliocreate'), 
    path('portfolios/edit/<int:pk>', PortfolioEditView.as_view(), name='portfolioedit'), 
    path('portfolios/delete/<int:pk>', PortfolioDeleteView.as_view(), name='portfoliodelete'), 
]