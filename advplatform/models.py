from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.urls import reverse
import jdatetime
from advplatform.choices_type import CAMPAIGN_TYPE, CUSTOMER_TYPE, DEALER_TYPE, RESUME_STATUS_CHOICES, USER_TYPE

'''
    TODO:
        1-       
        
''' 

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


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
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, 
        related_name='children', null=True, blank=True
        )
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    min_price = models.BigIntegerField(null=True, blank=True, verbose_name='حداقل قیمت')
    icon = models.ImageField(upload_to='topics/', null=True, blank=True, verbose_name='آیکون')
    description = models.TextField(null=True, blank=True, verbose_name='توضیحات')
    short_describe = models.CharField(max_length=200, null=True, blank=True, verbose_name='توضیحات کوتاه')
    color = models.CharField(max_length=7, default="#cccccc")  # مثل #28a745
    
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
    speciality_field = models.ManyToManyField(
                                         Topic, 
                                         null=True, 
                                         blank=True, 
                                         related_name='speciality_field',
                                         verbose_name='تخصص'
                                         ) # for Dealer
    company_name = models.CharField(max_length=150, blank=True, null=True, verbose_name='نام شرکت')
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
    
    def get_full_name(self):
        if self.company_name:
            return f"شرکت {self.company_name}".strip()
        return f"{self.first_name} {self.last_name}".strip()
       
    
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
                              default='unpaid'
                              )
    
    campaign_dealer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'is_active': True, 'user_type': 'dealer'},
        related_name='campaign_dealers',
        blank=True, null=True,
        verbose_name='مجری کمپین'
      )
    
    is_active = models.BooleanField(default=False, verbose_name='وضعیت کمپین')
    needs_mentor = models.BooleanField(null=True, blank=True, verbose_name='نیاز به مشاور')
    assigned_mentor = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        limit_choices_to={'user_type': 'mentor', 'is_active': True},
        related_name='assigned_campaigns',
        verbose_name='مشاور اختصاص داده شده'
        )
    finished_review = models.BooleanField(default=False, verbose_name='وضعیت تعیین برنده') #Check finished after 96 hours campaign
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
    
    def get_campaign_price(self):
        return (self.purposed_price*10)/100
    
    def get_finished_proposals(self):
        return self.endtimedate >= timezone.now() - timedelta(hours=96)
    

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
    

class Province(BaseModel):
    name = models.CharField(max_length=100, verbose_name='نام استان')
    
    class Meta:
        verbose_name = 'استان'
        verbose_name_plural = 'استان‌ها'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(max_length=100, verbose_name='نام شهر')
    province = models.ForeignKey(
        Province, 
        on_delete=models.CASCADE, 
        related_name='cities',
        verbose_name='استان'
    )
    
    class Meta:
        verbose_name = 'شهر'
        verbose_name_plural = 'شهرها'
        ordering = ['name']
        unique_together = ['name', 'province']  # جلوگیری از تکرار نام شهر در یک استان
    
    def __str__(self):
        return f"{self.name} - {self.province.name}"


