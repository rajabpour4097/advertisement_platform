from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.urls import reverse, reverse_lazy
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from account.models import CampaignTransaction, EditingCampaign, RequestForMentor
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
                            CheckHaveRequestOrMentor,
                            ContextsMixin,
                            CreateCampaignUserMixin,
                            CancelUserMixin,
                            CustomerUserMixin,
                            DealerUserMixin,
                            EditCampaignUserMixin,
                            MentorUserMixin,
                            NotLoginedMixin, 
                            PortfolioDeleteMixin, 
                            PortfolioEditMixin,
                            StaffUserMixin
                            )
from advplatform.models import Campaign, CustomUser, Portfolio, UsersImages
from django.contrib.auth import logout
from notifications.models import Notification
from django.contrib.auth.decorators import login_required
from notifications.signals import notify
from django.utils import timezone




'''
TODO:
    1-Change Register HttpResponse template with render
    2-Change activate HttpResponse template with render

'''


staff_users = CustomUser.objects.filter(is_staff=True)
dealers = CustomUser.objects.filter(user_type='dealer')


class NotificationsView(LoginRequiredMixin, TemplateView):
    template_name = 'notifications/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = Notification.objects.filter(recipient=self.request.user).order_by('-timestamp')
        return context


class NotificationDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'notifications/detail.html'
    
    def get(self, request, *args, **kwargs):
        notification = get_object_or_404(Notification, pk=self.kwargs.get('pk'))

        # Check if the notification is for the requested user or if the user is staff
        if notification.recipient == request.user or request.user.is_staff:
            # Mark as read if the user has permission to view it
            notification.unread = False
            notification.save()
            
            return render(request, self.template_name, {'notification': notification})
        else:
            # If not authorized, return a 403 forbidden response
            return render(request, '403.html', {'error_message': 'شما به این اعلان دسترسی ندارید'})



class Register(NotLoginedMixin, CreateView):
    
    form_class = SignupForm
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        user = form.save(commit=False)

        if user.user_type == 'mentor':
            user.is_active = False
            message = "ثبت‌نام شما به عنوان مشاور انجام شد. لطفاً منتظر تأیید مدیریت باشید."
        else:
            user.is_active = True
            message = "ثبت‌نام شما با موفقیت انجام شد! حالا می‌توانید وارد شوید."

        user.username = user.email
        user.save()

        self.request.session['signup_success'] = True
        self.request.session['signup_message'] = message
        
        success_url = reverse('signup_success') + f"?message={message}"
    
        # current_site = get_current_site(self.request)
        # mail_subject = 'فعالسازی حساب کاربری'
        # message = render_to_string('registration/activate_account.html', {
        #     'user': user,
        #     'domain': current_site.domain,
        #     'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        #     'token':account_activation_token.make_token(user),
        # })
        # to_email = form.cleaned_data.get('email')
        # email = EmailMessage(
        #             mail_subject, message, to=[to_email]
        # )
        # email.send()
        # return HttpResponse('لینک فعالسازی برای ایمیل شما ارسال شد. <a href="/login">صفحه ورود</a>')
        
        return redirect(success_url)


class SignupSuccessView(TemplateView):
    template_name = "registration/signup_success.html"

    def get(self, request, *args, **kwargs):
        if not request.session.get('signup_success', False):
            return redirect('adv:login')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = self.request.session.get("signup_message", "عملیات انجام شد!")

        del self.request.session['signup_success']
        del self.request.session['signup_message']
        
        return context


