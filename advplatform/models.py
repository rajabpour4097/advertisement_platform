from django.utils import timezone
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.urls import reverse
import jdatetime
from advplatform.choices_type import CAMPAIGN_TYPE, CUSTOMER_TYPE, DEALER_TYPE, USER_TYPE

'''
    TODO:
        1-       
        
''' 



class ActivityCategory(models.Model):
    name = models.CharField(max_length=60)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        related_name='children', null=True, blank=True
        )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'زمینه فعالیت'
        verbose_name_plural = 'زمینه های فعالیت'
    
    def __str__(self):
        return self.name


class SpecialityCategory(models.Model):
    name = models.CharField(max_length=60)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        related_name='children', null=True, blank=True
        )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'دسته بندی تخصص'
        verbose_name_plural = 'دسته بندی های تخصص'
    
    def __str__(self):
        return self.name
    

class Topic(models.Model):
    name = models.CharField(max_length=60)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        related_name='children', null=True, blank=True
        )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'موضوع'
        verbose_name_plural = 'موضوعات'
    
    def __str__(self):
        return self.name
        

# مدیر کاربر سفارشی برای ایجاد و مدیریت کاربران
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if password:
            user.set_password(password)  # هش کردن پسورد
            print(f"Password set for {email}: {user.password}")  # پرینت پسورد هش شده برای بررسی

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, unique=True, verbose_name='شماره تماس')
    address = models.TextField(null=True, blank=True, verbose_name='آدرس')
    birth_date = models.DateField(null=True, blank=True, verbose_name='تاریخ تولد')
    field_of_activity = models.ForeignKey(
                                          'ActivityCategory', 
                                          on_delete=models.PROTECT, 
                                          null=True, blank=True, 
                                          verbose_name='زمینه فعالیت'
                                          ) # for Customer
    user_type = models.CharField(
                                 choices=USER_TYPE, 
                                 max_length=30, 
                                 blank=True, 
                                 null=True, 
                                 verbose_name='نوع کاربر',
                                 default=''
                                )  # customer, dealer, mentor
    cutomer_type = models.CharField(
                                    choices=CUSTOMER_TYPE, 
                                    max_length=30, 
                                    blank=True, 
                                    null=True, 
                                    verbose_name='نوع مشتری', 
                                    default=''
                                    )  # Juridical, Private
    dealer_type = models.CharField(
                                   choices=DEALER_TYPE, 
                                   max_length=30, 
                                   blank=True, 
                                   null=True, 
                                   verbose_name='نوع عامل تبلیغ', 
                                   default=''
                                   )  # Influencer, Private Designer, Corporate
    rank = models.SmallIntegerField(default=2, blank=True, null=True, verbose_name='رتبه')# for Dealer and Mentor
    bussines_value = models.BigIntegerField(null=True, blank=True, verbose_name='ارزش کسب و کار')# for Customer
    speciality_field = models.ForeignKey(
                                         'SpecialityCategory', 
                                         on_delete=models.PROTECT, 
                                         null=True, blank=True, 
                                         verbose_name='تخصص'
                                         ) # for Dealer
    modified_time = models.DateTimeField(auto_now=True, verbose_name='آخرین تغییر پروفایل')
    is_am = models.BooleanField(default=False, verbose_name='مدیر تبلیغات')

    # استفاده از CustomUserManager برای مدیریت کاربران
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # فیلد نام کاربری
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.email}'
    
    def count_null_fields(self):
        null_fields = 0
        # بررسی تمام فیلدهای مدل
        for field in self._meta.get_fields():
            if hasattr(self, field.name):  # اطمینان از وجود فیلد در آبجکت
                value = getattr(self, field.name)
                if value is None:  # اگر مقدار null باشد
                    null_fields += 1
        return null_fields
    
    def get_field_count(self):
        return len([field for field in self._meta.get_fields() if field.concrete])
       
    
