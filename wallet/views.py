from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.admin.views.decorators import staff_member_required
import json
import requests
from decimal import Decimal

from .models import Wallet, Transaction, PaymentReceipt
from advplatform.models import Campaign
from .forms import PaymentReceiptForm, WalletChargeForm

# ZarinPal Configuration
MERCHANT = settings.ZARINPAL_MERCHANT_ID
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
description = "پرداخت در سامانه تبلیغات"  # Required
CallbackURL = settings.ZARINPAL_CALLBACK_URL # Important: replace with your host


class WalletHomeView(LoginRequiredMixin, View):
    template_name = 'account/wallet/home.html'
    
    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        transactions = wallet.transactions.all()[:5]  # Get last 5 transactions
        context = {
            'wallet': wallet,
            'transactions': transactions,
        }
        return render(request, self.template_name, context)


class TransactionListView(LoginRequiredMixin, ListView):
    template_name = 'account/wallet/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        wallet = get_object_or_404(Wallet, user=self.request.user)
        return Transaction.objects.filter(wallet=wallet)


@method_decorator(login_required, name='dispatch')
class WalletChargeView(View):
    template_name = 'account/wallet/charge.html'

    def get(self, request):
        form = WalletChargeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = WalletChargeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_method = form.cleaned_data['payment_method']
            
            print(f"Selected payment method: {payment_method}")  # برای دیباگ
            
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            
            # Create transaction record
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='deposit',
                payment_method=payment_method,
                status='pending',  # اضافه کردن وضعیت اولیه
                description='شارژ کیف پول'
            )

            if payment_method == 'gateway':
                return self.process_gateway_payment(request, transaction)
            elif payment_method == 'receipt':
                return redirect('wallet:upload_receipt', transaction_id=transaction.id)
        else:
            print(f"Form errors: {form.errors}")  # برای دیباگ
            
        return render(request, self.template_name, {'form': form})

    def process_gateway_payment(self, request, transaction):
        amount_rials = int(transaction.amount * 10)
        
        print(f"Processing gateway payment for amount: {amount_rials} rials")  # برای دیباگ
        
        req_data = {
            "merchant_id": MERCHANT,
            "amount": amount_rials,
            "callback_url": CallbackURL,
            "description": description,
            "metadata": {"mobile": request.user.phone_number, "transaction_id": transaction.id}
        }
        req_header = {"accept": "application/json",
                     "content-type": "application/json"}  # اصلاح کاراکتر اضافی
        
        try:
            print(f"Sending request to ZarinPal: {req_data}")  # برای دیباگ
            response = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
            print(f"ZarinPal response: {response.text}")  # برای دیباگ
            
            if response.status_code == 200:
                response = response.json()
                if response['data']['code'] == 100:
                    transaction.tracking_code = response['data']['authority']
                    transaction.save()
                    return redirect(ZP_API_STARTPAY.format(authority=response['data']['authority']))
                else:
                    transaction.status = 'failed'
                    transaction.save()
                    messages.error(request, "خطا در اتصال به درگاه پرداخت")
            return redirect('wallet:home')
            
        except requests.exceptions.RequestException:
            transaction.status = 'failed'
            transaction.save()
            messages.error(request, "خطا در اتصال به درگاه پرداخت")
            return redirect('wallet:home')


