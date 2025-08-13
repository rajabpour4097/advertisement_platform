from datetime import time
from django.db import models

from advplatform.choices_type import DIGITAL_AD_TYPE_CHOICES, ENVIRONMENTAL_AD_TYPE_CHOICES, EVENT_TYPE_CHOICES, PRINTING_AD_TYPE_CHOICES, REQUEST_TYPE, SOCIAL_MEDIA_AD_TYPE_CHOICES, TARGETING_TYPE_CHOICES
from advplatform.models import Campaign, City, CustomUser



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


class ContentCategory(BaseModel):
    name = models.CharField(max_length=100, verbose_name='نام دسته بندی')
    description = models.TextField(verbose_name='توضیحات', blank=True, null=True)

    class Meta:
        verbose_name = 'دسته بندی محتوا'
        verbose_name_plural = 'دسته بندی های محتوا'
        ordering = ['name']

    def __str__(self):
        return self.name


class Platform(BaseModel):
    name = models.CharField(max_length=100, verbose_name='نام پلتفرم')
    description = models.TextField(verbose_name='توضیحات', blank=True, null=True)

    class Meta:
        verbose_name = 'پلتفرم'
        verbose_name_plural = 'پلتفرم ها'
        ordering = ['name']

    def __str__(self):
        return self.name


class EnvironmentalAdvertisement(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='environmental_ads', verbose_name='کمپین')
    proposed_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposed_ads_%(class)s', verbose_name='کاربر پیشنهاد دهنده')
    location_title = models.CharField(max_length=255, verbose_name='عنوان موقعیت تبلیغاتی')
    service_area = models.ManyToManyField(
                                    City,
                                    verbose_name='شهر مورد نظر',
                                    related_name='cities',
                                    )
    media_type = models.CharField(max_length=50, choices=ENVIRONMENTAL_AD_TYPE_CHOICES, default='billboard', verbose_name='نوع رسانه')
    media_width = models.PositiveIntegerField(verbose_name='عرض رسانه')
    media_height = models.PositiveIntegerField(verbose_name='ارتفاع رسانه')
    # حذف فیلد image و اضافه کردن رابطه با مدل جدید ImageInline
    available_date = models.DateField(verbose_name='تاریخ شروع قابل رزرو')
    expiration_date = models.IntegerField(verbose_name='مدت زمان اکران (روز)')
    proposal_price = models.BigIntegerField(verbose_name='قیمت پیشنهادی')
    description = models.TextField(verbose_name='توضیحات', blank=True, null=True)
    media_location_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    media_location_longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        verbose_name = 'تبلیغ محیطی'
        verbose_name_plural = 'تبلیغات محیطی'
        ordering = ['-created_at']

    def __str__(self):
        return self.campaign.topic.first.name
    

class SocialmediaAdvertisement(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='socialmedia_ads', verbose_name='کمپین')
    proposed_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposed_ads_%(class)s', verbose_name='کاربر پیشنهاد دهنده')
    content_categories = models.ManyToManyField(ContentCategory, verbose_name='دسته بندی محتوا')    
    proposed_ad_template = models.CharField(
                                                max_length=50, 
                                                choices=SOCIAL_MEDIA_AD_TYPE_CHOICES, 
                                                default='post', 
                                                verbose_name='نوع رسانه'
                                            )
    start_execution_time = models.DateTimeField(verbose_name='زمان شروع تبلیغ')
    end_execution_time = models.DateTimeField(verbose_name='زمان پایان تبلیغ')
    proposal_price = models.BigIntegerField(verbose_name='قیمت پیشنهادی')

    class Meta:
        verbose_name = 'تبلیغ رسانه اجتماعی'
        verbose_name_plural = 'تبلیغات رسانه اجتماعی'
        ordering = ['-created_at']

    def __str__(self):
        return self.campaign.topic.first.name

    # def check_correct_data(self):
    #     return self.start_execution_time > time.now() and self.end_execution_time > self.start_execution_time

