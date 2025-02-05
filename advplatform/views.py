from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from advplatform.forms import CustomAuthenticationForm
from advplatform.models import Campaign, Mentor, Portfolio




class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'login.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account:home') 
        return super().dispatch(request, *args, **kwargs)
    


def home_view(request):
    context = dict()
    context['mentors'] = Mentor.objects.filter(is_active=True)
    context['campaigns'] = Campaign.objects.filter(is_active=True)
    return render(request, 'index.html', context=context)

def about_us(request):
    return render(request, 'aboutus.html')

def contact_us(request):
    return render(request, 'contactus.html')

def signup_page(request):
    return render(request, 'advplatform/signup.html')

def mentors_list(request):
    context = dict()
    context['mentors'] = Mentor.objects.filter(is_active=True)
    return render(request, 'advplatform/mentors.html', context=context)

def portfolios_list(request):
    context = dict()
    context['portfolios'] = Portfolio.objects.filter(is_active=True)
    return render(request, 'advplatform/portfolios.html', context=context)
