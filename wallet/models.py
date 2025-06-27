from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from advplatform.models import CustomUser, Campaign

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'کیف پول'
        verbose_name_plural = 'کیف پول ها'

    def __str__(self):
        return f"کیف پول {self.user.get_full_name()}"

    def deposit(self, amount):
        """افزایش موجودی کیف پول"""
        if amount > 0:
            self.balance += Decimal(str(amount))
            self.save()
            return True
        return False

    def withdraw(self, amount):
        """برداشت از کیف پول"""
        if 0 < amount <= self.balance:
            self.balance -= Decimal(str(amount))
            self.save()
            return True
        return False

    def has_sufficient_balance(self, amount):
        """بررسی کافی بودن موجودی"""
        return self.balance >= amount


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'واریز'),
        ('withdraw', 'برداشت'),
        ('campaign_payment', 'پرداخت کمپین'),
    )

    PAYMENT_METHODS = (
        ('wallet', 'کیف پول'),
        ('gateway', 'درگاه پرداخت'),
        ('mixed', 'ترکیبی'),
        ('receipt', 'فیش واریزی'),
    )

    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('reviewing', 'در حال بررسی'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(1000)])
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    description = models.TextField(blank=True)
    tracking_code = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} تومان"


class PaymentReceipt(models.Model):
    """مدل فیش های پرداختی برای شارژ کیف پول"""
    STATUS_CHOICES = (
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
    )

    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='receipt')
    receipt_image = models.ImageField(upload_to='receipts/', verbose_name='تصویر فیش')
    bank_name = models.CharField(max_length=100, verbose_name='نام بانک')
    payment_date = models.DateTimeField(verbose_name='تاریخ پرداخت', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, verbose_name='شماره پیگیری')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_description = models.TextField(blank=True, verbose_name='توضیحات ادمین')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فیش پرداختی'
        verbose_name_plural = 'فیش های پرداختی'
        ordering = ['-created_at']

    def __str__(self):
        return f"فیش پرداختی {self.tracking_number}"
