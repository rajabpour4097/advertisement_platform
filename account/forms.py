from django import forms
from advplatform.choices_type import CUSTOMER_TYPE, USER_TYPE
from advplatform.models import Campaign, CampaignImages,\
    CustomUser, Portfolio, PortfolioImages, UsersImages
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from account.models import CampaignTransaction, EditingCampaign
from django.utils import timezone
from account.models import (
    EnvironmentalAdvertisement,
    SocialmediaAdvertisement,
    DigitalAdvertisement,
    PrintingAdvertisement,
    EventMarketingAdvertisement,
    ContentCategory,
    Platform,
)
from advplatform.models import City  # for service_area
from django.core.exceptions import ValidationError



class SignupForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=[('', 'نوع کاربری*')] + list(USER_TYPE), 
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cutomer_type = forms.ChoiceField(
        choices=[('', 'نوع کاربر (حقیقی/حقوقی)')] + list(CUSTOMER_TYPE), 
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'togglePersonFields()'
        })
    )
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    company_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField()
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
        }), 
        required=True
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'cutomer_type', 'first_name', 'last_name', 
                 'company_name', 'phone_number', 'address', 'user_type')
        
    def clean(self):
        cleaned_data = super().clean()
        cutomer_type = cleaned_data.get('cutomer_type')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        company_name = cleaned_data.get('company_name')

        # validation برای مشتری حقیقی
        if cutomer_type == 'private':
            if not first_name:
                self.add_error('first_name', 'نام برای مشتری حقیقی اجباری است.')
            if not last_name:
                self.add_error('last_name', 'نام خانوادگی برای مشتری حقیقی اجباری است.')
        
        # validation برای مشتری حقوقی
        elif cutomer_type == 'juridical':
            if not company_name:
                self.add_error('company_name', 'نام شرکت برای مشتری حقوقی اجباری است.')

        return cleaned_data


class ProfileForm(forms.ModelForm):
    
    profile_image = forms.ImageField(required=False, label="عکس پروفایل")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['is_active'].help_text = None
        if not user.is_staff:
            self.fields['username'].disabled = True
            self.fields['email'].disabled = True
            self.fields['user_type'].disabled = True
            self.fields['is_active'].disabled = True
            self.fields['rank'].disabled = True
            del self.fields['speciality_field']
            
    
    class Meta:
        model = CustomUser
        fields = [
                'username',
                'email',
                'first_name',
                'last_name',
                'speciality_field',#/ for mentor
                'phone_number',#/
                'address',#/
                'birth_date',#/
                'user_type',#/ customer, dealer, mentor
                'cutomer_type',#/ for Customer
                'dealer_type',#/ for Dealer
                'rank',#/  for Dealer and Mentor
                'bussines_value',# /for Customer
                'is_active',#/
            ]
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        profile_image = self.cleaned_data.get('profile_image')
        if profile_image:
            UsersImages.objects.create(customer=user, image=profile_image)

        if commit:
            user.save()
        return user


