from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView
from account.forms import PortfolioEditForm, PortfolioImageFormSet, ProfileForm
from account.mixins import (
                            ContextsMixin, 
                            DealerUserMixin, 
                            PortfolioDeleteMixin, 
                            PortfolioEditMixin
                            )
from advplatform.models import CustomUser, Portfolio
from django.contrib.auth import logout



'''
TODO:
    1- is_active check for users
    2- is_active check for campaigns
    3- is_active check for portfolios

'''


class CustomLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('adv:home')


class AccountView(LoginRequiredMixin, ContextsMixin,TemplateView):
    
    template_name = 'account/index.html'
    
    
class PortfolioListView(LoginRequiredMixin, DealerUserMixin, TemplateView):
    
    template_name = 'account/portfolio/portfolioslist.html'

    def handle_no_permission(self):
        return render(self.request, '403.html', 
                          {'error_message': "شما به صفحه نمونه کار دسترسی ندارید"})  # یا HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['portfolios'] = Portfolio.objects.all()
        else:
            context['portfolios'] = Portfolio.objects.filter(dealer=self.request.user)
        return context
    

class PortfolioCreateView(LoginRequiredMixin, DealerUserMixin, CreateView):
    model = Portfolio
    form_class = PortfolioEditForm
    template_name = 'account/portfolio/portfoliocreate.html'

    def handle_no_permission(self):
        return render(
            self.request,
            '403.html',
            {'error_message': "شما به صفحه ایجاد نمونه کار دسترسی ندارید"},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = PortfolioImageFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context['image_formset'] = PortfolioImageFormSet()
        return context

    def form_valid(self, form):
        # تنظیم فیلد dealer برای کاربران نوع 'dealer'
        if self.request.user.user_type == 'dealer':
            form.instance.dealer = self.request.user

        # ذخیره‌ی نمونه اصلی
        response = super().form_valid(form)

        # مدیریت فرمت تصاویر
        context = self.get_context_data()
        image_formset = context['image_formset']
        if image_formset.is_valid():
            # تنظیم ارتباط تصاویر با نمونه ایجادشده
            image_formset.instance = self.object
            image_formset.save()
        else:
            # اگر فرمست معتبر نبود، خطا بازگردانده شود
            return self.form_invalid(form)

        return response


class PortfolioEditView(LoginRequiredMixin, DealerUserMixin, PortfolioEditMixin, UpdateView):
    
    model = Portfolio
    form_class = PortfolioEditForm
    template_name = 'account/portfolio/portfolioedit.html'
    

    def handle_no_permission(self):
        return render(self.request, '403.html', 
                          {'error_message': "شما به صفحه ویرایش نمونه کار دسترسی ندارید"})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class PortfolioDeleteView(LoginRequiredMixin, DealerUserMixin, PortfolioDeleteMixin, DeleteView):
    
    model = Portfolio
    template_name = 'account/portfolio/portfolio_confirm_delete.html'
    success_url = reverse_lazy('account:portfolios')
    

    def handle_no_permission(self):
        return render(self.request, '403.html', 
                          {'error_message': "شما به صفحه حذف این نمونه کار دسترسی ندارید"})


class ProfileView(LoginRequiredMixin, UpdateView):
    
    model = CustomUser
    form_class = ProfileForm
    template_name = 'account/profile.html'
    success_url = reverse_lazy('account:profile')

    def handle_no_permission(self):
        return reverse_lazy('account:login')
    
    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.pk)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs