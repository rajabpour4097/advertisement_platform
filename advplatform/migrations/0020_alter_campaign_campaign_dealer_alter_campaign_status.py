# Generated by Django 5.1.6 on 2025-02-16 05:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advplatform', '0019_portfolio_execution_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='campaign_dealer',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_active': True, 'user_type': 'dealer'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='campaign_dealers', to=settings.AUTH_USER_MODEL, verbose_name='مجری کمپین'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='status',
            field=models.CharField(choices=[('reviewing', 'در حال بررسی'), ('progressing', 'در حال برگزاری'), ('unsuccessful', 'ناموفق'), ('successful', 'موفق')], default='reviewing', max_length=30, verbose_name='وضعیت اجرای کمپین'),
        ),
    ]
