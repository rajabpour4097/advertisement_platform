from django.db import models

from advplatform.choices_type import REQUEST_TYPE
from advplatform.models import Campaign, CustomUser



class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CampaignTransaction(BaseModel):
    
    dealer = models.ForeignKey(
                                CustomUser, 
                                on_delete=models.CASCADE,
                                limit_choices_to={'is_active': True, 'user_type': 'dealer'},
                                related_name='campaign_participate',
                                verbose_name='شرکت کننده'
                                )
    campaign = models.ForeignKey(
                                 Campaign,
                                 on_delete=models.CASCADE,
                                 related_name='running_campaign',
                                 verbose_name='کمپین'
                                 )
    proposals = models.TextField(verbose_name='پیشنهادات شما')
    proposal_price = models.BigIntegerField(verbose_name='قیمت پیشنهادی')
    
    class Meta:
        verbose_name = 'تراکنش های کمپین'
        verbose_name_plural = 'تراکنش های کمپین ها'
        unique_together = ('dealer', 'campaign') # each dealer can give a proposal in each campaign

    def __str__(self):
        return (f'{self.dealer} {self.campaign.describe}')
    
    
class EditingCampaign(BaseModel):
        
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='editings',
        verbose_name='کمپین'
    )
    edit_reason = models.TextField(verbose_name='موارد ویرایش')
    submitted_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name='کاربر ویرایش کننده'
    )

    class Meta:
        verbose_name = 'ویرایش های کمپین'
        verbose_name_plural = 'ویرایش های کمپین ها'
        ordering = ['-created_at'] 


    def __str__(self):
        return (f'{self.submitted_user} {self.campaign.describe}')


class RequestForMentor(BaseModel):
    
    requested_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='requested_user')
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='requested_mentor')
    status = models.CharField(
                              choices=REQUEST_TYPE, 
                              max_length=30, 
                              verbose_name='وضعیت درخواست', 
                              default='pending'
                              )
    
    class Meta:
        verbose_name = 'درخواست مشاور'
        verbose_name_plural = 'درخواست های مشاور'
        ordering = ['-created_at']
    
    def get_status_display(self):
        return dict(REQUEST_TYPE).get(self.status, self.status)