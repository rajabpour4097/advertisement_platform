from django.urls import path
from django.conf.urls import handler404
from account.views import (
    AccountView,
    ChangeStatusRequestForMentor,
    CampaignActivateView,
    CampaignCancelParticipateView,
    CampaignCancelView,
    CampaignCreateView,
    CampaignDeactivateView,
    CampaignDeleteView,
    CampaignEditView,
    CampaignParticipateView,
    CampaignReviewView,
    CampaignListView,
    ListOfRequestForMentor,
    MentorChooseView,
    MentorUsersList,
    MentorsList,
    MyMentor,
    NewMentorActivate,
    NotificationDetailView,
    NotificationsView,
    PasswordChange,
    PasswordChangeDone, 
    PortfolioCreateView,
    PortfolioDeleteView, 
    PortfolioEditView, 
    PortfolioListView,
    ProfileView,
    )
from advplatform.views import custom_404_view


app_name = 'account'

handler404 = custom_404_view


urlpatterns = [
    path('', AccountView.as_view(), name='home'),
    path('notifications/', NotificationsView.as_view(), name='notifications_list'),
    path('notifications/detail/<int:pk>', NotificationDetailView.as_view(), name='notifications_detail'),
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
    path('campaigns/cancelparticipate/<int:pk>', CampaignCancelParticipateView.as_view(), name='cancelcampaignparticipate'), 
    path('mentoruserslist/', MentorUsersList.as_view(), name='mentoruserslist'), 
    path('mymentor/', MyMentor.as_view(), name='mymentor'), 
    path('mentorslist/', MentorsList.as_view(), name='mentorslist'), 
    path('mentor/choosementor/<int:pk>', MentorChooseView.as_view(), name='choosementor'), 
    path('mentor/activementor/<int:pk>', NewMentorActivate.as_view(), name='activementor'), 
    path('requestformentor/', ListOfRequestForMentor.as_view(), name='listofrequestformentor'), 
    path('requestformentor/<int:request_id>/change-status/', ChangeStatusRequestForMentor.as_view(), name='changestatusrequestformentor'),    
]