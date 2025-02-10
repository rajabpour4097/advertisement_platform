from django import forms
from advplatform.models import CustomUser, Portfolio, PortfolioImages
from django.forms import inlineformset_factory, modelformset_factory



        
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
            self.fields['cutomer_type'].disabled = True
            self.fields['customer_mentor'].disabled = True
            self.fields['is_active'].disabled = True
            self.fields['rank'].disabled = True
        if user.user_type != 'dealer' or user.is_staff:
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
        

class PortfolioImageForm(forms.ModelForm):
    class Meta:
        model = PortfolioImages
        fields = ['image'] 
        
        
PortfolioImageFormSet = modelformset_factory(
    PortfolioImages,
    form=PortfolioImageForm,
    extra=0,  
    can_delete=True,  # امکان حذف تصاویر
)

