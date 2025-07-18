# Generated by Django 3.2 on 2025-05-31 11:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255, verbose_name='موضوع')),
                ('body', models.TextField(verbose_name='متن پیام')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')),
                ('is_read', models.BooleanField(default=False, verbose_name='خوانده شده')),
                ('is_starred', models.BooleanField(default=False, verbose_name='ستاره\u200cدار')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='حذف شده')),
                ('is_spam', models.BooleanField(default=False, verbose_name='هرزنامه')),
                ('has_attachment', models.BooleanField(default=False, verbose_name='دارای پیوست')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL, verbose_name='گیرنده')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL, verbose_name='فرستنده')),
            ],
            options={
                'verbose_name': 'پیام',
                'verbose_name_plural': 'پیام\u200cها',
                'ordering': ['-created_at'],
            },
        ),
    ]
