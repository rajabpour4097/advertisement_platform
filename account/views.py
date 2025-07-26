from datetime import timedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, LoginView
from django.urls import reverse, reverse_lazy
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from account.models import CampaignTransaction, EditingCampaign, RequestForMentor
from wallet.models import Wallet, Transaction
from .tokens import account_activation_token
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from django.db.models import Q, Count
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView, ListView
from django.views.generic.edit import BaseUpdateView
from account.forms import (
                            AssignMentorForm,
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
                            CustomerUserMixin,
                            DealerUserMixin,
                            EditCampaignUserMixin,
                            ManagerUserMixin,
                            MentorUserMixin,
                            NotLoginedMixin, 
                            PortfolioDeleteMixin, 
                            PortfolioEditMixin,
                            StaffUserMixin
                            )
from advplatform.models import Campaign, CustomUser, Portfolio, UsersImages, Topic
from django.contrib.auth import logout
from notifications.models import Notification
from django.contrib.auth.decorators import login_required
from notifications.signals import notify
from django.utils import timezone
from .utils.send_notification import notify_campaign_actions, notify_campaign_mentor_assignment, notify_campaign_participation, notify_campaign_winner, notify_mentor_activation, notify_mentor_request, notify_mentor_request_status, notify_profile_update, notify_portfolio_actions, notify_user_registration, notify_password_change
from .utils.send_sms import send_activation_sms, send_campaign_winner_sms, verify_otp, send_campaign_confirmation_sms, send_campaign_review_sms, send_campaign_start_sms, send_campaign_mentor_assignment_sms
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator





'''
TODO:

'''


staff_users = CustomUser.objects.filter(is_staff=True)
dealers = CustomUser.objects.filter(user_type='dealer')
am_users = CustomUser.objects.filter(is_am=True)


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
        user.is_active = False
        user.username = user.email
        user.save()
        notify_user_registration(user, staff_users)

        
        # ارسال کد فعال‌سازی
        response, otp, error = send_activation_sms(user)
        if response:
            # ذخیره اطلاعات موردنیاز در session
            self.request.session['user_id'] = user.id
            self.request.session['phone_number'] = user.phone_number
            message = "کد تایید برای شماره موبایل شما ارسال شد."
            return redirect('verify_otp')
        else:
            form.add_error(None, f"خطا در ارسال پیامک: {error}")
            return self.form_invalid(form)


class VerifyOTP(View):
    template_name = 'registration/verify_otp.html'

    def get(self, request):
        if not request.session.get('user_id'):
            messages.error(request, 'دسترسی نامعتبر')
            return redirect('login')
        return render(request, self.template_name)

    def post(self, request):
        otp = request.POST.get('otp')
        phone_number = request.session.get('phone_number')
        user_id = request.session.get('user_id')

        if not all([otp, phone_number, user_id]):
            messages.error(request, 'اطلاعات نامعتبر است.')
            return redirect('login')

        if verify_otp(phone_number, otp):
            # فعال کردن کاربر
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            # پاک کردن اطلاعات session
            del request.session['user_id']
            del request.session['phone_number']

            messages.success(request, 'حساب کاربری شما با موفقیت فعال شد.')
            return redirect('adv:login')
        else:
            messages.error(request, 'کد وارد شده نامعتبر است.')
            return render(request, self.template_name)

@method_decorator(require_POST, name='dispatch')
class ResendOTPView(View):
    def post(self, request): 
        user_id = request.session.get('user_id')
        if not user_id:

            return JsonResponse({'success': False, 'error': 'کاربر نامعتبر'})

        try:
            user = CustomUser.objects.get(id=user_id)
            response, otp, error = send_activation_sms(user)
            
            if response:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': error})
                
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'کاربر یافت نشد'})


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
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Send notification to user
        notify_password_change(self.request.user)
        
        return response


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
        if self.request.user.is_staff or self.request.user.is_am:
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
        elif self.request.user.is_staff or self.request.user.is_am and not form.instance.dealer:
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
        
        notify_portfolio_actions(self.request.user, self.object, 'create', staff_users, am_users)

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

        notify_portfolio_actions(self.request.user, self.object, 'edit', staff_users, am_users)

        return response
    

