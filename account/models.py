from django.db import models

from advplatform.models import Campaign, CustomUser



class CampaignTransaction(models.Model):
    
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
    
    
class EditingCampaign(models.Model):
        
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='editings',
        verbose_name='کمپین'
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    edit_reason = models.TextField(verbose_name='موارد ویرایش')
    submitted_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name='کاربر ویرایش کننده'
    )

    class Meta:
        verbose_name = 'ویرایش های کمپین'
        verbose_name_plural = 'ویرایش های کمپین ها'
        ordering = ['-created_time'] 


    def __str__(self):
        return (f'{self.submitted_user} {self.campaign.describe}')