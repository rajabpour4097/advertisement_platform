from django import forms
from advplatform.choices_type import USER_TYPE
from advplatform.models import Campaign, CampaignImages, CustomUser, Portfolio, PortfolioImages, Topic, UsersImages
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from account.models import CampaignTransaction, EditingCampaign
from django.utils import timezone



class SignupForm(UserCreationForm):
        
    user_type = forms.ChoiceField(choices=USER_TYPE, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2', 'user_type', 'phone_number', 'first_name', 'last_name')


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

