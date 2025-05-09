# Generated by Django 3.2 on 2025-02-06 20:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('advplatform', '0009_campaign_campaign_dealer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='campaign_dealer',
            field=models.ForeignKey(limit_choices_to={'is_active': True, 'user_type': 'dealer'}, on_delete=django.db.models.deletion.CASCADE, related_name='campaign_dealers', to=settings.AUTH_USER_MODEL),
        ),
    ]