class PortfolioDeleteView(LoginRequiredMixin, DealerUserMixin, PortfolioDeleteMixin, DeleteView):
    model = Portfolio
    template_name = 'account/portfolio/portfolio_confirm_delete.html'
    success_url = reverse_lazy('account:portfolios')

    def handle_no_permission(self):
        return render(self.request, '403.html', 
                          {'error_message': "شما به صفحه حذف این نمونه کار دسترسی ندارید"})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()

        # Send notification to dealer
        notify_portfolio_actions(request.user, self.object, 'delete', staff_users, am_users)

        return HttpResponseRedirect(success_url)


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
        
        notify_profile_update(self.request.user, staff_users)

        return response
    

class CampaignListView(LoginRequiredMixin, CampaignUserMixin, TemplateView):
    
    template_name = 'account/campaign/campaignslist.html'

    def handle_no_permission(self):
        return render(self.request, '403.html', 
                          {'error_message': "شما به صفحه کمپین ها دسترسی ندارید"})  # یا HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff or self.request.user.is_am:
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
        # Add topic count to each topic
        context['form'].fields['topic'].queryset = Topic.objects.annotate(
            campaign_count=Count('topics')
        )
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
        
        context = self.get_context_data()
        image_formset = context['image_formset']
        if image_formset.is_valid():
            image_formset.instance = self.object
            image_formset.save()
        else:
            return self.form_invalid(form)

        # تغییر مسیر به صفحه انتخاب منتور
        return redirect('account:confirm_mentor', pk=self.object.pk)  # به جای redirect به پرداخت


class CampaignConfirmMentorView(LoginRequiredMixin, View):
    template_name = 'account/campaign/confirm_mentor.html'

    def dispatch(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=kwargs.get('pk'))
        
        # اگر کمپین قبلاً تأیید شده باشد (needs_mentor مقدار دارد)
        if campaign.needs_mentor is not None:
            messages.error(request, "این کمپین قبلاً تأیید شده است.")
            return redirect('account:campaigns')
            
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        return render(request, self.template_name, {'campaign': campaign})

    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        needs_mentor = request.POST.get('needs_mentor') == 'yes'
        
        campaign.needs_mentor = needs_mentor
        campaign.save()

        # ارسال اعلان و پیامک
        notify_campaign_actions(request.user, campaign, 'create', staff_users, am_users)
        success, error = send_campaign_confirmation_sms(campaign, needs_mentor)
        if not success:
            print(f"Error in sending SMS: {error}")
            messages.warning(request, f"خطا در ارسال پیامک: {error}")

        # هدایت به صفحه پرداخت
        return redirect('wallet:campaign_payment', campaign_id=campaign.pk)


class CampaignDeleteView(LoginRequiredMixin, ManagerUserMixin, DeleteView):
    
    model = Campaign
    template_name = 'account/campaign/campaign_delete_confirm.html'
    success_url = reverse_lazy('account:campaigns')
    

    def handle_no_permission(self):
        return render(self.request, '403.html', 
                          {'error_message': "شما به صفحه حذف کمپین دسترسی ندارید"})
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Send notifications before deletion
        notify_campaign_actions(request.user, self.object, 'delete', staff_users, am_users)
        
        # Delete the object
        success_url = self.get_success_url()
        self.object.delete()

        return HttpResponseRedirect(success_url)


class CampaignDeactivateView(ManagerUserMixin, View):
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        
        # Send notifications before status change
        notify_campaign_actions(request.user, campaign, 'deactivate', staff_users, am_users)

        campaign.is_active = False
        campaign.save()
        return HttpResponseRedirect(reverse_lazy('account:campaigns'))

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    