class PortfolioCreateForm(forms.ModelForm):
    
    subject = forms.CharField(
        max_length=50, 
        required=True, 
        label='عنوان نمونه کار',
        error_messages={
            'required': 'لطفاً عنوان نمونه کار را وارد کنید!',
            'max_length': 'عنوان نمونه کار نمی‌تواند بیش از ۵۰ کاراکتر باشد!',
        }
    )
    done_time = forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
    
    class Meta:
        model = Portfolio
        fields = [
                  'dealer', 
                  'subject', 
                  'topic', 
                  'description', 
                  'done_time', 
                  'is_active'
                  ]
        widgets = {
            'done_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if not user.is_staff and user.user_type == 'dealer':
            self.fields['dealer'].initial = user
            self.fields['dealer'].widget = forms.HiddenInput()
      
         
PortfolioImageFormSet = inlineformset_factory(
    Portfolio, 
    PortfolioImages, 
    fields=('image',), 
    extra=1,
    can_delete=True,
)


class PortfolioEditForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user.user_type == 'dealer':
            self.fields.pop('dealer', None)
            self.fields.pop('is_active', None)
            
    class Meta:
        model = Portfolio
        fields = '__all__'


class CampaignCreateForm(forms.ModelForm):
    
    purposed_price = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_purposed_price',  # اطمینان از وجود ID
            'placeholder': 'مثلاً 10.000.000 تومان'
        })
    )
    
    class Meta:
        model = Campaign
        fields = [
                  'customer',
                  'topic', 
                  'describe', 
                  'purposed_price',
                  ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['customer'].widget.attrs.update({'class': 'form-control'})
        self.fields['topic'].widget.attrs.update({'class': 'form-control'})
        self.fields['describe'].widget.attrs.update({'class': 'form-control',
                                                     'placeholder': 'شرح کمپین باید بیشتر از 100 کاراکتر باشد'
                                                     })
        
        if not user.is_staff and user.user_type == 'customer':
            self.fields['customer'].initial = user
            self.fields['customer'].widget = forms.HiddenInput()
            
    def clean_purposed_price(self):
        data = self.cleaned_data['purposed_price']
        topics = self.cleaned_data.get('topic')  # QuerySet از Topicها

        cleaned = (
            str(data)
            .replace(',', '')
            .replace('تومان', '')
            .replace(' ', '')
            .strip()
        )

        try:
            price = int(cleaned)
        except ValueError:
            raise forms.ValidationError("قیمت وارد شده معتبر نیست.")

        # بررسی تمام موضوعات انتخاب شده
        for topic in topics:
            min_price = topic.min_price
            if min_price and price < min_price:
                raise forms.ValidationError(
                    f"حداقل قیمت برای موضوع '{topic.name}' مبلغ {min_price:,} تومان است."
                )

        return price


   
CampaignImageFormSet = inlineformset_factory(
    Campaign, 
    CampaignImages, 
    fields=('image',), 
    extra=1,
    can_delete=True
)


class ReviewCampaignForm(forms.ModelForm):
    class Meta:
        model = EditingCampaign
        fields = ['edit_reason']
        widgets = {
            'edit_reason': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'دلیل ویرایش را وارد کنید...'}
                ),
        }


class StartCampaignForm(forms.ModelForm):
    starttimedate = forms.DateTimeField(
        required=True,
        error_messages={
            'required': 'لطفاً تاریخ شروع را وارد کنید.',
        }
    )
    endtimedate = forms.DateTimeField(
        required=True,
        error_messages={
            'required': 'لطفاً تاریخ پایان را وارد کنید.',
        }
    )

    class Meta:
        model = Campaign
        fields = ['starttimedate', 'endtimedate']
        widgets = {
            'starttimedate': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'endtimedate': forms.DateTimeInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        starttimedate = cleaned_data.get('starttimedate')
        endtimedate = cleaned_data.get('endtimedate')

        if not starttimedate:
            raise forms.ValidationError("لطفاً تاریخ شروع را وارد کنید.")
        
        if not endtimedate:
            raise forms.ValidationError("لطفاً تاریخ پایان را وارد کنید.")

        if starttimedate and endtimedate:
            if starttimedate > endtimedate:
                raise forms.ValidationError("تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد.")
            
            if starttimedate < timezone.now():
                raise forms.ValidationError("تاریخ شروع نمی‌تواند قبل از زمان فعلی باشد.")

        return cleaned_data


class AssignMentorForm(forms.ModelForm):
    assigned_mentor = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(
            user_type='mentor',
            is_active=True
        ).order_by('first_name', 'last_name'),
        label='انتخاب پیشتیبان',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='لطفاً یک پیشتیبان انتخاب کنید',
        required=True
    )

    class Meta:
        model = Campaign
        fields = ['assigned_mentor']


