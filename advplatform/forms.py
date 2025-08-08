from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Resume, Topic, Portfolio, City  # افزودن Portfolio و City
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model




class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل کاربر'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'custom-class'}))
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # اجازه ورود به کاربران غیرفعال با is_active=False
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password, 
                check_active=False  # این پارامتر به authenticate اضافه می‌شود
            )
            
            if self.user_cache is None:
                raise ValidationError(
                    '',
                    code='invalid_login'
                )
            
            # بررسی وضعیت کاربر مشاور
            if self.user_cache.user_type == 'mentor' and not self.user_cache.is_active:
                raise ValidationError(
                    'حساب کاربری شما هنوز توسط مدیر تایید نشده است.',
                    code='inactive_mentor'
                )
                
        return self.cleaned_data


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, check_active=True, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            if check_active:
                if user.is_active:
                    return user
            else:
                return user  # برگرداندن کاربر حتی اگر غیرفعال باشد
        return None


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        

class ResumeForm(forms.ModelForm):
    file = forms.FileField(label='فایل رزومه', required=False)
    bank_account = forms.CharField(
        max_length=24,
        min_length=24,
        required=True,
        label='شماره حساب بانکی',
        error_messages={
            'required': 'لطفاً شماره حساب بانکی خود را وارد کنید!',
        }
    )

    class Meta:
        model = Resume
        fields = [
            'dealer_type', 'service_area', 'describe', 
            'specialty_categories', 'services', 'socialmedia_and_sites',
            'tools_and_platforms', 'file', 'portfolios', 'partner_brand',
            'bank_account'
        ]
        widgets = {
            'dealer_type': forms.Select(attrs={'class': 'form-control'}),
            'describe': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'cols': 30}),
            'services': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 30}),
            'socialmedia_and_sites': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 30}),
            'tools_and_platforms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 30}),
            'partner_brand': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 30}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تبدیل اولیه داده های خام hidden ها به فرمت قابل قبول قبل از validation
        if self.data:
            mutable_data = self.data.copy()

            def normalize_m2m_field(field_name):
                raw = mutable_data.get(field_name, None)
                if raw is None:
                    return
                raw = raw.strip()
                if raw == '':
                    # باید به لیست خالی ست شود تا ModelMultipleChoiceField خطا ندهد
                    mutable_data.setlist(field_name, [])
                else:
                    ids = [x.strip() for x in raw.split(',') if x.strip().isdigit()]
                    mutable_data.setlist(field_name, ids)

            normalize_m2m_field('portfolios')
            normalize_m2m_field('service_area')

            self.data = mutable_data  # اعمال داده نرمال‌شده

        self.fields['dealer_type'].queryset = Topic.objects.filter(parent__isnull=True)
        self.fields['dealer_type'].empty_label = "انتخاب کنید..."

        self.fields['specialty_categories'].queryset = Topic.objects.none()
        self.fields['specialty_categories'].empty_label = "انتخاب کنید..."

        self.fields['portfolios'].required = False
        self.fields['service_area'].required = False

        instance = kwargs.get('instance')
        if instance and instance.dealer_type:
            self.fields['specialty_categories'].queryset = Topic.objects.filter(parent=instance.dealer_type)

        dealer_type_id = self.data.get('dealer_type') or (instance.dealer_type_id if instance else None)
        if dealer_type_id:
            try:
                self.fields['specialty_categories'].queryset = Topic.objects.filter(parent_id=int(dealer_type_id))
            except (ValueError, TypeError):
                pass

    # در صورت تمایل می‌توانید متدهای clean_service_area / clean_portfolios را حذف کنید
    def clean_service_area(self):
        # حالا مقدار ورودی یک لیست از آیدی‌هاست و ModelMultipleChoiceField خودش queryset می‌سازد
        return self.cleaned_data.get('service_area')

    def clean_portfolios(self):
        return self.cleaned_data.get('portfolios')
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file

        allowed_types = [
            'application/pdf', 
            'application/zip',
            'application/x-zip-compressed'
        ]
        
        if file.content_type not in allowed_types:
            raise forms.ValidationError('فقط فایل‌های PDF یا ZIP مجاز هستند.')

        if file.size > 10 * 1024 * 1024:  # 10 مگابایت محدودیت حجم
            raise forms.ValidationError('حداکثر حجم فایل ۱۰ مگابایت است.')

        return file

    def clean_bank_account(self):
        value = self.cleaned_data.get('bank_account', '') or ''
        value = value.replace(' ', '').strip()
        if not value:
            raise ValidationError('شماره حساب الزامی است.')
        if not value.isdigit():
            raise ValidationError('شماره حساب باید فقط شامل ارقام باشد.')
        if len(value) != 24:
            raise ValidationError('شماره حساب باید دقیقاً 24 رقم باشد.')
        return value

class ResumeReviewForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['status', 'manager_comment']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_status'
            }),
            'manager_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'نظر یا توضیحات مدیر در مورد رزومه...',
                'id': 'id_manager_comment'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # فقط وضعیت‌های مربوط به بررسی مدیر را نمایش دهید
        self.fields['status'].choices = [
            ('under_review', 'در حال بررسی'),
            ('needs_editing', 'نیاز به ویرایش'),
            ('approved', 'تایید شده'),
            ('rejected', 'رد شده'),
        ]
        
        # اجباری کردن کامنت برای وضعیت‌های خاص
        self.fields['manager_comment'].help_text = 'برای وضعیت "نیاز به ویرایش" و "رد شده" نوشتن توضیحات الزامی است.'
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        manager_comment = cleaned_data.get('manager_comment')
        
        # اجباری کردن کامنت برای وضعیت‌های خاص
        if status in ['needs_editing', 'rejected']:
            if not manager_comment or not manager_comment.strip():
                raise forms.ValidationError(
                    f'برای وضعیت "{dict(self.fields["status"].choices)[status]}" نوشتن توضیحات الزامی است.'
                )
        
        return cleaned_data
