from django.contrib.admin import register
from django.contrib import admin

from account.models import CampaignTransaction, EditingCampaign, RequestForMentor



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