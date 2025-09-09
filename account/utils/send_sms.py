import random
import requests
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from account.models import CustomUser

def generate_otp():
    return str(random.randint(100000, 999999))

def store_otp(user_phone, otp, expire_time=120):
    cache.set(f"otp_{user_phone}", otp, expire_time)

def verify_otp(user_phone, otp):
    cache_key = f"otp_{user_phone}"
    stored_otp = cache.get(cache_key)
    if stored_otp and stored_otp == otp:
        cache.delete(cache_key)
        return True
    return False

def send_sms(to, body_id, text):
    try:
        payload = {
            "username": settings.MELIPAYAMAK_USERNAME,
            "password": settings.MELIPAYAMAK_PASSWORD,
            "to": to.strip(),
            "bodyId": body_id,
            "text": text
        }
        response = requests.post("https://rest.payamak-panel.com/api/SendSMS/BaseServiceNumber", json=payload)
        result = response.json()
        if result.get("RetStatus") != 1:
            return False, f"SMS failed: {result.get('StrRetStatus')}"
        return True, None
    except Exception as e:
        return False, str(e)

def send_activation_sms(user):
    otp = generate_otp()
    store_otp(user.phone_number, otp)
    ok, error = send_sms(user.phone_number, "337375", otp)
    return (ok, otp, error) if ok else (None, None, error)

def send_campaign_confirmation_sms(campaign, needs_mentor):
    topic = campaign.topic.name
    customer_name = campaign.customer.get_full_name()
    customer_phone = campaign.customer.phone_number

    ok, error = send_sms(customer_phone, "337938", topic)
    if not ok:
        return False, f"User SMS failed: {error}"

    staff_am_users = CustomUser.objects.filter(Q(is_staff=True) | Q(is_am=True))
    for user in staff_am_users:
        if user.phone_number:
            text = f"{topic};{customer_name}"
            ok, error = send_sms(user.phone_number, "337941", text)
            if not ok:
                return False, f"Admin SMS failed: {error}"

    return True, None

def send_campaign_review_sms(campaign, editing_campaign):
    topic = campaign.topic.name
    phone = campaign.customer.phone_number.strip() if campaign.customer else None
    return send_sms(phone, "337980", topic) if phone else (True, None)

def send_campaign_start_sms(campaign):
    topic = campaign.topic.name

    customer = campaign.customer
    if customer and customer.phone_number:
        ok, error = send_sms(customer.phone_number, "337981", topic)
        if not ok:
            return False, f"Customer SMS failed: {error}"

    dealers = CustomUser.objects.filter(user_type='dealer')
    for dealer in dealers:
        if dealer.phone_number:
            ok, error = send_sms(dealer.phone_number, "337982", topic)
            if not ok:
                return False, f"Dealer SMS failed: {error}"

    return True, None

def send_campaign_mentor_assignment_sms(campaign):
    mentor_name = campaign.assigned_mentor.get_full_name() if campaign.assigned_mentor else 'نامشخص'
    topic = campaign.topic.name
    phone = campaign.customer.phone_number.strip() if campaign.customer else None
    text = f"{mentor_name};{topic}"
    return send_sms(phone, "337984", text) if phone else (True, None)

def send_campaign_finished_sms(campaign):
    topic = campaign.topic.name
    phone = campaign.customer.phone_number.strip() if campaign.customer else None
    return send_sms(phone, "339423", topic) if phone else (True, None)

def send_campaign_winner_sms(campaign, winner):
    topic = campaign.topic.name
    return send_sms(winner.phone_number, "341519", topic)

def send_campaign_without_participate_sms(campaign, refund_amount):
    topic = campaign.topic.name
    phone = campaign.customer.phone_number.strip() if campaign.customer else None
    text = f"{topic};{refund_amount}"
    return send_sms(phone, "341522", text) if phone else (True, None)

def send_campaign_not_choose_winner_sms(campaign, gift_amount):
    topic = campaign.topic.name
    phone = campaign.customer.phone_number.strip() if campaign.customer else None
    text = f"{topic};{gift_amount}"
    return send_sms(phone, "341523", text) if phone else (True, None)

def send_campaign_one_percent_dealer_sms(campaign, dealer, gift_amount):
    topic = campaign.topic.name
    text = f"{topic};{gift_amount}"
    return send_sms(dealer.phone_number, "341524", text)

def send_campaign_cancel_sms(campaign):
    topic = campaign.topic.name
    phone = campaign.customer.phone_number.strip() if campaign.customer else None
    return send_sms(phone, "349749", topic) if phone else (True, None)

def send_resume_review_sms(resume, new_status):
    """ارسال پیامک برای بررسی رزومه"""
    
    # موقتاً از body_id عمومی استفاده می‌کنیم
    body_id = "337375"  # یا هر body_id عمومی که دارید
    
    phone = resume.user.phone_number.strip() if resume.user.phone_number else None
    if not phone:
        return False, "User phone number not found"
    
    # کد پیگیری رزومه
    text = str(resume.id)
    
    return send_sms(phone, body_id, text)