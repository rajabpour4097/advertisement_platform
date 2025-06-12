from django.contrib.admin import register
from django.contrib import admin

from wallet.models import Wallet, Transaction, PaymentReceipt
# Register your models here.


@register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at', 'updated_at']
    search_fields = ['user']
    

@register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'created_at', 'updated_at']
    search_fields = ['wallet']
    

@register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'receipt_image', 'created_at', 'updated_at']
    search_fields = ['transaction']