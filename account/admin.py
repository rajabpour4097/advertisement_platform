from django.contrib.admin import register
from django.contrib import admin

from account.models import CampaignTransaction, ContentCategory, EditingCampaign, RequestForMentor
from .models import (
    EnvironmentalAdvertisement, 
    EnvironmentalAdImage, 
    EventMarketingAdvertisement, 
    Platform, 
    PrintingAdvertisement, 
    SocialmediaAdvertisement, 
    DigitalAdvertisement
)




@register(EditingCampaign)
class EditingCampaignAdmin(admin.ModelAdmin):
    
    list_display = [
                    'campaign',
                    'created_at', 
                    'modified_at', 
                    'edit_reason',
                    'submitted_user'
                    ]
    search_fields = ['campaign']


@register(CampaignTransaction)
class CampaignTransactionAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'campaign', 'proposals', 'proposal_price']
    search_fields = ['dealer', 'campaign']    
    

@register(RequestForMentor)
class RequestForMentorAdmin(admin.ModelAdmin):
    list_display = ['requested_user', 'mentor', 'status', 'created_at', 'modified_at']
    search_fields = ['requested_user', 'mentor']
    

@register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'modified_at']
    search_fields = ['name']


class EnvironmentalAdImageInline(admin.TabularInline):
    model = EnvironmentalAdImage
    extra = 1
    fields = ('image',)
    ordering = ('id',)

@register(EnvironmentalAdvertisement)
class EnvironmentalAdvertisementAdmin(admin.ModelAdmin):
    inlines = [EnvironmentalAdImageInline]
    list_display = ('id', 'campaign', 'proposed_user', 'media_type', 'available_date')

@register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'modified_at']
    search_fields = ['name']

@register(SocialmediaAdvertisement)
class SocialmediaAdvertisementAdmin(admin.ModelAdmin):
    list_display = ['id', 'campaign', 'proposed_user', 'proposed_ad_template', 'start_execution_time', 'end_execution_time']
    search_fields = ['campaign', 'proposed_user']

@register(DigitalAdvertisement)
class DigitalAdvertisementAdmin(admin.ModelAdmin):
    list_display = ['id', 'campaign', 'proposed_user', 'digital_ad_type']
    search_fields = ['campaign', 'proposed_user']

@register(PrintingAdvertisement)
class PrintingAdvertisementAdmin(admin.ModelAdmin):
    list_display = ['id', 'campaign', 'proposed_user', 'printing_ad_type', 'delivery_time']
    search_fields = ['campaign', 'proposed_user']

@register(EventMarketingAdvertisement)
class EventMarketingAdvertisementAdmin(admin.ModelAdmin):
    list_display = ['id', 'campaign', 'proposed_user', 'event_proposed_date']
    search_fields = ['campaign', 'proposed_user']
