from django.shortcuts import get_object_or_404, redirect, render
from account.models import RequestForMentor
from advplatform.models import Campaign, CustomUser, Portfolio, Topic
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.admin.models import LogEntry




class NotLoginedMixin():
    """Verify that the current user is not authenticated."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account:profile')
        return super().dispatch(request, *args, **kwargs)


class FieldMixin():
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.fields = []
        elif request.user == 'dealer':
            self.fields = []
        else:
            return render(self.request, '403.html', 
                          {'error_message': "پیام شما"})
        
        return super().dispatch(request, *args, **kwargs)
    

class DealerUserMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.user_type == 'dealer' or self.request.user.is_am


class ContextsMixin():
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['user_count'] = CustomUser.objects.count()
        
        filtered_customer_user = CustomUser.objects.filter(user_type='customer')
        context['customer_count'] = filtered_customer_user.count()
        
        filtered_dealer_user = CustomUser.objects.filter(user_type='dealer')
        context['dealer_count'] = filtered_dealer_user.count()
        
        filtered_mentor_user = CustomUser.objects.filter(user_type='dealer')
        context['mentor_count'] = filtered_mentor_user.count()
        
        filtered_done_campaign = Campaign.objects.filter(status=True)
        context['done_campaign_count'] = filtered_done_campaign.count()
        
        filtered_site_manager = CustomUser.objects.filter(is_staff=True)
        context['sitemanager_count'] = filtered_site_manager.count()

        campaign_with_instagram = Campaign.objects.filter(topic__name__icontains='اینستاگرام').distinct()
        instagram_percent = 0 if filtered_done_campaign.count() == 0 else campaign_with_instagram.count() * 100 / filtered_done_campaign.count()
        context['instagram_campaign_percent'] = instagram_percent 
        
        campaign_with_google = Campaign.objects.filter(topic__name__icontains='گوگل').distinct()
        google_percent = 0 if filtered_done_campaign.count() == 0 else campaign_with_google.count() * 100 / filtered_done_campaign.count()
        context['google_campaign_percent'] = google_percent
        
        filtered_customer_campaigns = Campaign.objects.filter(customer=self.request.user)
        context['customer_campaigns_count'] = filtered_customer_campaigns.count()
        
        customer_success_campaigns_count = filtered_customer_campaigns.filter(status=True)
        context['customer_success_campaigns_count'] = customer_success_campaigns_count.count()
        
        now = timezone.now()
        ended_customer_campaigns_count = Campaign.objects.filter(endtimedate__lte=now, customer=self.request.user)
        context['ended_customer_campaigns_count'] = ended_customer_campaigns_count.count()
        
        dealer_success_campaigns = Campaign.objects.filter(status=True, campaign_dealer=self.request.user)
        context['dealer_success_campaigns'] = dealer_success_campaigns.count()
        
        dealer_campaigns_count = Campaign.objects.filter(list_of_participants__id=self.request.user.id)
        context['dealer_campaigns_count'] = dealer_campaigns_count.count()
      
        recent_actions = LogEntry.objects.all().order_by('-action_time')[:5]
        context['recent_actions'] = recent_actions
        
        return context


class PortfolioEditMixin():
    
    def dispatch(self, request, *args, **kwargs):
        url_pk = self.kwargs.get('pk')
        
        if not request.user.is_staff and not request.user.is_am:
            if not Portfolio.objects.filter(pk=url_pk, dealer=self.request.user).exists():
                return render(self.request, '403.html', 
                              {'error_message': "شما به این نمونه کار دسترسی ندارید",
                               'back_url': "account:portfolios"},
                              )
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_pk = self.kwargs.get('pk')
        if self.request.user.is_staff or self.request.user.is_am:
            portfolio = get_object_or_404(Portfolio, pk=url_pk)
        else:    
            portfolio = get_object_or_404(Portfolio, pk=url_pk, dealer=self.request.user)
            
        context['portfolio'] = portfolio
        context['topics'] = Topic.objects.all()
        return context
    

class PortfolioDeleteMixin():
    def dispatch(self, request, *args, **kwargs):
        url_pk = self.kwargs.get('pk')
        
        if not request.user.is_staff and not request.user.is_am:
            if not Portfolio.objects.filter(pk=url_pk, dealer=self.request.user).exists():
                return render(self.request, '403.html', 
                              {'error_message': "شما به این نمونه کار دسترسی ندارید",
                               'back_url': "account:portfolios"},
                              )
        
        return super().dispatch(request, *args, **kwargs)
    

class CampaignUserMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_staff or\
            self.request.user.user_type == 'dealer' or\
                self.request.user.user_type == 'customer' or\
                    self.request.user.is_am
                

class CreateCampaignUserMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.user_type == 'customer' or self.request.user.is_am


class StaffUserMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_staff


class AMUserMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_am


class ManagerUserMixin(UserPassesTestMixin):
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff and not request.user.is_am:
            return render(self.request, '403.html', 
                          {'error_message': "شما به این صفحه دسترسی ندارید",
                           'back_url': "account:campaigns"},
                          )
        return super().dispatch(request, *args, **kwargs)
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_am
    
  
class CancelUserMixin(UserPassesTestMixin):

    def test_func(self):
        campaign_id = self.kwargs.get('pk')
        campaign = Campaign.objects.filter(pk=campaign_id).first()

        return campaign and self.request.user == campaign.customer


class EditCampaignUserMixin(UserPassesTestMixin):
    
    def test_func(self):
        campaign_id = self.kwargs.get('pk')
        campaign = Campaign.objects.filter(pk=campaign_id).first()
        return self.request.user.is_staff or self.request.user.is_am or\
            self.request.user.user_type == 'customer' and self.request.user == campaign.customer


class MentorUserMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.user_type == 'mentor'


class CustomerUserMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.user_type == 'customer'


class CheckHaveRequestOrMentor():
    def dispatch(self, request, *args, **kwargs):
        if RequestForMentor.objects.filter(requested_user=request.user, status='pending').exists():
            return render(self.request, '403.html', 
                          {'error_message': "شما در حال حاضر یک درخواست در حال بررسی دارید.",
                           'back_url': "account:mymentor"},
                          )

        if request.user.customer_mentor:
            return render(self.request, '403.html', 
                          {'error_message': "شما در حال حاضر مشاور دارید.",
                           'back_url': "account:mymentor"},
                          )

        return super().dispatch(request, *args, **kwargs)
    

class AdvertisementsManagerMixin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.user_type == 'AM'
    
    
    