@method_decorator(csrf_exempt, name='dispatch')
class PaymentVerifyView(View):
    def get(self, request):
        t_status = request.GET.get('Status')
        t_authority = request.GET.get('Authority')
        
        if t_status == 'OK':
            try:
                transaction = Transaction.objects.get(id=request.session.get('transaction_id'))
                
                # Verify payment with ZarinPal
                req_data = {
                    "merchant_id": MERCHANT,
                    "amount": transaction.amount,
                    "authority": t_authority
                }
                req_header = {"accept": "application/json", "content-type": "application/json'"}
                
                response = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
                
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data['data']['code'] == 100:
                        # Payment successful
                        transaction.status = 'completed'
                        transaction.save()
                        
                        # If it's a mixed payment, deduct from wallet now
                        if transaction.payment_method == 'mixed':
                            wallet = transaction.wallet
                            description = transaction.description
                            wallet_amount = int(description.split('کیف پول: ')[1].split(' تومان')[0].replace(',', ''))
                            wallet.withdraw(wallet_amount)
                            wallet.save()
                            print(f"Deducting {wallet_amount} from wallet {wallet.id}")
                        
                        # Update campaign status if it's a campaign payment
                        if transaction.transaction_type == 'campaign_payment':
                            campaign = transaction.campaign
                            campaign.is_active = True
                            campaign.save()
                        
                        messages.success(request, 'پرداخت با موفقیت انجام شد.')
                        return redirect('wallet:transactions')
                    else:
                        # Payment failed
                        transaction.status = 'failed'
                        transaction.save()
                        messages.error(request, 'پرداخت ناموفق بود.')
                        return redirect('wallet:transactions')
                else:
                    # Error in verification
                    transaction.status = 'failed'
                    transaction.save()
                    messages.error(request, 'خطا در تایید پرداخت.')
                    return redirect('wallet:transactions')
                    
            except Transaction.DoesNotExist:
                messages.error(request, 'تراکنش یافت نشد.')
                return redirect('wallet:transactions')
        else:
            # User cancelled payment
            try:
                transaction = Transaction.objects.get(id=request.session.get('transaction_id'))
                transaction.status = 'failed'
                transaction.save()
                messages.error(request, 'پرداخت لغو شد.')
                return redirect('wallet:transactions')
            except Transaction.DoesNotExist:
                messages.error(request, 'تراکنش یافت نشد.')
                return redirect('wallet:transactions')


@method_decorator(login_required, name='dispatch')
class UploadReceiptView(CreateView):
    model = PaymentReceipt
    form_class = PaymentReceiptForm
    template_name = 'account/wallet/upload_receipt.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_id = self.kwargs.get('transaction_id')
        context['transaction'] = get_object_or_404(Transaction, id=transaction_id)
        return context
    
    def form_valid(self, form):
        transaction_id = self.kwargs.get('transaction_id')
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        if transaction.wallet.user != self.request.user:
            raise Http404("شما به این تراکنش دسترسی ندارید.")
        
        receipt = form.save(commit=False)
        receipt.transaction = transaction
        receipt.save()
        
        transaction.status = 'reviewing'
        transaction.save()
        
        messages.success(self.request, 'فیش پرداختی با موفقیت ثبت شد و در انتظار تایید می‌باشد.')
        return redirect('wallet:home')


