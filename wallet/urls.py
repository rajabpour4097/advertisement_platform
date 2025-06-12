from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('', views.WalletHomeView.as_view(), name='home'),
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('charge/', views.WalletChargeView.as_view(), name='charge'),
    path('verify/', views.PaymentVerifyView.as_view(), name='verify'),
    path('upload-receipt/<int:transaction_id>/', views.UploadReceiptView.as_view(), name='upload_receipt'),
    path('campaign-payment/<int:campaign_id>/', views.CampaignPaymentView.as_view(), name='campaign_payment'),
    path('receipts/management/', views.ReceiptManagementView.as_view(), name='receipt_management'),
] 