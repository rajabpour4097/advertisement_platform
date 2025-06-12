from django import forms
from .models import PaymentReceipt, Transaction

class WalletChargeForm(forms.Form):
    PAYMENT_CHOICES = (
        ('gateway', 'درگاه پرداخت'),
        ('receipt', 'فیش واریزی'),
    )
    
    amount = forms.DecimalField(
        min_value=10000,
        max_value=100000000,
        label='مبلغ (تومان)',
        help_text='لطفا مبلغ را به تومان وارد کنید',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        label='روش پرداخت',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )

    def clean_payment_method(self):
        payment_method = self.cleaned_data.get('payment_method')
        if payment_method not in ['gateway', 'receipt']:
            raise forms.ValidationError('لطفا یک روش پرداخت معتبر انتخاب کنید')
        return payment_method


class PaymentReceiptForm(forms.ModelForm):
    class Meta:
        model = PaymentReceipt
        fields = ['receipt_image', 'bank_name', 'payment_date', 'tracking_number']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control'}),
        } 