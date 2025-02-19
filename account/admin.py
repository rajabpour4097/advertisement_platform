from django.contrib.admin import register
from django.contrib import admin

from account.models import CampaignTransaction, EditingCampaign



@register(EditingCampaign)
class EditingCampaignAdmin(admin.ModelAdmin):
    
    list_display = [
                    'campaign',
                    'created_time', 
                    'modified_time', 
                    'edit_reason',
                    'submitted_user'
                    ]
    search_fields = ['campaign']


@register(CampaignTransaction)
class CampaignTransactionAdmin(admin.ModelAdmin):
    list_display = ['dealer', 'campaign', 'proposals', 'proposal_price']
    search_fields = ['dealer', 'campaign']    