from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView

from advplatform.models import Campaign, CustomUser, Topic


'''
TODO:
    1- is_active check for users
    2- is_active check for campaigns
    3- is_active check for portfolios

'''


class AccountView(LoginRequiredMixin, TemplateView):
    
    template_name = 'account/index.html'
    
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
        
        mentor_customer_count = CustomUser.objects.filter(customer_mentor=self.request.user)
        context['mentor_customer_count'] = mentor_customer_count.count()
        
        return context
    