class CampaignActivateView(ManagerUserMixin, View):
    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        
        # Send notifications before status change
        notify_campaign_actions(request.user, campaign, 'activate', staff_users, am_users)

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
        
        # Send notifications before status change
        notify_campaign_actions(request.user, campaign, 'cancel', staff_users, am_users)
        
        campaign.status = 'cancel'
        campaign.save()
        return HttpResponseRedirect(reverse_lazy('account:campaigns'))


class CampaignReviewView(ManagerUserMixin, View):  #This view is used for Staff
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
        form3 = AssignMentorForm()
        return render(request, self.template_name, {
            'campaign': campaign,
            'form1': form1,
            'form2': form2,
            'form3': form3,
            'editings': editings, 
        })
    
    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        form1 = ReviewCampaignForm(request.POST)
        form2 = StartCampaignForm(request.POST)
        form3 = AssignMentorForm(request.POST)
        form_type = request.POST.get('form_type')
        editing_campaign = None  # مقداردهی اولیه برای جلوگیری از خطا

        if form1.is_valid():
            editing_campaign = form1.save(commit=False)
            editing_campaign.campaign = campaign
            editing_campaign.submitted_user = request.user
            editing_campaign.save()

            campaign.status = "editing"
            campaign.save()
            
            # Send notifications for editing status
            notify_campaign_actions(
                user=request.user,
                campaign=campaign,
                action_type='editing',
                staff_users=staff_users,
                am_users=am_users
            )
            
            # ارسال پیامک به کاربر
            success, error = send_campaign_review_sms(campaign, editing_campaign)
            if not success:
                print(f"Error in sending review SMS: {error}")
                messages.warning(request, f"خطا در ارسال پیامک: {error}")

            return redirect('account:campaigns')  

        elif form_type == 'start' and form2.is_valid():
            # فقط starttimedate و endtimedate از فرم گرفته شوند
            campaign.starttimedate = form2.cleaned_data['starttimedate']
            campaign.endtimedate = form2.cleaned_data['endtimedate']
            campaign.is_active = True
            campaign.status = "progressing"
            
            #Send notification
            notify_campaign_actions(
                user=request.user,
                campaign=campaign,
                action_type='progressing',
                staff_users=staff_users,
                am_users=am_users,
                dealers=dealers  # Pass dealers to notify them
            )
            
            # ارسال پیامک به کاربر و دیلرها
            success, error = send_campaign_start_sms(campaign)
            if not success:
                print(f"Error in sending start campaign SMS: {error}")
                messages.warning(request, f"خطا در ارسال پیامک: {error}")
            
            campaign.save()  # ذخیره کمپین

            return redirect('account:campaigns')
        
        elif form_type == 'mentor' and form3.is_valid():
            campaign.assigned_mentor = form3.cleaned_data['assigned_mentor']
            campaign.is_active = False
            campaign.status = "reviewing"
            
            # ارسال نوتیفیکیشن
            notify_campaign_mentor_assignment(
                campaign,
                campaign.assigned_mentor,
                staff_users, 
                am_users, 
                request_user=request.user
            )
            
            # ارسال پیامک به کاربر
            success, error = send_campaign_mentor_assignment_sms(campaign)
            if not success:
                print(f"Error in sending mentor assignment SMS: {error}")
                messages.warning(request, f"خطا در ارسال پیامک: {error}")
            
            campaign.save()
            return redirect('account:campaigns')

        editings = campaign.editings.all()
        return render(request, self.template_name, {
            'campaign': campaign,
            'form1': form1,
            'form2': form2,
            'form3': form3,
            'editings': editings,
        })
        

