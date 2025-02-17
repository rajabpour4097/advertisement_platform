from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from advplatform.forms import CustomAuthenticationForm
from advplatform.models import Campaign, CustomUser, Portfolio
from django.views.generic import TemplateView



current_time = timezone.now()


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subtitle'] = 'ورود به حساب کاربری'  # اضافه کردن subtitle به کانتکست
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
