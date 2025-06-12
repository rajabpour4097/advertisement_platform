from django.core.management.base import BaseCommand
from django.utils import timezone
from advplatform.models import Campaign
from account.utils.send_notification import notify_campaign_actions
from account.utils.send_sms import send_campaign_finished_sms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Checks for finished campaigns and updates their status'

    def handle(self, *args, **options):
        # Get all active campaigns that have ended
        finished_campaigns = Campaign.objects.filter(
            is_active=True,
            endtimedate__lt=timezone.now(),
            status='progressing'
        )

        # Get staff and AM users for notifications
        staff_users = CustomUser.objects.filter(is_staff=True)
        am_users = CustomUser.objects.filter(is_am=True)
        
        if not finished_campaigns:
            self.stdout.write(
                self.style.SUCCESS(
                    'No finished campaigns found'
                )
            )
            return

        for campaign in finished_campaigns:
            # Update campaign status
            campaign.status = 'finished'
            campaign.is_active = False
            campaign.save()

            # Send notifications
            notify_campaign_actions(
                user=campaign.customer,
                campaign=campaign,
                action_type='finished',
                staff_users=staff_users,
                am_users=am_users
            )

            # Send SMS to customer
            success, error = send_campaign_finished_sms(campaign)
            if not success:
                self.stdout.write(
                    self.style.WARNING(
                        f'Failed to send SMS for campaign {campaign.id}: {error}'
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated campaign {campaign.id} to finished status'
                )
            ) 