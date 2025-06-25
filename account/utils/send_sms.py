from melipayamak import Api
from django.conf import settings
import random
import requests
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
    try:
        otp = generate_otp()
        store_otp(user.phone_number, otp)

        url = "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber"
        payload = {
            "username": settings.MELIPAYAMAK_USERNAME,
            "password": settings.MELIPAYAMAK_PASSWORD,
            "text": otp,
            "to": user.phone_number,
            "bodyId": "337375"
        }

        response = requests.post(url, json=payload)
        result = response.json()

        if result.get("RetStatus") == 1:
            return result, otp, None
        else:
            return None, None, result.get("StrRetStatus")

    except Exception as e:
        return None, None, str(e)


def send_campaign_confirmation_sms(campaign, needs_mentor):
    """
    ارسال پیامک اطلاع‌رسانی وضعیت کمپین به کاربر و مدیران با استفاده از الگوهای ملی پیامک
    """
    try:
        # چک کردن تعداد مدیران
        staff_am_users = CustomUser.objects.filter(Q(is_staff=True) | Q(is_am=True))

        # اطلاعات کمپین
        topic = campaign.topic.first().name if campaign.topic.exists() else 'نامشخص'
        customer_name = campaign.customer.get_full_name()
        customer_phone = campaign.customer.phone_number

        # ارسال پیامک به مشتری با الگو (کد متن 337938)
        payload_user = {
            "username": settings.MELIPAYAMAK_USERNAME,
            "password": settings.MELIPAYAMAK_PASSWORD,
            "to": customer_phone,
            "bodyId": "337938",  # کد الگو مخصوص مشتری
            "text": topic
        }
        user_response = requests.post(
            "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
            json=payload_user
        )
        user_result = user_response.json()

        if user_result.get("RetStatus") != 1:
            return False, f"User SMS failed: {user_result.get('StrRetStatus')}"

        # ارسال پیامک به مدیران با الگو (کد متن 337941)
        for staff_am_user in staff_am_users:
            if staff_am_user.phone_number:
                pattern_text = f"{topic};{customer_name}"
                payload_admin = {
                    "username": settings.MELIPAYAMAK_USERNAME,
                    "password": settings.MELIPAYAMAK_PASSWORD,
                    "to": staff_am_user.phone_number,
                    "bodyId": "337941",  # کد الگو مخصوص مدیران
                    "text": pattern_text
                }
                admin_response = requests.post(
                    "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
                    json=payload_admin
                )
                admin_result = admin_response.json()
                if admin_result.get("RetStatus") != 1:
                    return False, f"Admin SMS failed: {admin_result.get('StrRetStatus')}"

        return True, None

    except Exception as e:
        print(f"Error in sending SMS: {str(e)}")
        return False, str(e)

def send_campaign_review_sms(campaign, editing_campaign):
    """
    ارسال پیامک اطلاع‌رسانی بررسی کمپین به کاربر با استفاده از الگو
    """
    try:
        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD

        # استخراج نام موضوع کمپین
        topic = campaign.topic.first().name if campaign.topic.exists() else 'نامشخص'
        customer_phone = campaign.customer.phone_number.strip() if campaign.customer else None

        # ارسال پیامک فقط در صورتی که شماره موجود باشد
        if customer_phone:
            payload = {
                "username": username,
                "password": password,
                "to": customer_phone,
                "bodyId": "337980",  # کد متن الگو
                "text": topic  # متن پیامک شامل نام موضوع کمپین
            }

            response = requests.post(
                "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
                json=payload
            )

            result = response.json()
            if result.get("RetStatus") != 1:
                return False, f"User SMS failed: {result.get('StrRetStatus')}"

        return True, None

    except Exception as e:
        print(f"Error in sending review SMS: {str(e)}")
        return False, str(e)