class CampaignEditView(EditCampaignUserMixin, View):
    template_name = "account/campaign/campaign_edit.html"

    def get(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        editing_campaign = EditingCampaign.objects.filter(campaign=campaign).all()
        form = EditCampaignForm(instance=campaign, user=request.user)
        
        # Add image formset
        image_formset = CampaignImageFormSet(instance=campaign)

        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            'editing_campaign': editing_campaign,
            'image_formset': image_formset,
        })

    def post(self, request, pk):
        campaign = get_object_or_404(Campaign, id=pk)
        form = EditCampaignForm(request.POST, request.FILES, instance=campaign, user=request.user)
        image_formset = CampaignImageFormSet(request.POST, request.FILES, instance=campaign)

        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()
            campaign.status = "reviewing"
            
            # Send notifications for editing status
            notify_campaign_actions(
                user=request.user,
                campaign=campaign,
                action_type='review',
                staff_users=staff_users,
                am_users=am_users
            )
            
            campaign.save()
            return redirect('account:campaigns')
        
        editing_campaign = EditingCampaign.objects.filter(campaign=campaign).all()
        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            'editing_campaign': editing_campaign,
            'image_formset': image_formset,
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
        # proposal = campaign.running_campaign.filter(campaign=campaign) 
        form = ParticipateCampaignForm()
        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            # 'proposal': proposal, 
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
            
            # Send notifications
            notify_campaign_participation(
                user=request.user,
                campaign=campaign,
                action_type='participate',
                staff_users=staff_users,
                am_users=am_users
            )

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
            
            # Send notifications
            notify_campaign_participation(
                user=request.user,
                campaign=campaign,
                action_type='cancel',
                staff_users=staff_users,
                am_users=am_users
            )
            
            messages.success(request, "شما با موفقیت از کمپین خارج شدید.")
        else:
            messages.warning(request, "شما در این کمپین عضو نبودید.")

        return HttpResponseRedirect(reverse_lazy('account:campaigns'))
    

class CampaignEditProposalView(DealerUserMixin, View):
    template_name = 'account/campaign/campaign_edit_proposal.html'

    def get(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        proposal = get_object_or_404(CampaignTransaction, campaign=campaign, dealer=request.user)
        form = ParticipateCampaignForm(instance=proposal)
        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            'proposal': proposal
        })

    def post(self, request, *args, **kwargs):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        proposal = get_object_or_404(CampaignTransaction, campaign=campaign, dealer=request.user)
        form = ParticipateCampaignForm(request.POST, instance=proposal)
        if form.is_valid():
            form.save()
            return redirect('account:campaigns')
        
        return render(request, self.template_name, {
            'campaign': campaign,
            'form': form,
            'proposal': proposal
        })



class RunningCampaignParticipatedListView(ManagerUserMixin, ListView):
    template_name = 'account/campaign/running_campaign_participated_list.html'
    context_object_name = 'proposals'
    paginate_by = 8

    def get_queryset(self):
        campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        return campaign.running_campaign.filter(campaign=campaign).order_by('-created_at')
    

class FinishedCampaignProposalsListView(LoginRequiredMixin, EditCampaignUserMixin, ListView):
    template_name = 'account/campaign/finished_campaign_proposals_list.html'
    context_object_name = 'proposals'
    paginate_by = 8

    def get_queryset(self):
        self.campaign = get_object_or_404(Campaign, pk=self.kwargs.get('pk'))
        if self.campaign.status == 'finished' and not self.campaign.is_active:
            return CampaignTransaction.objects.filter(campaign=self.campaign)
        return CampaignTransaction.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.campaign
        return context
        

