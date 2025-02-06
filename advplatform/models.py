from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager

'''
    TODO:
        3-start time and end time and deadline of 
            campaigns will be set
        
        
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

# مدل کاربر سفارشی
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True, default="1")
    address = models.TextField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    field_of_activity = models.ForeignKey('ActivityCategory', on_delete=models.PROTECT, null=True, blank=True)
    user_type = models.CharField(max_length=50, blank=True, null=True)  # customer, dealer, mentor
    cutomer_type = models.CharField(max_length=50, blank=True, null=True)  # Juridical, Private
    dealer_type = models.CharField(max_length=50, blank=True, null=True)  # Influencer, Private Designer, Corporate
    rank = models.SmallIntegerField(default=2, blank=True, null=True)
    bussines_value = models.BigIntegerField(null=True, blank=True)
    speciality_field = models.ForeignKey('SpecialityCategory', on_delete=models.PROTECT, null=True, blank=True)
    modified_time = models.DateTimeField(auto_now=True)
    customer_mentor = models.ForeignKey(
        'self',  # اشاره به خود مدل CustomUser
        on_delete=models.SET_NULL,  # اگر کاربر حذف شد، مقدار این فیلد null شود
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'mentor'},  # فقط کاربران با user_type='mentor' انتخاب شوند
        related_name='mentored_customers'  # نام رابطه برای دسترسی به مشتریانی که توسط این منتور منتور شده‌اند
    )

    # استفاده از CustomUserManager برای مدیریت کاربران
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # فیلد نام کاربری
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.email}'
    
class Campaign(models.Model):
    customer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'is_active': True, 'user_type': 'customer'},
        related_name='customers'
        )
    topic = models.ManyToManyField(Topic)
    describe = models.TextField()
    purposed_price = models.BigIntegerField(default=0)
    starttimedate = models.DateTimeField(null=True, blank=True)
    endtimedate = models.DateTimeField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    list_of_participants = models.ManyToManyField(
        CustomUser, blank=True,
        related_name='campaigns',
        limit_choices_to={'is_active': True, 'user_type': 'dealer'},
    )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    campaign_dealer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'is_active': True, 'user_type': 'dealer'},
        related_name='campaign_dealers',
        blank=True, null=True
      )
    is_active = models.BooleanField(default=True)
    class Meta:
        verbose_name = 'کمپین'
        verbose_name_plural = 'کمپین ها'
    
    def get_countdown_datetime(self):
        return self.endtimedate.strftime('%Y-%m-%dT%H:%M:%S')
    
    def __str__(self):
        return (f'{self.id} {self.customer}')
    
    

class Portfolio(models.Model):
    dealer = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'is_active': True, 'user_type': 'dealer'},
        related_name='dealers'
        )
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT)
    description = models.TextField(null=True, blank=True)
    done_time = models.DateField()
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'نمونه کار'
        verbose_name_plural = 'نمونه کارها'
    
    def __str__(self):
        return (f'{self.id} {self.dealer}')
    

class UsersImages(models.Model):
    image = models.ImageField(upload_to='users/')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customuserimages')
    
    class Meta:
        verbose_name = 'عکس کاربر'
        verbose_name_plural = 'عکس های کاربر'
    
    def __str__(self):
        return str(self.customer)


class CampaignImages(models.Model):
    image = models.ImageField(upload_to='campaigns/')
    campaigns = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='campaignsimages')
    
    class Meta:
        verbose_name = 'عکس کمپین'
        verbose_name_plural = 'عکس های کمپین'
    
    def __str__(self):
        return str(self.campaigns)


class PortfolioImages(models.Model):
    image = models.ImageField(upload_to='portfolios/')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolioimages')
    
    class Meta:
        verbose_name = 'عکس نمونه کار'
        verbose_name_plural = 'عکس های نمونه کارها'
    
    def __str__(self):
        return str(self.portfolio)