def send_campaign_start_sms(campaign):
    """
    ارسال پیامک اطلاع‌رسانی شروع کمپین به کاربر و دیلرها با استفاده از الگو
    """
    try:
        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD

        # نام موضوع کمپین
        topic = campaign.topic.first().name if campaign.topic.exists() else 'نامشخص'

        # ارسال پیامک به مشتری
        if campaign.customer and campaign.customer.phone_number:
            customer_payload = {
                "username": username,
                "password": password,
                "to": campaign.customer.phone_number.strip(),
                "bodyId": "337981",  # الگوی مشتری
                "text": topic
            }

            customer_response = requests.post(
                "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
                json=customer_payload
            )
            customer_result = customer_response.json()
            if customer_result.get("RetStatus") != 1:
                return False, f"Customer SMS failed: {customer_result.get('StrRetStatus')}"

        # ارسال پیامک به دیلرها
        dealers = CustomUser.objects.filter(user_type='dealer')
        for dealer in dealers:
            if dealer.phone_number:
                dealer_payload = {
                    "username": username,
                    "password": password,
                    "to": dealer.phone_number.strip(),
                    "bodyId": "337982",  # الگوی دیلرها
                    "text": topic
                }

                dealer_response = requests.post(
                    "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
                    json=dealer_payload
                )
                dealer_result = dealer_response.json()
                if dealer_result.get("RetStatus") != 1:
                    return False, f"Dealer SMS failed: {dealer_result.get('StrRetStatus')}"

        return True, None

    except Exception as e:
        print(f"Error in sending start campaign SMS: {str(e)}")
        return False, str(e)

def send_campaign_mentor_assignment_sms(campaign):
    """
    ارسال پیامک اطلاع‌رسانی تخصیص مشاور به کاربر با استفاده از الگو
    """
    try:
        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD

        # استخراج مقادیر متغیرها
        mentor_name = campaign.assigned_mentor.get_full_name() if campaign.assigned_mentor else 'نامشخص'
        topic = campaign.topic.first().name if campaign.topic.exists() else 'نامشخص'
        customer_phone = campaign.customer.phone_number.strip() if campaign.customer else None

        if customer_phone:
            payload = {
                "username": username,
                "password": password,
                "to": customer_phone,
                "bodyId": "337984",  # الگوی تخصیص مشاور
                "text": f"{mentor_name};{topic}"  # ترتیب دقیق باید مطابق الگو باشد
            }

            response = requests.post(
                "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
                json=payload
            )

            result = response.json()
            if result.get("RetStatus") != 1:
                return False, f"Mentor SMS failed: {result.get('StrRetStatus')}"

        return True, None

    except Exception as e:
        print(f"Error in sending mentor assignment SMS: {str(e)}")
        return False, str(e)

def send_campaign_finished_sms(campaign):
    """
    ارسال پیامک اطلاع‌رسانی پایان کمپین به کاربر با استفاده از الگو
    """
    try:
        # تنظیمات ملی پیامک
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD

        # استخراج نام موضوع کمپین
        topic = campaign.topic.first().name if campaign.topic.exists() else 'نامشخص'
        customer_phone = campaign.customer.phone_number.strip() if campaign.customer else None

        # ارسال پیامک فقط در صورتی که شماره موجود باشد
        if customer_phone:
            payload = {
                "username": username,
                "password": password,
                "to": customer_phone,
                "bodyId": "339423",  # کد متن الگو برای پایان کمپین
                "text": topic  # متن پیامک شامل نام موضوع کمپین
            }

            response = requests.post(
                "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
                json=payload
            )

            result = response.json()
            if result.get("RetStatus") != 1:
                return False, f"User SMS failed: {result.get('StrRetStatus')}"

        return True, None

    except Exception as e:
        print(f"Error in sending finished campaign SMS: {str(e)}")
        return False, str(e)

def send_campaign_winner_sms(campaign, winner):
    """Send SMS to campaign winner"""
    try:
        username = settings.MELIPAYAMAK_USERNAME
        password = settings.MELIPAYAMAK_PASSWORD
        
        topic = campaign.topic.first().name if campaign.topic.exists() else 'نامشخص'
        winner_phone = winner.phone_number.strip()
        
        if winner_phone:
            payload = {
                "username": username,
                "password": password,
                "to": winner_phone,
                "bodyId": "339780",  # Update with actual template ID
                "text": f"{topic}"
            }
            
            response = requests.post(
                "https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber",
                json=payload
            )
            
            result = response.json()
            if result.get("RetStatus") != 1:
                return False, f"SMS failed: {result.get('StrRetStatus')}"
                
        return True, None
        
    except Exception as e:
        return False, str(e)
