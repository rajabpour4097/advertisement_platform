# Generated by Django 3.2 on 2025-02-08 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advplatform', '0012_alter_customuser_customer_mentor'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='subject',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
