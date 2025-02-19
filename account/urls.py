from django.urls import path
from account.views import (
    AccountView,
    CampaignActivateView,
    CampaignCancelView,
    CampaignCreateView,
    CampaignDeactivateView,
    CampaignDeleteView,
    CampaignEditView,
    CampaignParticipateView,
    CampaignReviewView,
    CampaignListView,
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
    path('campaigns/', CampaignListView.as_view(), name='campaigns'), 
    path('campaigns/create', CampaignCreateView.as_view(), name='campaigncreate'),
    path('campaigns/delete/<int:pk>', CampaignDeleteView.as_view(), name='campaignsdelete'), 
    path('campaigns/deactive/<int:pk>', CampaignDeactivateView.as_view(), name='deactivecampaign'), 
    path('campaigns/active/<int:pk>', CampaignActivateView.as_view(), name='activecampaign'), 
    path('campaigns/cancel/<int:pk>', CampaignCancelView.as_view(), name='cancelcampaign'), 
    path('campaigns/review/<int:pk>', CampaignReviewView.as_view(), name='reviewcampaign'), 
    path('campaigns/edit/<int:pk>/', CampaignEditView.as_view(), name='campaignedit'),
    path('campaigns/participate/<int:pk>/', CampaignParticipateView.as_view(), name='campaignparticipate'),
     
]