class DigitalAdvertisement(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='digital_ads', verbose_name='کمپین')
    proposed_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposed_ads_%(class)s', verbose_name='کاربر پیشنهاد دهنده')
    digital_ad_type = models.CharField(max_length=50, choices=DIGITAL_AD_TYPE_CHOICES, default='banner', verbose_name='نوع رسانه')
    proposed_platform = models.ManyToManyField(Platform, verbose_name='پلتفرم هدف')
    targeting_type = models.CharField(max_length=50, choices=TARGETING_TYPE_CHOICES, default='geographic', verbose_name='نوع هدف‌گذاری')
    estimated_clicks = models.PositiveIntegerField(verbose_name='تخمین کلیک/نمایش')
    duration = models.PositiveIntegerField(verbose_name='مدت زمان اجرا (روز)')
    advertising_budget = models.BigIntegerField(verbose_name='بودجه تبلیغ')
    proposal_price = models.BigIntegerField(verbose_name='قیمت پیشنهادی')
    class Meta:
        verbose_name = 'تبلیغ دیجیتال'
        verbose_name_plural = 'تبلیغات دیجیتال'
        ordering = ['-created_at']
    def __str__(self):
        return self.campaign.topic.first.name
    

class PrintingAdvertisement(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='printing_ads', verbose_name='کمپین')
    proposed_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposed_ads_%(class)s', verbose_name='کاربر پیشنهاد دهنده')
    printing_ad_type = models.CharField(max_length=50, choices=PRINTING_AD_TYPE_CHOICES, default='flyer', verbose_name='نوع اقلام چاپی')
    paper_weight_and_type = models.CharField(max_length=100, verbose_name='گرماژ و جنس کاغذ')
    dimensions = models.CharField(max_length=100, verbose_name='ابعاد (مثلا A5 یا اختصاصی)')
    circulation = models.PositiveIntegerField(verbose_name='تیراژ')
    delivery_time = models.PositiveIntegerField(verbose_name='زمان تحویل (عدد بر حسب روز کاری)')
    total_proposal_price = models.BigIntegerField(verbose_name='قیمت کل پیشنهادی (طراحی + چاپ)')
    graphic_design_included = models.BooleanField(default=False, verbose_name='طراحی گرافیکی همراه دارد؟')

    class Meta:
        verbose_name = 'تبلیغ چاپی'
        verbose_name_plural = 'تبلیغات چاپی'
        ordering = ['-created_at']

    def __str__(self):
        return self.campaign.topic.first.name
    

class EventMarketingAdvertisement(BaseModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='event_marketing_ads', verbose_name='کمپین')
    proposed_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposed_ads_%(class)s', verbose_name='کاربر پیشنهاد دهنده')
    event_type = models.CharField(max_length=100, choices=EVENT_TYPE_CHOICES, verbose_name='نوع رویداد پیشنهادی')
    location = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='شهر محل برگزاری')
    location_address = models.CharField(max_length=255, verbose_name='آدرس محل برگزاری')
    event_proposed_date = models.DateTimeField(verbose_name='تاریخ پیشنهادی رویداد')
    event_content = models.TextField(verbose_name='محتوا یا سناریوی کلی رویداد')
    total_proposal_price = models.BigIntegerField(verbose_name='قیمت پیشنهادی کل (همه هزینه‌ها را شامل شود)')

    class Meta:
        verbose_name = 'ایونت مارکتینگ'
        verbose_name_plural = 'ایونت مارکتینگ ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.campaign.topic.first.name


# class HybridAdvertisement(BaseModel):
#     campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='hybrid_ads', verbose_name='کمپین')
#     proposed_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='proposed_ads', verbose_name='کاربر پیشنهاد دهنده')
        

#     class Meta:
#         verbose_name = 'تبلیغ ترکیبی'
#         verbose_name_plural = 'تبلیغات ترکیبی'
#         ordering = ['-created_at']

#     def __str__(self):
#         return self.campaign.topic.first.name


class EnvironmentalAdImage(BaseModel):
    advertisement = models.ForeignKey(
        EnvironmentalAdvertisement,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='تبلیغ محیطی'
    )
    image = models.ImageField(upload_to='environmental_ads/%Y/%m/%d', verbose_name='تصویر')
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name='توضیح')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')

    class Meta:
        verbose_name = 'تصویر تبلیغ محیطی'
        verbose_name_plural = 'تصاویر تبلیغ محیطی'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.advertisement_id} - {self.caption or self.image.name}'