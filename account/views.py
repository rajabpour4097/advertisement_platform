from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from account.models import EditingCampaign
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.db.models import Q
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView
from django.views.generic.edit import BaseUpdateView
from account.forms import (
                            CampaignCreateForm,
                            CampaignImageFormSet,
                            EditCampaignForm,
                            ParticipateCampaignForm,
                            PortfolioCreateForm,
                            PortfolioEditForm, 
                            PortfolioImageFormSet, 
                            ProfileForm,
                            ReviewCampaignForm, 
                            SignupForm,
                            StartCampaignForm
                            )
from account.mixins import (
                            CampaignUserMixin,
                            ContextsMixin,
                            CreateCampaignUserMixin,
                            CancelUserMixin,
                            DealerUserMixin,
                            EditCampaignUserMixin,
                            NotLoginedMixin, 
                            PortfolioDeleteMixin, 
                            PortfolioEditMixin,
                            StaffUserMixin
                            )
from advplatform.models import Campaign, CustomUser, Portfolio
from django.contrib.auth import logout



'''
TODO:
    1-Change Register HttpResponse template with render
    2-Change activate HttpResponse template with render

'''


class Register(NotLoginedMixin, CreateView):
    
    form_class = SignupForm
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        mail_subject = 'فعالسازی حساب کاربری'
        message = render_to_string('registration/activate_account.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.send()
        return HttpResponse('لینک فعالسازی برای ایمیل شما ارسال شد. <a href="/login">صفحه ورود</a>')
    

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # return redirect('home')
        return HttpResponse('اکانت شما با موفقیت فعال شد. برای ورود <a href="/login"> کلیک </a>کنید.')
    else:
        return HttpResponse('لینک فعالسازی منقضی شده است.')


class PasswordChange(PasswordChangeView):
    
    template_name = 'account/password_change_form.html'
    success_url = reverse_lazy('account:password_change_done')
    

class PasswordChangeDone(PasswordChangeDoneView):
    
    template_name = 'account/password_change_done.html'
    

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
    form_class = PortfolioCreateForm
    template_name = 'account/portfolio/portfoliocreate.html'
    success_url = reverse_lazy('account:portfolios') 

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
        if self.request.user.user_type == 'dealer':
            form.instance.dealer = self.request.user  # اگر `dealer` باشد، مقدار را خودش بگیرد
        elif self.request.user.is_staff and not form.instance.dealer:
            form.instance.dealer = self.request.user  # اگر `is_staff` باشد و مقدار `dealer` در فرم خالی باشد

        if not form.instance.dealer:
            form.add_error('dealer', "فیلد مجری نمی‌تواند خالی باشد.")
            return self.form_invalid(form)

        self.object = form.save()

        # ذخیره‌سازی تصاویر
        context = self.get_context_data()
        image_formset = context['image_formset']
        if image_formset.is_valid():
            image_formset.instance = self.object
            image_formset.save()
        else:
            # اگر فرم‌ست تصاویر معتبر نباشد، خطا برگردانید
            return self.form_invalid(form)

        return super().form_valid(form)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = PortfolioImageFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context['image_formset'] = PortfolioImageFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']
        
        self.object = form.save()
    
        if image_formset.is_valid():
            image_formset.instance = self.object
            image_formset.save()
        else:
            print("خطاهای FormSet:", image_formset.errors)
            return self.form_invalid(form)
    
        return super().form_valid(form)
    
    def form_invalid(self, form):
        context = self.get_context_data()
        image_formset = context['image_formset']

        print("فرم اصلی نامعتبر است. خطاها:", form.errors)

        if image_formset:
            print("FormSet نامعتبر است. خطاها:", image_formset.errors)

        return super().form_invalid(form)

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


class CampaignListView(LoginRequiredMixin, CampaignUserMixin, TemplateView):
    
    template_name = 'account/campaign/campaignslist.html'

    def handle_no_permission(self):
        return render(self.request, '403.html', 
                          {'error_message': "شما به صفحه کمپین ها دسترسی ندارید"})  # یا HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['campaigns'] = Campaign.objects.all()
        elif self.request.user.user_type == 'dealer':
            dealer = self.request.user
            context['campaigns'] = Campaign.objects.filter(
                        Q(status='progressing') | 
                        Q(Q(list_of_participants=dealer) | Q(campaign_dealer=dealer))).distinct()

        elif self.request.user.user_type == 'customer':
            context['campaigns'] = Campaign.objects.filter(customer=self.request.user)
        return context
    

class CampaignCreateView(CreateCampaignUserMixin, CreateView):
    model = Campaign
    form_class = CampaignCreateForm
    template_name = 'account/campaign/campaigncreate.html'
    success_url = reverse_lazy('account:campaigns') 

    def handle_no_permission(self):
        return render(
            self.request,
            '403.html',
            {'error_message': "شما به صفحه ایجاد کمپین دسترسی ندارید"},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = CampaignImageFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context['image_formset'] = CampaignImageFormSet()
        return context

    def form_valid(self, form):
        if self.request.user.user_type == 'customer':
            form.instance.customer = self.request.user 
        elif self.request.user.is_staff and not form.instance.customer:
            form.instance.customer = self.request.user

        if not form.instance.customer:
            form.add_error('customer', "فیلد مشتری نمی‌تواند خالی باشد.")
            return self.form_invalid(form)

        self.object = form.save()

        # ذخیره‌سازی تصاویر
        context = self.get_context_data()
        image_formset = context['image_formset']
        if image_formset.is_valid():
            image_formset.instance = self.object
            image_formset.save()
        else:
            # اگر فرم‌ست تصاویر معتبر نباشد، خطا برگردانید
            return self.form_invalid(form)

        return super().form_valid(form)


class CampaignDeleteView(LoginRequiredMixin, StaffUserMixin, DeleteView):
    
    model = Campaign
    template_name = 'account/campaign/campaign_delete_confirm.html'
    success_url = reverse_lazy('account:campaigns')
    

    def handle_no_permission(self):
        return render(self.request, '403.html', 
                          {'error_message': "شما به صفحه حذف کمپین دسترسی ندارید"})


class CampaignDeactivateView(StaffUserMixin, View):
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        campaign.is_active = False
        campaign.save()
        return HttpResponseRedirect(reverse_lazy('account:campaigns'))

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    

class CampaignActivateView(StaffUserMixin, View):
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        campaign.is_active = True
        campaign.save()
        return HttpResponseRedirect(reverse_lazy('account:campaigns'))

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    

class CampaignCancelView(CancelUserMixin, View):
    template_name = "account/campaign/campaign_cancel_confirm.html"  

    def get(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'campaign': campaign})

    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        campaign.status = 'cancel'
        campaign.save()
        return HttpResponseRedirect(reverse_lazy('account:campaigns'))


class CampaignReviewView(StaffUserMixin, View):
    template_name = "account/campaign/campaign_review.html"
    
    def dispatch(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, id=kwargs['pk'])
        if campaign.is_active:
            return render(self.request, '403.html', 
                          {'error_message': "این کمپین در مرحله تایید مدیریت نمیباشد.",
                               'back_url': "account:campaigns"},
                          )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        editings = campaign.editings.all() 
        form1 = ReviewCampaignForm()
        form2 = StartCampaignForm()
        return render(request, self.template_name, {
            'campaign': campaign,
            'form1': form1,
            'form2': form2,
            'editings': editings, 
        })
    
    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        form1 = ReviewCampaignForm(request.POST)
        form2 = StartCampaignForm(request.POST)

        editing_campaign = None  # مقداردهی اولیه برای جلوگیری از خطا

        if form1.is_valid():
            editing_campaign = form1.save(commit=False)
            editing_campaign.campaign = campaign
            editing_campaign.submitted_user = request.user
            editing_campaign.save()

            campaign.status = "editing"
            campaign.save()

            return redirect('account:campaigns')  

        elif form2.is_valid():
        # فقط starttimedate و endtimedate از فرم گرفته شوند
            campaign.starttimedate = form2.cleaned_data['starttimedate']
            campaign.endtimedate = form2.cleaned_data['endtimedate']
            campaign.is_active = True
            campaign.status = "progressing"
            campaign.save()  # ذخیره کمپین

            return redirect('account:campaigns')

        editings = campaign.editings.all()
        return render(request, self.template_name, {
            'campaign': campaign,
            'form1': form1,
            'form2': form2,
            'editings': editings,
        })

class CampaignEditView(EditCampaignUserMixin, View):
    template_name = "account/campaign/campaign_edit.html"

    def dispatch(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, id=kwargs['pk'])
        if campaign.is_active:
            return render(self.request, '403.html', 
                          {'error_message': "شما اجازه ویرایش این کمپین را ندارید.",
                               'back_url': "account:campaigns"},
                          )

        if campaign.status == "reviewing" and not request.user.is_staff:
            return render(self.request, '403.html', 
                          {'error_message': "فقط مدیران اجازه بررسی این کمپین را دارند.",
                               'back_url': "account:campaigns"},
                          )

        if campaign.status not in ["editing", "reviewing"]:
            return render(self.request, '403.html', 
                          {'error_message': "شما اجازه ویرایش این کمپین را ندارید.",
                               'back_url': "account:campaigns"},
                          )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        
        editing_campaign = EditingCampaign.objects.filter(campaign=campaign).all()
        
        form = EditCampaignForm(instance=campaign, user=request.user)

        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            'editing_campaign': editing_campaign,
        })

    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        
        form = EditCampaignForm(request.POST, instance=campaign, user=request.user)

        if form.is_valid():
            form.save()
            campaign.status = "reviewing"
            campaign.save()
            return redirect('account:campaigns')
        
        editing_campaign = get_object_or_404(EditingCampaign, campaign=campaign)
        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            'editing_campaign': editing_campaign,
        })


class CampaignParticipateView(DealerUserMixin, View):
    template_name = "account/campaign/campaign_participate.html"
    
    def dispatch(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, id=kwargs['pk'])
        
        if request.user in campaign.list_of_participants.all():
            return render(self.request, '403.html', 
                          {'error_message': "شما قبلاً به این کمپین پیوسته اید.",
                           'back_url': "account:campaigns"},
                          )
        
        if campaign.status != 'progressing':
            return render(self.request, '403.html', 
                          {'error_message': "این کمپین در مرحله برگزاری نمیباشد.",
                           'back_url': "account:campaigns"},
                          )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        proposal = campaign.running_campaign.filter(campaign=campaign) 
        form = ParticipateCampaignForm()
        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            'proposal': proposal, 
        })
    
    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        form = ParticipateCampaignForm(request.POST)
        print("Request POST Data:", request.POST)
        if form.is_valid():
            proposal_campaign = form.save(commit=False)
            proposal_campaign.campaign = campaign
            proposal_campaign.dealer = request.user
            proposal_campaign.save()

            campaign.list_of_participants.add(request.user)
            campaign.save()

            return redirect('account:campaigns')  

        proposal = campaign.running_campaign.filter(campaign=campaign)
        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            'editings': proposal,
        })
        
