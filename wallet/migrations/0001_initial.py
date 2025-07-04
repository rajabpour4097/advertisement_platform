# Generated by Django 3.2 on 2025-06-08 20:55

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('advplatform', '0002_topic_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=0, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wallet', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'کیف پول',
                'verbose_name_plural': 'کیف پول ها',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=0, max_digits=10, validators=[django.core.validators.MinValueValidator(1000)])),
                ('transaction_type', models.CharField(choices=[('deposit', 'واریز'), ('withdraw', 'برداشت'), ('campaign_payment', 'پرداخت کمپین')], max_length=20)),
                ('payment_method', models.CharField(choices=[('wallet', 'کیف پول'), ('gateway', 'درگاه پرداخت'), ('mixed', 'ترکیبی'), ('receipt', 'فیش واریزی')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'در انتظار پرداخت'), ('completed', 'تکمیل شده'), ('failed', 'ناموفق'), ('reviewing', 'در حال بررسی')], default='pending', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('tracking_code', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='advplatform.campaign')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='wallet.wallet')),
            ],
            options={
                'verbose_name': 'تراکنش',
                'verbose_name_plural': 'تراکنش ها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PaymentReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_image', models.ImageField(upload_to='receipts/', verbose_name='تصویر فیش')),
                ('bank_name', models.CharField(max_length=100, verbose_name='نام بانک')),
                ('payment_date', models.DateField(verbose_name='تاریخ پرداخت')),
                ('tracking_number', models.CharField(max_length=100, verbose_name='شماره پیگیری')),
                ('status', models.CharField(choices=[('pending', 'در انتظار بررسی'), ('approved', 'تایید شده'), ('rejected', 'رد شده')], default='pending', max_length=20)),
                ('admin_description', models.TextField(blank=True, verbose_name='توضیحات ادمین')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='receipt', to='wallet.transaction')),
            ],
            options={
                'verbose_name': 'فیش پرداختی',
                'verbose_name_plural': 'فیش های پرداختی',
                'ordering': ['-created_at'],
            },
        ),
    ]