#Activate with email
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
            form.instance.dealer = self.request.user 
        elif self.request.user.is_staff and not form.instance.dealer:
            form.instance.dealer = self.request.user

        if not form.instance.dealer:
            form.add_error('dealer', "فیلد مجری نمی‌تواند خالی باشد.")
            return self.form_invalid(form)

        context = self.get_context_data()
        image_formset = context['image_formset']

        if not image_formset.is_valid():
            return self.form_invalid(form)

        # بررسی اینکه حداقل یک تصویر انتخاب شده باشد
        has_image = any(bool(f.cleaned_data.get('image')) for f in image_formset if not f.cleaned_data.get('DELETE'))
        if not has_image:
            form.add_error(None, "افزودن حداقل یک تصویر الزامی است.")
            return self.form_invalid(form)

        self.object = form.save()

        image_formset.instance = self.object
        image_formset.save()

        return super().form_valid(form)


class PortfolioEditView(LoginRequiredMixin, DealerUserMixin, PortfolioEditMixin, UpdateView):
    model = Portfolio
    form_class = PortfolioEditForm
    template_name = 'account/portfolio/portfolioedit.html'
    success_url = reverse_lazy('account:portfolios') 
    

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
        # Send notification after edit portfolio
        response = super().form_valid(form)

        notify.send(
                    self.request.user, 
                    recipient=self.object.dealer, 
                    timestamp=timezone.now(), 
                    verb=f"ویرایش نمونه کار", 
                    description=self.object.subject,
                    target=self.object
                    )

        return response
    

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
    
    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # ذخیره تصویر جدید در مدل UsersImages
        profile_image = self.request.FILES.get('profile_image')
        if profile_image:
            # بررسی برای حذف تصویر قدیمی (در صورت وجود)
            user_images = UsersImages.objects.filter(customer=self.request.user)
            if user_images.exists():
                user_images.first().delete()  # حذف تصویر قدیمی
            # ذخیره تصویر جدید
            UsersImages.objects.create(customer=self.request.user, image=profile_image)

        return response
    

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
        
        # Send notification to user created campaign
        notify.send(
                    self.request.user,
                    recipient=form.instance.customer,
                    verb="ایجاد کمپین جدید",
                    description=f"کمپین جدید با عنوان '{self.object.get_describe_summrize()}' توسط شما ایجاد شد.",
                    target=self.object, 
                    timestamp=timezone.now(), 
                    )
        # Send notification to all staff users
        for staff in staff_users:
                notify.send(
                    self.request.user, 
                    recipient=staff, 
                    verb="ایجاد کمپین جدید", 
                    description=f"کمپین جدید با عنوان '{self.object.get_describe_summrize()}' توسط {self.request.user.get_full_name()} ایجاد شد.", 
                    target=self.object, 
                    timestamp=timezone.now()
                )
        
        context = self.get_context_data()
        image_formset = context['image_formset']
        if image_formset.is_valid():
            image_formset.instance = self.object
            image_formset.save()
        else:
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
            
            campaign_customer = campaign.customer
            notification_message = f"کمپین '{campaign.get_describe_summrize()}'  شروع شده است."
            notification_message2 = f"کمپین '{campaign.get_describe_summrize()}' توسط کاربر '{campaign_customer.get_full_name()}' شروع شده است."
            
            #Send notification to campaign created user
            notify.send(
                        request.user, 
                        recipient=campaign_customer, 
                        verb="برگزاری کمپین", 
                        description=notification_message, 
                        target=campaign, 
                        timestamp=timezone.now()
                        )
            
            # Send notification to all dealer users
            for dealer in dealers:
                notify.send(
                            request.user, 
                            recipient=dealer, 
                            verb="برگزاری کمپین", 
                            description=notification_message2, 
                            target=campaign, 
                            timestamp=timezone.now()
                            )

            # Send notification to all staff users
            for staff in staff_users:
                notify.send(
                    request.user, 
                    recipient=staff, 
                    verb="برگزاری کمپین", 
                    description=notification_message2, 
                    target=campaign, 
                    timestamp=timezone.now()
                )
                
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
        

