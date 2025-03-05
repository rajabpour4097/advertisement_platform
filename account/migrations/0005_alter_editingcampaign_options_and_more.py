# Generated by Django 5.1.6 on 2025-03-04 14:53

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_rename_purposed_price_campaigntransaction_proposal_price_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='editingcampaign',
            options={'ordering': ['-created_at'], 'verbose_name': 'ویرایش های کمپین', 'verbose_name_plural': 'ویرایش های کمپین ها'},
        ),
        migrations.RenameField(
            model_name='editingcampaign',
            old_name='created_time',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='editingcampaign',
            old_name='modified_time',
            new_name='modified_at',
        ),
        migrations.AddField(
            model_name='campaigntransaction',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='campaigntransaction',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