class Resume(models.Model):
    user = models.OneToOneField(  # تغییر از ForeignKey به OneToOneField
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'is_active': True, 'user_type': 'dealer'},
        related_name='resume',  # تغییر نام related_name
        verbose_name='کاربر صاحب رزومه'
    )
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name='عنوان رزومه')

    #### consider by document ####
    dealer_type = models.ForeignKey(Topic, verbose_name='نوع مجری تبلیغات', 
                                    related_name='dealer_type', 
                                    on_delete=models.PROTECT,
                                    )
    service_area = models.ManyToManyField(
                                    City,
                                    verbose_name='حوزه خدمات (شهرها)',
                                    related_name='resumes',
                                    help_text='شهرهایی که در آن‌ها خدمات ارائه می‌دهید'
                                    )
    describe = models.TextField(verbose_name='توضیحات')
    specialty_categories = models.ForeignKey(Topic, 
                                                  verbose_name='دسته‌های تخصصی', 
                                                  related_name='specialty_categories',
                                                  on_delete=models.PROTECT,
                                                  blank=True, null=True
                                                  ) #four subcategories
    services = models.TextField(verbose_name='خدمات قابل ارائه')
    socialmedia_and_sites = models.TextField(blank=True, null=True, verbose_name='شبکه‌های اجتماعی و وب‌سایت‌ها')
    tools_and_platforms = models.TextField(blank=True, null=True, verbose_name='ابزارها و پلتفرم‌ها')
    file = models.FileField(upload_to='resumes/files/', blank=True, null=True, verbose_name='فایل رزومه')
    #worklinks inline
    portfolios = models.ManyToManyField(Portfolio, blank=True, verbose_name='پورتفولیوها')
    partner_brand = models.TextField(blank=True, null=True, verbose_name='برند همکار')
    #permissions inline
    bank_account = models.CharField(max_length=25, blank=True, null=True, verbose_name='شماره حساب بانکی')
    #### end consider by document ####
    
    status = models.CharField(max_length=20, choices=RESUME_STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    manager_comment = models.TextField(blank=True, null=True, verbose_name='نظر مدیر')
    is_seen_by_manager = models.BooleanField(default=False, verbose_name='مشاهده شده توسط مدیر')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'رزومه'
        verbose_name_plural = 'رزومه ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} - {self.status}"
    
    def get_permissions_count(self):
        """تعداد مجوزهای آپلود شده"""
        return self.permission_files.count()
    
    def get_work_links_count(self):
        """تعداد لینک‌های نمونه کار"""
        return self.work_links.count()
    
    def get_featured_work_links(self):
        """لینک‌های نمونه کار برجسته"""
        return self.work_links.filter(is_featured=True)
    
    def get_recent_work_links(self, limit=5):
        """آخرین لینک‌های نمونه کار"""
        return self.work_links.order_by('-created_at')[:limit]
    
    def get_available_specialty_categories(self):
        """دریافت فرزندان Topic انتخاب شده در dealer_type"""
        if self.dealer_type:
            return Topic.objects.filter(parent=self.dealer_type)
        return Topic.objects.none()
    
    def get_service_provinces(self):
        """استان‌هایی که کاربر در آن‌ها خدمات ارائه می‌دهد"""
        return Province.objects.filter(cities__in=self.service_area.all()).distinct()
    
    def get_service_cities_by_province(self):
        """شهرها را بر اساس استان گروه‌بندی می‌کند"""
        cities_by_province = {}
        for city in self.service_area.all():
            province_name = city.province.name
            if province_name not in cities_by_province:
                cities_by_province[province_name] = []
            cities_by_province[province_name].append(city.name)
        return cities_by_province


class Permission(BaseModel):
    """مدل برای ذخیره مجوزهای کاربران"""
    resume = models.ForeignKey(
        Resume, 
        on_delete=models.CASCADE, 
        related_name='permission_files',
        verbose_name='رزومه'
    )
    title = models.CharField(
        max_length=100, 
        verbose_name='عنوان مجوز',
        help_text='مثل: مجوز کسب، گواهینامه، پروانه فعالیت'
    )
    file = models.FileField(
        upload_to='resumes/permissions/', 
        verbose_name='فایل مجوز',
        help_text='فرمت‌های مجاز: PDF, JPG, PNG'
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='توضیحات',
        help_text='توضیحات اضافی در مورد این مجوز'
    )
    issue_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='تاریخ صدور'
    )
    expiry_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='تاریخ انقضا'
    )
    issuing_authority = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        verbose_name='مرجع صادرکننده'
    )

    class Meta:
        verbose_name = 'مجوز'
        verbose_name_plural = 'مجوزها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.resume.user.get_full_name()}"
    
    def is_expired(self):
        """بررسی انقضای مجوز"""
        if self.expiry_date:
            from django.utils import timezone
            return self.expiry_date < timezone.now().date()
        return False


class WorkLink(BaseModel):
    """مدل برای ذخیره لینک‌های نمونه کارهای کاربران"""
    resume = models.ForeignKey(
        Resume, 
        on_delete=models.CASCADE, 
        related_name='work_links',
        verbose_name='رزومه'
    )
    title = models.CharField(
        max_length=100, 
        verbose_name='عنوان نمونه کار',
        help_text='عنوان یا توضیح کوتاه نمونه کار'
    )
    url = models.URLField(
        verbose_name='آدرس لینک',
        help_text='آدرس کامل نمونه کار (مثل: https://example.com)'
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name='توضیحات',
        help_text='توضیحات اضافی در مورد این نمونه کار'
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='دسته‌بندی',
        help_text='نوع نمونه کار (مثل: وب‌سایت، اپلیکیشن، طراحی گرافیک)'
    )
    completion_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='تاریخ تکمیل'
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='نمونه کار برجسته',
        help_text='آیا این نمونه کار به عنوان کار برجسته نمایش داده شود؟'
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='ترتیب نمایش',
        help_text='ترتیب نمایش این لینک (عدد کمتر اولویت بالاتر)'
    )

    class Meta:
        verbose_name = 'لینک نمونه کار'
        verbose_name_plural = 'لینک‌های نمونه کارها'
        ordering = ['order', '-is_featured', '-created_at']
        unique_together = ['resume', 'url']  # جلوگیری از تکرار URL در یک رزومه

    def __str__(self):
        return f"{self.title} - {self.resume.user.get_full_name()}"
    
    def get_domain(self):
        """استخراج دامنه از URL"""
        from urllib.parse import urlparse
        try:
            domain = urlparse(self.url).netloc
            return domain.replace('www.', '')
        except:
            return None
    
    def is_valid_url(self):
        """بررسی معتبر بودن URL"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// یا https://
            r'(?:(?:[A-Z0-9](?:[A ز0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # پورت اختیاری
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(self.url) is not None