class Campaign(models.Model):
    customer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'is_active': True, 'user_type': 'customer'},
        related_name='customers',
        verbose_name='کارفرما'
        )
    topic = models.ManyToManyField(Topic, verbose_name='موضوعات کمپین', related_name='topics')
    describe = models.TextField(verbose_name='شرح کمپین')
    purposed_price = models.BigIntegerField(verbose_name='قیمت پیشنهادی')
    starttimedate = models.DateTimeField(null=True, blank=True, verbose_name='زمان شروع')
    endtimedate = models.DateTimeField(null=True, blank=True, verbose_name='زمان اتمام')
    deadline = models.DateField(null=True, blank=True, verbose_name='تاریخ مهلت اجرا')
    list_of_participants = models.ManyToManyField(
        CustomUser, blank=True,
        related_name='campaigns',
        limit_choices_to={'is_active': True, 'user_type': 'dealer'},
        verbose_name='لیست شرکت کنندگان'
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    status = models.CharField(
                              choices=CAMPAIGN_TYPE, 
                              max_length=30, 
                              verbose_name='وضعیت اجرای کمپین', 
                              default='reviewing'
                              )
    
    campaign_dealer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'is_active': True, 'user_type': 'dealer'},
        related_name='campaign_dealers',
        blank=True, null=True,
        verbose_name='مجری کمپین'
      )
    
    is_active = models.BooleanField(default=False, verbose_name='وضعیت کمپین')
    needs_mentor = models.BooleanField(default=False, verbose_name='نیاز به مشاور')
    assigned_mentor = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        limit_choices_to={'user_type': 'mentor', 'is_active': True},
        related_name='assigned_campaigns',
        verbose_name='مشاور اختصاص داده شده'
        )
    class Meta:
        verbose_name = 'کمپین'
        verbose_name_plural = 'کمپین ها'
        ordering = ['-created_time']
    
    def get_countdown_datetime(self):
        return self.endtimedate.strftime('%Y-%m-%dT%H:%M:%S')
    
    def __str__(self):
        return (f'{self.describe} {self.customer}')
    
    def get_jalali_endtimedate(self):
        if self.endtimedate:
            return jdatetime.datetime.fromgregorian(datetime=self.endtimedate)
        return None
    
    def get_jalali_endtimedate_clean(self):
        jalali_date = self.get_jalali_endtimedate()
        if jalali_date:
            return f"{jalali_date.year}-{jalali_date.month}-{jalali_date.day} {jalali_date.hour}:{jalali_date.minute}:{jalali_date.second}"
        return None
    
    def get_participant_count(self):
        return self.list_of_participants.count()
    
    def get_gift_price(self):
        return (self.purposed_price * 5) / 100
    
    def get_ended_campaign(self):
        current_time = timezone.now()
        if self.endtimedate and self.endtimedate < current_time:
            return 'پایان یافته'
        return None
    
    def get_describe_summrize(self):
        words = self.describe.split()  # Split the text into words
        return " ".join(words[:10])
    

class Portfolio(models.Model):
    dealer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_active': True, 'user_type': 'dealer'},
        related_name='dealers', verbose_name='نام مجری'
        )
    subject = models.CharField(max_length=50, null=True, blank=True, verbose_name='عنوان نمونه کار')
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, verbose_name='موضوع')
    description = models.TextField(null=True, blank=True, verbose_name='شرح نمونه کار')
    done_time = models.DateField(verbose_name='زمان انجام')
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    execution_price = models.BigIntegerField(blank=True, null=True, verbose_name='هزینه اجرا')
    is_active = models.BooleanField(default=True, verbose_name='وضعیت')
    
    class Meta:
        verbose_name = 'نمونه کار'
        verbose_name_plural = 'نمونه کارها'
        ordering = ['-created_time']
    
    def __str__(self):
        return (f'{self.id} {self.dealer}')
    
    def get_absolute_url(self):
        return reverse("account:portfolios")
    
    def get_jalali_datetime(self):
        if self.done_time:
            self.jalali_done_time = jdatetime.date.fromgregorian(date=self.done_time)
        else:
            self.jalali_done_time = None
        return self.jalali_done_time
        

class UsersImages(models.Model):
    image = models.ImageField(upload_to='users/')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customuserimages')
    
    class Meta:
        verbose_name = 'عکس کاربر'
        verbose_name_plural = 'عکس های کاربر'
    
    def __str__(self):
        return str(self.customer)
    
    def save(self, *args, **kwargs):
        # حذف عکس قبلی کاربر (در صورت وجود)
        UsersImages.objects.filter(customer=self.customer).delete()
        super().save(*args, **kwargs)


class CampaignImages(models.Model):
    image = models.ImageField(upload_to='campaigns/', verbose_name='آپلود تصویر کمپین')
    campaigns = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='campaignsimages')
    
    class Meta:
        verbose_name = 'عکس کمپین'
        verbose_name_plural = 'عکس های کمپین'
    
    def __str__(self):
        return str(self.campaigns)


class PortfolioImages(models.Model):
    image = models.ImageField(upload_to='portfolios/', verbose_name='عکس های نمونه کار')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolioimages')
    
    class Meta:
        verbose_name = 'عکس نمونه کار'
        verbose_name_plural = 'عکس های نمونه کارها'
    
    def __str__(self):
        return str(self.portfolio)
     