class EditCampaignForm(forms.ModelForm):
    purposed_price = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_purposed_price',
            'placeholder': 'مثلاً 10.000.000 تومان'
        })
    )

    class Meta:
        model = Campaign
        fields = ['topic', 'describe', 'purposed_price']
        widgets = {
            'describe': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user.user_type == 'customer':
            self.fields.pop('starttimedate', None)
            self.fields.pop('endtimedate', None)

        # تنظیم مقدار اولیه topic
        if self.instance and self.instance.topic.all():
            first_topic = self.instance.topic.first()
            if first_topic:
                self.initial['topic'] = first_topic.id

        # تبدیل قیمت به فرمت مناسب برای نمایش
        if self.instance and self.instance.purposed_price:
            self.initial['purposed_price'] = f"{self.instance.purposed_price:,} تومان"
  
    def clean_purposed_price(self):
        topics = self.cleaned_data.get('topic')
        if not topics:
            raise forms.ValidationError("لطفاً یک موضوع انتخاب کنید.")
        
        data = self.cleaned_data['purposed_price']
        
        cleaned = (
            str(data)
            .replace(',', '')
            .replace('تومان', '')
            .replace(' ', '')
            .strip()
        )

        try:
            price = int(cleaned)
        except ValueError:
            raise forms.ValidationError("قیمت وارد شده معتبر نیست.")
        # بررسی تمام موضوعات انتخاب شده
        for topic in topics:
            min_price = topic.min_price
            if min_price and price < min_price:
                raise forms.ValidationError(
                    f"حداقل قیمت برای موضوع '{topic.name}' مبلغ {min_price:,} تومان است."
                )

        return price



class ParticipateCampaignForm(forms.ModelForm):
    proposal_price = forms.CharField(
        label='قیمت پیشنهادی',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_proposal_price',
            'placeholder': 'مثلاً 10.000.000 تومان',
            'required': True,
        })
    )
    class Meta:
        model = CampaignTransaction
        fields = ['proposals', 'proposal_price']
        widgets = {
            'proposals': forms.Textarea(
                attrs={'class': 'form-control',
                       'style': 'margin-bottom: 10px;',
                       'rows': 6, 
                       'placeholder': 'طرح خود را ارائه کنید...', 
                       'required': True}
                ),
            }
        
    def clean_proposal_price(self):
        data = self.cleaned_data['proposal_price']
        
        cleaned = (
            str(data)
            .replace(',', '')
            .replace('تومان', '')
            .replace(' ', '')
            .strip()
        )

        try:
            price = int(cleaned)
        except ValueError:
            raise forms.ValidationError("قیمت وارد شده معتبر نیست.")

        return price


# New specialized forms

class EnvironmentalAdvertisementForm(forms.ModelForm):
    class Meta:
        model = EnvironmentalAdvertisement
        exclude = ['campaign', 'proposed_user', 'created_at', 'modified_at']
        widgets = {
            'service_area': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'available_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiration_date': forms.NumberInput(attrs={'class': 'form-control'}),
            'media_type': forms.Select(attrs={'class': 'form-control'}),
            'media_width': forms.NumberInput(attrs={'class': 'form-control'}),
            'media_height': forms.NumberInput(attrs={'class': 'form-control'}),
            'proposal_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            # مخفی کردن مختصات برای پرشدن با نقشه
            'media_location_latitude': forms.HiddenInput(),
            'media_location_longitude': forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('media_location_latitude')
        lon = cleaned.get('media_location_longitude')
        if lat in [None, ''] or lon in [None, '']:
            raise ValidationError("لطفاً موقعیت رسانه را روی نقشه انتخاب کنید.")
        try:
            lat = float(lat); lon = float(lon)
        except (TypeError, ValueError):
            raise ValidationError("مختصات واردشده نامعتبر است.")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValidationError("مختصات خارج از محدوده معتبر است.")
        return cleaned


class SocialmediaAdvertisementForm(forms.ModelForm):
    class Meta:
        model = SocialmediaAdvertisement
        exclude = ['campaign', 'proposed_user', 'created_at', 'modified_at']
        widgets = {
            'content_categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'proposed_ad_template': forms.Select(attrs={'class': 'form-control'}),
            'start_execution_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_execution_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content_categories'].queryset = ContentCategory.objects.all()


class DigitalAdvertisementForm(forms.ModelForm):
    class Meta:
        model = DigitalAdvertisement
        exclude = ['campaign', 'proposed_user', 'created_at', 'modified_at']
        widgets = {
            'proposed_platform': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'digital_ad_type': forms.Select(attrs={'class': 'form-control'}),
            'targeting_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proposed_platform'].queryset = Platform.objects.all()


class PrintingAdvertisementForm(forms.ModelForm):
    class Meta:
        model = PrintingAdvertisement
        exclude = ['campaign', 'proposed_user', 'created_at', 'modified_at']
        widgets = {
            'printing_ad_type': forms.Select(attrs={'class': 'form-control'}),
            'paper_weight_and_type': forms.TextInput(attrs={'class': 'form-control'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_proposal_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'circulation': forms.NumberInput(attrs={'class': 'form-control'}),
            'graphic_design_included': forms.CheckboxInput(),
        }


class EventMarketingAdvertisementForm(forms.ModelForm):
    class Meta:
        model = EventMarketingAdvertisement
        exclude = ['campaign', 'proposed_user', 'created_at', 'modified_at']
        widgets = {
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'location_address': forms.TextInput(attrs={'class': 'form-control'}),
            'event_proposed_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'event_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'total_proposal_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }




