from django import forms
from advplatform.choices_type import USER_TYPE
from advplatform.models import Campaign, CampaignImages, CustomUser, Portfolio, PortfolioImages
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from account.models import CampaignTransaction, EditingCampaign




class SignupForm(UserCreationForm):
        
    user_type = forms.ChoiceField(choices=USER_TYPE, required=True)
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type')
        
        
class ProfileForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['is_active'].help_text = None
        if not user.is_staff:
            self.fields['username'].disabled = True
            self.fields['email'].disabled = True
            self.fields['user_type'].disabled = True
            self.fields['customer_mentor'].disabled = True
            self.fields['is_active'].disabled = True
            self.fields['rank'].disabled = True
        if user.user_type != 'dealer' and user.user_type != 'mentor' or user.is_staff:
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
                'customer_mentor',# /for Customer
                'is_active',#/
            ]


class PortfolioEditForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user.user_type == 'dealer':
            self.fields.pop('dealer', None)
            
    class Meta:
        model = Portfolio
        fields = '__all__'
        

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
    can_delete=True
)


class CampaignCreateForm(forms.ModelForm):
    
    class Meta:
        model = Campaign
        fields = [
                  'customer',
                  'topic', 
                  'describe', 
                  'purposed_price',
                  'starttimedate', 
                  'endtimedate'
                  ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if not user.is_staff and user.user_type == 'customer':
            self.fields['customer'].initial = user
            self.fields['customer'].widget = forms.HiddenInput()
            self.fields['starttimedate'].widget = forms.HiddenInput()
            self.fields['endtimedate'].widget = forms.HiddenInput()
            

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
    class Meta:
        model = Campaign
        fields = ['starttimedate', 'endtimedate']
        


class EditCampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['topic', 'describe', 'purposed_price', 'starttimedate', 'endtimedate']
        widgets = {
            'describe': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'starttimedate': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'endtimedate': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user.user_type == 'customer':
            self.fields.pop('starttimedate', None)
            self.fields.pop('endtimedate', None)
            

class ParticipateCampaignForm(forms.ModelForm):
    class Meta:
        model = CampaignTransaction
        fields = ['proposals', 'proposal_price']
        widgets = {
            'proposals': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'طرح خود را ارائه کنید...'}
                ),
            }