from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from advplatform.forms import CustomAuthenticationForm
from advplatform.models import Campaign, CustomUser, Portfolio
from django.views.generic import TemplateView
from account.utils.send_sms import send_activation_sms



current_time = timezone.now()

def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account:home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Check if user is active before login"""
        user = form.get_user()
        
        # اگر کاربر فعال نیست و مشاور هم نیست
        if not user.is_active and user.user_type != 'mentor':
            # ارسال مجدد کد تایید
            response, otp, error = send_activation_sms(user)
            if response:
                # ذخیره اطلاعات در session
                self.request.session['user_id'] = user.id
                self.request.session['phone_number'] = user.phone_number
                messages.warning(self.request, 'لطفا ابتدا شماره موبایل خود را تایید کنید.')
                return redirect('verify_otp')
            else:
                messages.error(self.request, f'خطا در ارسال کد تایید: {error}')
                return redirect('adv:login')
                
        return super().form_valid(form)

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        messages.error(self.request, 'نام کاربری یا رمز عبور اشتباه است.')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subtitle'] = 'ورود به حساب کاربری'
        return context


class ContactUs(TemplateView):
    template_name = 'advplatform/contactus.html'
    

class AboutUs(TemplateView):
    template_name = 'advplatform/aboutus.html'
    

def home_view(request):
    context = dict()
    # context['mentors'] = Mentor.objects.filter(is_active=True)
    context['campaigns'] = Campaign.objects.filter(
                                                    Q(status='progressing') &
                                                    Q(is_active=True) &
                                                    Q(endtimedate__isnull=False) & 
                                                    Q(endtimedate__gte=current_time)
                                                   )
    return render(request, 'index.html', context=context)

def mentors_list(request):
    context = dict()
    context['mentors'] = CustomUser.objects.filter(user_type='mentor', is_active=True)
    return render(request, 'advplatform/mentors.html', context=context)

def portfolios_list(request):
    context = dict()
    context['portfolios'] = Portfolio.objects.filter(is_active=True)
    return render(request, 'advplatform/portfolios.html', context=context)

def campaigns_list(request):
    context = dict()
    context['campaigns'] = Campaign.objects.filter(
                                                    Q(status='progressing') &
                                                    Q(is_active=True) &
                                                    Q(endtimedate__isnull=False) & 
                                                    Q(endtimedate__gte=current_time)
                                                   )
    return render(request, 'advplatform/campaigns.html', context=context)
