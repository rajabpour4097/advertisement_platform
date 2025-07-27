from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from advplatform.models import Campaign
from account.utils.send_sms import send_campaign_cancel_sms
from django.contrib.auth import get_user_model
from django.db.models import Q
from account.utils.send_notification import notify_campaign_actions

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Cancels unpaid campaigns older than 10 days and notifies users'

    def handle(self, *args, **options):
        # تاریخ ده روز پیش
        ten_days_ago = timezone.now() - timedelta(days=10)

        # کمپین‌های واجد شرایط
        unpaid_campaigns = Campaign.objects.filter(
            status='unpaid',
            created_time__lt=ten_days_ago
        )

        if not unpaid_campaigns.exists():
            self.stdout.write(self.style.SUCCESS('No unpaid campaigns older than 10 days found.'))
            return

        staff_users = CustomUser.objects.filter(is_staff=True)
        am_users = CustomUser.objects.filter(is_am=True)

        for campaign in unpaid_campaigns:
            customer = campaign.customer
            phone = customer.phone_number.strip() if customer else None

            # تغییر وضعیت کمپین
            campaign.status = 'cancel'
            campaign.modified_time = timezone.now()
            campaign.save()

            # ارسال پیامک فقط به مشتری
            if phone:
                ok, error = send_campaign_cancel_sms(campaign)
                if not ok:
                    self.stdout.write(self.style.WARNING(
                        f'Failed to send SMS to {phone} for campaign {campaign.id}: {error}'
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f'SMS sent to customer for campaign {campaign.id}'
                    ))

            # ارسال نوتیفیکیشن به مشتری، استاف و AM
            notify_campaign_actions(
                user=customer,
                campaign=campaign,
                action_type='cancel',
                staff_users=staff_users,
                am_users=am_users
            )

            self.stdout.write(self.style.SUCCESS(
                f'Campaign {campaign.id} cancelled and notifications sent.'
            ))