class SelectCampaignWinnerView(EditCampaignUserMixin, View):
    template_name = 'account/campaign/confirm_winner.html'

    def get(self, request, campaign_id, dealer_id):
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        dealer = get_object_or_404(CustomUser, pk=dealer_id)
        
        if campaign.campaign_dealer:
            messages.error(request, "برنده این کمپین قبلاً انتخاب شده است.")
            return redirect('account:finished_campaign_proposals', pk=campaign_id)
        elif not campaign.get_finished_proposals():
            messages.error(request, "زمان انتخاب برنده به پایان رسیده است.")
            return redirect('account:finished_campaign_proposals', pk=campaign_id)
        
        return render(request, self.template_name, {
            'campaign': campaign,
            'dealer': dealer
        })

    def post(self, request, campaign_id, dealer_id):
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        dealer = get_object_or_404(CustomUser, pk=dealer_id)

        # Set campaign winner
        campaign.campaign_dealer = dealer
        campaign.save()

        # Calculate and add gift to winner's wallet
        gift_amount = campaign.get_gift_price()
        wallet, _ = Wallet.objects.get_or_create(user=dealer)
        wallet.deposit(gift_amount)

        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=gift_amount,
            transaction_type='deposit',
            payment_method='wallet',
            status='completed',
            campaign=campaign,
            description=f"واریز جایزه برنده شدن در کمپین {campaign.id}",
            wallet_amount=gift_amount,
        )

        # Send notifications
        if request.user.is_staff or request.user.is_am:
            request_user = campaign.customer
        else:
            request_user = request.user
            
        notify_campaign_winner(campaign, dealer, request_user, staff_users, am_users)

        # Send SMS to winner
        success, error = send_campaign_winner_sms(campaign, dealer)
        if not success:
            messages.warning(request, f"خطا در ارسال پیامک: {error}")

        messages.success(request, "برنده کمپین با موفقیت انتخاب شد.")
        return redirect('account:campaigns')


class WinnedProposalDetail(EditCampaignUserMixin, View):
    template_name = 'account/campaign/show_winned_proposal_detail.html'

    def get(self, request, pk):
        campaign = get_object_or_404(Campaign, pk=pk)
        if campaign.campaign_dealer:
            propsal = get_object_or_404(CampaignTransaction, campaign=campaign,dealer=campaign.campaign_dealer)
                
            return render(request, self.template_name, {
                'proposal': propsal,
            })
            
        else:
            messages.error(request, "این کمپین برنده ای نداشته یا هنوز انتخاب نشده.")
            return redirect('account:campaigns')


class MentorUsersList(MentorUserMixin, TemplateView):
    
    template_name = 'account/mentor/mentoruserslist.html'
    

class MyMentor(CustomerUserMixin, TemplateView):
    
    template_name = 'account/mentor/mymentor.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if RequestForMentor.objects.filter(requested_user=user, status='pending').exists():
            context['user_last_request'] = RequestForMentor.objects.get(requested_user=user, status='pending')
        
        context['user'] = CustomUser.objects.get(pk=user.pk)
    
        return context

   
class MentorsList(ManagerUserMixin, TemplateView):
    
    template_name = 'account/mentor/mentorslist.html'
 
    def get_context_data(self, **kwargs):
        print(self.request.user.is_staff)
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_staff or self.request.user.is_am:
            context['mentors'] = CustomUser.objects.filter(user_type='mentor')
            
        return context
    

class MentorChooseView(CustomerUserMixin, View):
    
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
        
        notify_mentor_request(user, mentor, request_for_mentor, staff_users)
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
            notify
            
        elif status == 'approved':
            requested_user = get_object_or_404(CustomUser, pk=requested_user_id)
            mentor = get_object_or_404(CustomUser, pk=mentor_id)
            request_for_mentor.status = status
            request_for_mentor.save()
            requested_user.save()
            notify_mentor_request_status(request_for_mentor, status, request.user, staff_users)

        
        return HttpResponseRedirect(reverse_lazy('account:listofrequestformentor'))

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    

class NewMentorActivate(ManagerUserMixin, View):
    
    template_name = "account/activatenewmentor.html"  
    
    def get(self, request, *args, **kwargs):
        mentor = get_object_or_404(CustomUser, pk=self.kwargs.get('pk'))
        return render(request, self.template_name, {'mentor': mentor})

    def post(self, request, *args, **kwargs):
        mentor = get_object_or_404(CustomUser, pk=self.kwargs.get('pk'))
        mentor.is_active = True
        mentor.save()
        notify_mentor_activation(request.user, mentor, staff_users)
        
        return redirect('account:mentorslist')

