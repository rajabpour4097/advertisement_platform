from django.core.management.base import BaseCommand
from django.utils import timezone
from advplatform.models import Campaign, CustomUser
from account.models import CampaignTransaction
from wallet.models import Wallet, Transaction
from account.utils.send_notification import (
    send_notification, send_staff_notification, send_am_notification
)
from account.utils.send_sms import send_campaign_not_choose_winner_sms, send_campaign_one_percent_dealer_sms, send_campaign_without_participate_sms
from django.db import transaction as db_transaction
from decimal import Decimal

class Command(BaseCommand):
    
    help = 'بررسی کمپین‌های پایان یافته با مهلت ۴۸ ساعته و انجام عملیات مالی و اطلاع‌رسانی'

    def handle(self, *args, **options):
        now = timezone.now()
        # فقط کمپین‌هایی که status=finished و مهلت ۴۸ ساعته‌شان گذشته و هنوز بررسی نشده‌اند
        expired_campaigns = Campaign.objects.filter(
            status='finished',
            is_active=False,
            endtimedate__lt=now - timezone.timedelta(hours=96),
            finished_review=False
        )

        staff_users = CustomUser.objects.filter(is_staff=True)
        am_users = CustomUser.objects.filter(is_am=True)
        
        if expired_campaigns is None:
            print("There are no expired without check campaigns")

        for campaign in expired_campaigns:
            # شرکت‌کننده‌ها
            participants = CampaignTransaction.objects.filter(campaign=campaign).values_list('dealer', flat=True).distinct()
            participants_users = CustomUser.objects.filter(id__in=participants)

            # حالت ۱: بدون شرکت‌کننده
            if not participants_users.exists():
                refund_amount = Decimal(campaign.get_campaign_price())
                customer_wallet, _ = Wallet.objects.get_or_create(user=campaign.customer)
                with db_transaction.atomic():
                    customer_wallet.deposit(refund_amount)
                    Transaction.objects.create(
                        wallet=customer_wallet,
                        amount=refund_amount,
                        transaction_type='deposit',
                        payment_method='wallet',
                        status='completed',
                        campaign=campaign,
                        description=f"بازگشت مبلغ کمپین بدون شرکت‌کننده (کمپین {campaign.id})"
                    )
                    # اطلاع‌رسانی
                    send_notification(
                        sender=None,
                        recipient=campaign.customer,
                        verb="بازگشت مبلغ کمپین",
                        description=f"کمپین شما بدون شرکت‌کننده پایان یافت و مبلغ {refund_amount} تومان به کیف پول شما بازگشت.",
                        target=campaign
                    )
                    send_staff_notification(
                        sender=None,
                        staff_users=staff_users,
                        verb="کمپین بدون شرکت‌کننده",
                        description=f"کمپین {campaign.id} بدون شرکت‌کننده پایان یافت و مبلغ به مشتری بازگشت.",
                        target=campaign
                    )
                    send_am_notification(
                        sender=None,
                        am_users=am_users,
                        verb="کمپین بدون شرکت‌کننده",
                        description=f"کمپین {campaign.id} بدون شرکت‌کننده پایان یافت و مبلغ به مشتری بازگشت.",
                        target=campaign
                    )
                    send_campaign_without_participate_sms(campaign, refund_amount)
                    # علامت‌گذاری به عنوان بررسی‌شده
                    campaign.finished_review = True
                    campaign.save()
                self.stdout.write(self.style.SUCCESS(f"کمپین {campaign.id}: بازگشت مبلغ به مشتری (بدون شرکت‌کننده)"))

            # حالت ۲: شرکت‌کننده دارد اما برنده انتخاب نشده
            elif not campaign.campaign_dealer:
                gift_amount = Decimal(campaign.get_gift_price())
                customer_wallet, _ = Wallet.objects.get_or_create(user=campaign.customer)
                with db_transaction.atomic():
                    # واریز ۵ درصد به مشتری
                    customer_wallet.deposit(gift_amount)
                    Transaction.objects.create(
                        wallet=customer_wallet,
                        amount=gift_amount,
                        transaction_type='deposit',
                        payment_method='wallet',
                        status='completed',
                        campaign=campaign,
                        description=f"بازگشت ۵٪ مبلغ کمپین {campaign.topic.name} به مشتری (بدون انتخاب برنده)"
                    )
                    # اطلاع‌رسانی به مشتری
                    send_notification(
                        sender=None,
                        recipient=campaign.customer,
                        verb="بازگشت بخشی از مبلغ کمپین",
                        description=f"در کمپین شما برنده‌ای انتخاب نشد و ۵٪ مبلغ ({gift_amount} تومان) به کیف پول شما بازگشت.",
                        target=campaign
                    )
                    
                    send_campaign_not_choose_winner_sms(campaign, gift_amount)
                    
                    # تقسیم ۱٪ بین شرکت‌کننده‌ها
                    total_participants = participants_users.count()
                    if total_participants > 0:
                        one_percent = Decimal(campaign.purposed_price) * Decimal('0.01')
                        share_per_participant = one_percent / total_participants
                        for user in participants_users:
                            user_wallet, _ = Wallet.objects.get_or_create(user=user)
                            user_wallet.deposit(share_per_participant)
                            Transaction.objects.create(
                                wallet=user_wallet,
                                amount=share_per_participant,
                                transaction_type='deposit',
                                payment_method='wallet',
                                status='completed',
                                campaign=campaign,
                                description=f"سهم ۱٪ از مبلغ کمپین {campaign.topic.name} (بدون انتخاب برنده)"
                            )
                            # اطلاع‌رسانی و SMS به شرکت‌کننده
                            send_notification(
                                sender=None,
                                recipient=user,
                                verb="دریافت سهم از کمپین",
                                description=f"در کمپین {campaign.id} برنده‌ای انتخاب نشد و سهمی از ۱٪ مبلغ به کیف پول شما واریز شد.",
                                target=campaign
                            )
                            send_campaign_one_percent_dealer_sms(campaign, dealer=user, gift_amount=share_per_participant)
                    # اطلاع‌رسانی به مدیران
                    send_staff_notification(
                        sender=None,
                        staff_users=staff_users,
                        verb="کمپین بدون انتخاب برنده",
                        description=f"در کمپین {campaign.id} برنده‌ای انتخاب نشد و ۵٪ به مشتری و ۱٪ بین شرکت‌کننده‌ها تقسیم شد.",
                        target=campaign
                    )
                    send_am_notification(
                        sender=None,
                        am_users=am_users,
                        verb="کمپین بدون انتخاب برنده",
                        description=f"در کمپین {campaign.id} برنده‌ای انتخاب نشد و ۵٪ به مشتری و ۱٪ بین شرکت‌کننده‌ها تقسیم شد.",
                        target=campaign
                    )
                    # علامت‌گذاری به عنوان بررسی‌شده
                    campaign.finished_review = True
                    campaign.save()
                self.stdout.write(self.style.SUCCESS(f"کمپین {campaign.id}: تقسیم مبلغ بین مشتری و شرکت‌کننده‌ها (بدون انتخاب برنده)"))