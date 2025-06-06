from melipayamak import Api
from django.conf import settings
import random
from django.core.cache import cache
from django.db.models import Q
from account.models import CustomUser

def generate_otp():
    """
    تولید کد تصادفی 6 رقمی
    """
    return str(random.randint(100000, 999999))

def store_otp(user_phone, otp, expire_time=120):
    """
    ذخیره کد OTP در کش با زمان انقضای مشخص
    """
    cache_key = f"otp_{user_phone}"
    cache.set(cache_key, otp, expire_time)  # ذخیره به مدت 2 دقیقه

def verify_otp(user_phone, otp):
    """
    بررسی صحت کد OTP
    """
    cache_key = f"otp_{user_phone}"
    stored_otp = cache.get(cache_key)
    if stored_otp and stored_otp == otp:
        cache.delete(cache_key)  # حذف کد پس از استفاده
        return True
    return False

def send_activation_sms(user):
    """
    ارسال پیامک حاوی کد فعال‌سازی به کاربر
    """
    try:
        # تولید کد OTP
        otp = generate_otp()
        
        # ذخیره کد در کش
        store_otp(user.phone_number, otp)

        # متن پیامک
        sms_message = f"""
        کد تایید شما: {otp}
        این کد تا ۲ دقیقه معتبر است.
        لغو11
        """

        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD
        api = Api(username, password)
        sms = api.sms()
        
        # ارسال پیامک
        response = sms.send(
            to=user.phone_number,
            _from=settings.MELIPAYAMAK_NUMBER,
            text=sms_message
        )
        
        return response, otp, None  # برگرداندن پاسخ، کد OTP و None به عنوان خطا
        
    except Exception as e:
        return None, None, str(e)  # برگرداندن None و پیغام خطا

def send_campaign_confirmation_sms(campaign, needs_mentor):
    """
    ارسال پیامک اطلاع‌رسانی وضعیت کمپین به کاربر و مدیران
    """
    try:
        print("Starting SMS service...")
        
        # چک کردن تنظیمات
        print(f"Settings check - Username: {settings.MELIPAYAMAK_USERNAME}, Number: {settings.MELIPAYAMAK_NUMBER}")
        
        # چک کردن شماره موبایل کاربر
        print(f"Customer phone number: {campaign.customer.phone_number if campaign.customer else 'No customer'}")
        
        # چک کردن تعداد مدیران
        staff_am_users = CustomUser.objects.filter(Q(is_staff=True) | Q(is_am=True))
        print(f"Number of staff/am users: {staff_am_users.count()}")
        print(f"Staff/am users with phone numbers: {staff_am_users.filter(phone_number__isnull=False).count()}")
        
        # متن پیامک
        sms_message = f"""
           کمپین شما با موضوع {campaign.topic.first().name if campaign.topic else 'نامشخص'} ثبت شد و در دست بررسی است.
        لغو11
        """

        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD
        api = Api(username, password)
        sms = api.sms()
        
        # ارسال پیامک
        response = sms.send(
            to=campaign.customer.phone_number,
            _from=settings.MELIPAYAMAK_NUMBER,
            text=sms_message
        )
        
        # پیام برای مدیران
        staff_am_message = f"""
        کمپین جدید:
        موضوع: {campaign.topic.first().name if campaign.topic else 'نامشخص'}
        کاربر: {campaign.customer.get_full_name()}
        لغو11
        """
        
        # ارسال پیامک به مدیران (staff و am)
        for staff_am_user in staff_am_users:
            if staff_am_user.phone_number:
                sms.send(
                    to=staff_am_user.phone_number,
                    _from=settings.MELIPAYAMAK_NUMBER,
                    text=staff_am_message
                )
                
        return True, None
        
    except Exception as e:
        print(f"Error in sending SMS: {str(e)}")
        return False, str(e)

def send_campaign_review_sms(campaign, editing_campaign):
    """
    ارسال پیامک اطلاع‌رسانی بررسی کمپین به کاربر
    """
    try:
        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD
        api = Api(username, password)
        sms = api.sms()
        
        # پیام برای کاربر
        user_message = f"""
        کمپین شما با موضوع {campaign.topic.first().name if campaign.topic else 'نامشخص'} توسط مدیر بررسی شد.
        لطفا وارد پنل کاربری خود شوید و اصلاحات را انجام دهید.
        لغو11
        """
        
        # ارسال پیامک به کاربر
        if campaign.customer and campaign.customer.phone_number:
            response = sms.send(
                to=campaign.customer.phone_number,
                _from=settings.MELIPAYAMAK_NUMBER,
                text=user_message
            )
            
        return True, None
        
    except Exception as e:
        print(f"Error in sending review SMS: {str(e)}")
        return False, str(e)

def send_campaign_start_sms(campaign):
    """
    ارسال پیامک اطلاع‌رسانی شروع کمپین به کاربر و دیلرها
    """
    try:
        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD
        api = Api(username, password)
        sms = api.sms()
        
        # پیام برای کاربر
        user_message = f"""
        کمپین شما با موضوع {campaign.topic.first().name if campaign.topic else 'نامشخص'} شروع شده است.
        لغو11
        """
        
        # پیام برای دیلرها
        dealer_message = f"""
        کمپین جدید در حال برگزاری:
        موضوع: {campaign.topic.first().name if campaign.topic else 'نامشخص'}
        برای مشارکت وارد پنل کاربری خود شوید.
        لغو11
        """
        
        # ارسال پیامک به کاربر
        if campaign.customer and campaign.customer.phone_number:
            sms.send(
                to=campaign.customer.phone_number,
                _from=settings.MELIPAYAMAK_NUMBER,
                text=user_message
            )
            
        # ارسال پیامک به دیلرها
        dealers = CustomUser.objects.filter(user_type='dealer')
        for dealer in dealers:
            if dealer.phone_number:
                sms.send(
                    to=dealer.phone_number,
                    _from=settings.MELIPAYAMAK_NUMBER,
                    text=dealer_message
                )
                
        return True, None
        
    except Exception as e:
        print(f"Error in sending start campaign SMS: {str(e)}")
        return False, str(e)

def send_campaign_mentor_assignment_sms(campaign):
    """
    ارسال پیامک اطلاع‌رسانی تخصیص مشاور به کاربر
    """
    try:
        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD
        api = Api(username, password)
        sms = api.sms()
        
        # پیام برای کاربر
        user_message = f"""
        کاربر گرامی،
        مشاور {campaign.assigned_mentor.get_full_name()} برای کمپین شما با موضوع {campaign.topic.first().name if campaign.topic else 'نامشخص'} تعیین شد.
        لغو11
        """
        
        # ارسال پیامک به کاربر
        if campaign.customer and campaign.customer.phone_number:
            sms.send(
                to=campaign.customer.phone_number,
                _from=settings.MELIPAYAMAK_NUMBER,
                text=user_message
            )
                
        return True, None
        
    except Exception as e:
        print(f"Error in sending mentor assignment SMS: {str(e)}")
        return False, str(e) 