from melipayamak import Api
from django.conf import settings
import random
from django.core.cache import cache

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