class CampaignCancelParticipateView(DealerUserMixin, View):
    template_name = 'account/campaign/campaign_cancel_participate_confirm.html'
    
    def get(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'campaign': campaign})
    
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        user = request.user
        
        # Check campaign status
        if campaign.status != 'progressing':
            messages.error(request, "امکان خروج از کمپین در این وضعیت وجود ندارد.")
            return HttpResponseRedirect(reverse_lazy('account:campaigns'))
        
        transaction = CampaignTransaction.objects.filter(dealer=user, campaign=campaign).first()

        # Remove from participate list
        if request.user in campaign.list_of_participants.all():
            if transaction:
                transaction.delete()
            campaign.list_of_participants.remove(request.user)
            messages.success(request, "شما با موفقیت از کمپین خارج شدید.")
        else:
            messages.warning(request, "شما در این کمپین عضو نبودید.")

        return HttpResponseRedirect(reverse_lazy('account:campaigns'))


class MentorUsersList(MentorUserMixin, TemplateView):
    
    template_name = 'account/mentor/mentoruserslist.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mentor = self.request.user
        context['users'] = CustomUser.objects.filter(customer_mentor=mentor)
    
        return context


class MyMentor(CustomerUserMixin, TemplateView):
    
    template_name = 'account/mentor/mymentor.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if RequestForMentor.objects.filter(requested_user=user, status='pending').exists():
            context['user_last_request'] = RequestForMentor.objects.get(requested_user=user, status='pending')
        
        context['user'] = CustomUser.objects.get(pk=user.pk)
    
        return context

   
class MentorsList(CreateCampaignUserMixin, CheckHaveRequestOrMentor, TemplateView):
    
    template_name = 'account/mentor/mentorslist.html'
 
    def get_context_data(self, **kwargs):
        print(self.request.user.is_staff)
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['mentors'] = CustomUser.objects.filter(user_type='mentor')
        else:    
            context['mentors'] = CustomUser.objects.filter(user_type='mentor', is_active=True)
    
        return context
    

class MentorChooseView(CustomerUserMixin, CheckHaveRequestOrMentor, View):
    
    template_name = "account/mentor/mentor_choose_confirm.html"  
    
    def get(self, request, *args, **kwargs):
        mentor = get_object_or_404(CustomUser, pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'mentor': mentor})
    
    def post(self, request, *args, **kwargs):
        mentor = get_object_or_404(CustomUser, pk=self.kwargs.get('pk'))
        user = request.user
        
        request_for_mentor = RequestForMentor.objects.create(
            requested_user=user,
            mentor=mentor
        )
        
        return redirect('account:mymentor')


class ListOfRequestForMentor(StaffUserMixin, TemplateView):
    
    template_name = "account/mentor/requestformentor.html"  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = RequestForMentor.objects.all()
    
        return context


class ChangeStatusRequestForMentor(StaffUserMixin, View):
    def post(self, request, request_id, *args, **kwargs):
        request_for_mentor = get_object_or_404(RequestForMentor, pk=request_id)
        
        requested_user_id = request.POST.get('requested_user_id')
        mentor_id = request.POST.get('mentor_id')
        status = request.POST.get('status')

        if status =='reject': 
            request_for_mentor.status = status
            request_for_mentor.save()
        elif status == 'approved':
            requested_user = get_object_or_404(CustomUser, pk=requested_user_id)
            mentor = get_object_or_404(CustomUser, pk=mentor_id)
            request_for_mentor.status = status
            request_for_mentor.save()
            requested_user.customer_mentor = mentor
            requested_user.save()
            
        
        return HttpResponseRedirect(reverse_lazy('account:listofrequestformentor'))

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    

class NewMentorActivate(StaffUserMixin, View):
    
    template_name = "account/activatenewmentor.html"  
    
    def get(self, request, *args, **kwargs):
        mentor = get_object_or_404(CustomUser, pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'mentor': mentor})

    def post(self, request, *args, **kwargs):
        mentor = get_object_or_404(CustomUser, pk=self.kwargs.get('pk'))
        mentor.is_active = True
        mentor.save()
        return redirect('account:mentorslist')
        