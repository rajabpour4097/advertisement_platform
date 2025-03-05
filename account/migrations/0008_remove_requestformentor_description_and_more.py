# Generated by Django 5.1.6 on 2025-03-05 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_requestformentor_description_requestformentor_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestformentor',
            name='description',
        ),
        migrations.AlterField(
            model_name='requestformentor',
            name='status',
            field=models.CharField(choices=[('', ''), ('pending', 'در حال بررسی'), ('approved', 'تایید'), ('reject', 'عدم تایید')], default='pending', max_length=30, verbose_name='وضعیت درخواست'),
        ),
    ]