@method_decorator(login_required, name='dispatch')
class CampaignPaymentView(View):
    template_name = 'account/wallet/campaign_payment.html'
    
    def get(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, id=campaign_id)
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        campaign_price = campaign.get_campaign_price()
        
        context = {
            'campaign': campaign,
            'wallet': wallet,
            'wallet_sufficient': wallet.has_sufficient_balance(campaign_price)
        }
        return render(request, self.template_name, context)
    
    def post(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, id=campaign_id)
        payment_method = request.POST.get('payment_method')
        wallet_amount = Decimal(request.POST.get('wallet_amount', 0))
        
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        total_amount = campaign.purposed_price
        
        if payment_method == 'wallet':
            if not wallet.has_sufficient_balance(total_amount):
                messages.error(request, 'موجودی کیف پول کافی نیست.')
                return redirect('wallet:campaign_payment', campaign_id=campaign_id)
                
            # Create transaction
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=total_amount,
                transaction_type='campaign_payment',
                payment_method='wallet',
                campaign=campaign,
                status='completed',
                description=f'پرداخت کامل از کیف پول: {total_amount} تومان'
            )
            
            # Update wallet balance
            wallet.withdraw(total_amount)
            
            # Update campaign status
            campaign.is_active = True
            campaign.save()
            
            messages.success(request, 'پرداخت با موفقیت انجام شد.')
            return redirect('account:campaigns')
            
        elif payment_method == 'gateway':
            # Create transaction for gateway payment
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=total_amount,
                transaction_type='campaign_payment',
                payment_method='gateway',
                campaign=campaign,
                description=f'پرداخت از درگاه: {total_amount} تومان'
            )
            return self.process_gateway_payment(request, transaction)
            
        elif payment_method == 'mixed':
            if not wallet.has_sufficient_balance(wallet_amount):
                messages.error(request, 'موجودی کیف پول کافی نیست.')
                return redirect('wallet:campaign_payment', campaign_id=campaign_id)
                
            gateway_amount = total_amount - wallet_amount
            
            # Create transaction for mixed payment
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=total_amount,
                transaction_type='campaign_payment',
                payment_method='mixed',
                campaign=campaign,
                description=f'پرداخت ترکیبی - کیف پول: {wallet_amount} تومان، درگاه: {gateway_amount} تومان'
            )
            
            # Store transaction ID in session for verification
            request.session['transaction_id'] = transaction.id
            
            # Process remaining amount through gateway
            return self.process_gateway_payment(request, transaction, gateway_amount)
            
        messages.error(request, 'روش پرداخت نامعتبر است.')
        return redirect('wallet:campaign_payment', campaign_id=campaign_id)
    
    def process_gateway_payment(self, request, transaction, amount=None):
        if amount is None:
            amount = transaction.amount
            
        req_data = {
            "merchant_id": MERCHANT,
            "amount": int(amount),
            "callback_url": CallbackURL,
            "description": description,
            "metadata": {"mobile": request.user.phone_number, "transaction_id": transaction.id}
        }
        req_header = {"accept": "application/json",
                     "content-type": "application/json'"}
        
        try:    
            response = requests.post(url=ZP_API_REQUEST, data=json.dumps(
                req_data), headers=req_header)
            
            if response.status_code == 200:
                response = response.json()
                if response['data']['code'] == 100:
                    transaction.tracking_code = response['data']['authority']
                    transaction.save()
                    return redirect(ZP_API_STARTPAY.format(authority=response['data']['authority']))
                else:
                    transaction.status = 'failed'
                    transaction.save()
                    messages.error(request, "خطا در اتصال به درگاه پرداخت")
            return redirect('wallet:campaign_payment', campaign_id=transaction.campaign.id)
            
        except requests.exceptions.RequestException:
            transaction.status = 'failed'
            transaction.save()
            messages.error(request, "خطا در اتصال به درگاه پرداخت")
            return redirect('wallet:campaign_payment', campaign_id=transaction.campaign.id)


@method_decorator(staff_member_required, name='dispatch')
class ReceiptManagementView(ListView):
    template_name = 'account/wallet/receipt_management.html'
    context_object_name = 'receipts'
    paginate_by = 20

    def get_queryset(self):
        return PaymentReceipt.objects.select_related(
            'transaction', 
            'transaction__wallet', 
            'transaction__wallet__user'
        ).filter(
            transaction__status='reviewing'
        ).order_by('-transaction__created_at')

    def post(self, request):
        receipt_id = request.POST.get('receipt_id')
        action = request.POST.get('action')
        
        receipt = get_object_or_404(PaymentReceipt, id=receipt_id)
        transaction = receipt.transaction
        
        if action == 'approve':
            # تایید فیش و به‌روزرسانی موجودی کیف پول
            transaction.status = 'completed'
            transaction.save()
            transaction.wallet.deposit(transaction.amount)
            messages.success(request, 'فیش پرداختی تایید و موجودی کیف پول به‌روز شد.')
            
        elif action == 'reject':
            # رد فیش
            transaction.status = 'rejected'
            transaction.save()
            messages.warning(request, 'فیش پرداختی رد شد.')
            
        return redirect('wallet:receipt_management')
