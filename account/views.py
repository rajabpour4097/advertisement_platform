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
from advplatform.forms import ResumeForm, ResumeReviewForm
from wallet.models import Wallet, Transaction
from .tokens import account_activation_token
from django.db.models import Q, Count
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView, ListView
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
from advplatform.models import Campaign, CustomUser, Portfolio, PortfolioImages, Resume, UsersImages, Topic, Province, City, Permission, WorkLink
from django.contrib.auth import logout
from notifications.models import Notification
from django.contrib.auth.decorators import login_required
from notifications.signals import notify
from django.utils import timezone
from .utils.send_notification import notify_campaign_actions, notify_campaign_mentor_assignment, notify_campaign_participation, notify_campaign_winner, notify_mentor_activation, notify_mentor_request, notify_mentor_request_status, notify_profile_update, notify_portfolio_actions, notify_user_registration, notify_password_change, notify_resume_review
from .utils.send_sms import send_activation_sms, send_campaign_winner_sms, verify_otp, send_campaign_confirmation_sms, send_campaign_review_sms, send_campaign_start_sms, send_campaign_mentor_assignment_sms, send_resume_review_sms
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.utils.dateparse import parse_date
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError





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
        context['form'].fields['topic'].queryset = Topic.objects.filter(parent__isnull=True).annotate(
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

        if not Resume.objects.filter(user=request.user, status='approved').exists():
            return render(self.request, '403.html',
                          {'error_message': "تا زمانی که رزومه ای ارسال نکرده اید و توسط مدیر بررسی و تایید نشده است، نمی توانید در هیچ کمپین شرکت کنید.",
                           'back_url': "account:campaigns"},
                          )

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


class ResumeReviewListView(ManagerUserMixin, ListView):
    model = Resume
    template_name = 'account/resumes/review_list.html'
    context_object_name = 'resumes'

    
class SubmitResumeView(DealerUserMixin, CreateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'account/resumes/submit.html'
    success_url = reverse_lazy('account:my_resume')  # ریدایرکت پس از ارسال موفق

    def form_valid(self, form):
        form.instance.user = self.request.user  # اتصال رزومه به کاربر جاری
        return super().form_valid(form)


class ResumeDetailView(ManagerUserMixin, UpdateView):
    model = Resume
    form_class = ResumeReviewForm
    template_name = 'account/resumes/detail.html'
    success_url = reverse_lazy('account:review_resumes')
    context_object_name = 'resume'

    def get_object(self, queryset=None):
        resume = get_object_or_404(Resume, id=self.kwargs['resume_id'])
        # تنها در صورت اولین مشاهده، وضعیت را تغییر دهید
        if not resume.is_seen_by_manager and resume.status == 'pending':
            resume.is_seen_by_manager = True
            resume.status = 'under_review'
            resume.save()
        return resume

    def form_valid(self, form):
        old_status = self.object.status
        response = super().form_valid(form)
        new_status = self.object.status
        
        # ارسال اعلان به کاربر در صورت تغییر وضعیت
        if old_status != new_status:
            # ارسال نوتیفیکیشن
            notify_resume_review(
                resume=self.object,
                reviewer=self.request.user,
                old_status=old_status,
                new_status=new_status
            )
            
            # ارسال پیامک
            try:
                success, error = send_resume_review_sms(self.object, new_status)
                if not success:
                    messages.warning(self.request, f"خطا در ارسال پیامک: {error}")
            except Exception as e:
                messages.warning(self.request, f"خطا در ارسال پیامک: {str(e)}")
            
            # پیام موفقیت
            status_messages = {
                'under_review': 'رزومه در حال بررسی قرار گرفت.',
                'needs_editing': 'درخواست ویرایش رزومه ارسال شد.',
                'approved': 'رزومه تایید شد.',
                'rejected': 'رزومه رد شد.'
            }
            
            messages.success(
                self.request, 
                status_messages.get(new_status, 'وضعیت رزومه تغییر کرد.')
            )
        
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resume'] = self.object
        
        # اضافه کردن اطلاعات مجوزها و لینک‌های کار
        context['permissions'] = self.object.permission_files.all()
        context['work_links'] = self.object.work_links.all()
        
        return context


class ResumeDeleteView(DealerUserMixin, DeleteView):
    model = Resume
    template_name = 'account/resumes/confirm_delete.html'
    success_url = reverse_lazy('account:review_resumes')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # دریافت نمونه رزومه
        if self.object.status == 'approved':
            messages.error(request, "این رزومه قبلاً توسط مدیر تایید شده و امکان حذف آن وجود ندارد.")
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)


class MyResumeView(DealerUserMixin, View):
    template_name = 'account/resumes/my_resume.html'

    def get(self, request):
        try:
            resume = Resume.objects.get(user=request.user)
            form = ResumeForm(instance=resume)
            is_edit_mode = True
            selected_cities = list(resume.service_area.values_list('id', flat=True))
            selected_specialty_categories = [resume.specialty_categories_id] if resume.specialty_categories_id else []
            selected_portfolios = list(resume.portfolios.values_list('id', flat=True))
        except Resume.DoesNotExist:
            form = ResumeForm()
            resume = None
            is_edit_mode = False
            selected_cities = []
            selected_specialty_categories = []
            selected_portfolios = []
        
        # دریافت تمام استان‌ها همراه با شهرهایشان
        provinces_qs = Province.objects.prefetch_related('cities').all()
        provinces = [
            {
                "id": p.id,
                "name": p.name,
                "cities": [{"id": c.id, "name": c.name} for c in p.cities.all()]
            }
            for p in provinces_qs
        ]
        
        # دریافت Topic های والد (بدون parent)
        parent_topics = Topic.objects.filter(parent__isnull=True)
        
        # دریافت پورتفولیوهای کاربر
        user_portfolios_qs = Portfolio.objects.filter(dealer=request.user, is_active=True)
        user_portfolios = [
            {
                "id": p.id,
                "subject": p.subject,
                "description": p.description,
            }
            for p in user_portfolios_qs
        ]
        
        work_links_qs = []
        if resume:
            work_links_qs = [
                {
                    "id": wl.id,
                    "title": wl.title,
                    "url": wl.url,
                    "description": wl.description or "",
                    "category": wl.category or "",
                    "completion_date": wl.completion_date.isoformat() if wl.completion_date else "",
                    "is_featured": wl.is_featured,
                    "order": wl.order,
                } for wl in resume.work_links.all()
            ]
        permissions_qs = []
        if resume:
            permissions_qs = [
                {
                    "id": pm.id,
                    "title": pm.title,
                    "description": pm.description or "",
                    "issue_date": pm.issue_date.isoformat() if pm.issue_date else "",
                    "expiry_date": pm.expiry_date.isoformat() if pm.expiry_date else "",
                    "issuing_authority": pm.issuing_authority or "",
                    "file_url": pm.file.url,
                    "is_selected": pm.is_selected,
                } for pm in resume.permission_files.all()
            ]
        return render(request, self.template_name, {
            'form': form,
            'resume': resume,
            'is_edit_mode': is_edit_mode,
            'provinces': json.dumps(provinces, cls=DjangoJSONEncoder),
            'parent_topics': parent_topics,
            'user_portfolios': json.dumps(user_portfolios, cls=DjangoJSONEncoder),
            'selected_cities': selected_cities,
            'selected_specialty_categories': selected_specialty_categories,
            'selected_portfolios': selected_portfolios,
            'work_links_json': json.dumps(work_links_qs, cls=DjangoJSONEncoder),
            'permissions_json': json.dumps(permissions_qs, cls=DjangoJSONEncoder),
        })
    
    def post(self, request):
        try:
            resume = Resume.objects.get(user=request.user)
            form = ResumeForm(request.POST, request.FILES, instance=resume)
            is_edit_mode = True
        except Resume.DoesNotExist:
            form = ResumeForm(request.POST, request.FILES)
            resume = None
            is_edit_mode = False

        dealer_type_id = request.POST.get('dealer_type', '')  # برای بازیابی مجدد
        specialty_category_id = request.POST.get('specialty_categories', '')

        # پردازش ورودی‌های مخفی (رشته کاما جدا)
        service_area_raw = request.POST.get('service_area', '')
        portfolio_raw = request.POST.get('portfolios', '')
        work_links_raw = request.POST.get('work_links', '')
        permissions_raw = request.POST.get('permissions', '')

        def parse_ids(raw):
            return [int(x) for x in raw.split(',') if x.strip().isdigit()]

        city_ids = parse_ids(service_area_raw)
        portfolio_ids_list = parse_ids(portfolio_raw)
        specialty_categories_id = int(specialty_category_id) if specialty_category_id.isdigit() else None
        work_link_ids = parse_ids(work_links_raw)
        permission_ids = parse_ids(permissions_raw)

        if form.is_valid():
            resume_instance = form.save(commit=False)
            resume_instance.user = request.user

            # اگر رزومه قبلی وجود دارد و واقعاً تغییری انجام شده باشد، وضعیت به "در حال بررسی" برگردد
            if is_edit_mode and form.has_changed():
                # فقط در صورتی که قبلاً تایید/رد/نیاز به ویرایش بوده یا هر وضعیتی غیر از under_review
                if resume.status != 'under_review':
                    resume_instance.status = 'under_review'
                    resume_instance.is_seen_by_manager = False  # تا دوباره برای مدیر برجسته شود

            if specialty_categories_id:
                resume_instance.specialty_categories_id = specialty_categories_id

            resume_instance.save()

            if city_ids:
                resume_instance.service_area.set(city_ids)
            else:
                resume_instance.service_area.clear()

            if portfolio_ids_list:
                resume_instance.portfolios.set(portfolio_ids_list)
            else:
                resume_instance.portfolios.clear()

            # به‌روزرسانی انتخاب لینک‌های نمونه کار (is_featured)
            if resume_instance.pk:
                if work_link_ids:
                    resume_instance.work_links.filter(id__in=work_link_ids).update(is_featured=True)
                    resume_instance.work_links.exclude(id__in=work_link_ids).update(is_featured=False)
                else:
                    resume_instance.work_links.update(is_featured=False)

                # به‌روزرسانی انتخاب مجوزها
                if permission_ids:
                    resume_instance.permission_files.filter(id__in=permission_ids).update(is_selected=True)
                    resume_instance.permission_files.exclude(id__in=permission_ids).update(is_selected=False)
                else:
                    resume_instance.permission_files.update(is_selected=False)

            messages.success(request, 'رزومه شما با موفقیت ذخیره شد.')
            return redirect('account:my_resume')

        # در صورت خطا:
        provinces_qs = Province.objects.prefetch_related('cities').all()
        provinces = [
            {"id": p.id, "name": p.name,
             "cities": [{"id": c.id, "name": c.name} for c in p.cities.all()]}
            for p in provinces_qs
        ]
        parent_topics = Topic.objects.filter(parent__isnull=True)
        user_portfolios_qs = Portfolio.objects.filter(dealer=request.user, is_active=True)
        user_portfolios = [
            {"id": p.id, "subject": p.subject, "description": p.description}
            for p in user_portfolios_qs
        ]

        return render(request, self.template_name, {
            'form': form,
            'resume': resume,
            'is_edit_mode': is_edit_mode,
            'provinces': json.dumps(provinces, cls=DjangoJSONEncoder),
            'parent_topics': parent_topics,
            'user_portfolios': json.dumps(user_portfolios, cls=DjangoJSONEncoder),
            'selected_cities': city_ids,
            'selected_specialty_categories': [specialty_categories_id] if specialty_categories_id else [],
            'selected_portfolios': portfolio_ids_list,
            'dealer_type_id': dealer_type_id,
        })

# اضافه کردن AJAX view برای دریافت دسته‌های تخصصی:
@login_required
def get_specialty_categories(request):
    """دریافت فرزندان Topic بر اساس dealer_type انتخاب شده"""
    dealer_type_id = request.GET.get('dealer_type_id')
    
    if dealer_type_id:
        try:
            specialty_categories = Topic.objects.filter(parent_id=dealer_type_id)
            data = [
                {
                    'id': category.id,
                    'name': category.name
                }
                for category in specialty_categories
            ]
            return JsonResponse({'categories': data})
        except ValueError:
            pass
    
    return JsonResponse({'categories': []})

@csrf_exempt
@login_required
def ajax_add_portfolio(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        done_time = request.POST.get('done_time')
        
        if not subject or not done_time:
            return JsonResponse({'success': False, 'error': 'عنوان و زمان انجام الزامی است.'})
        
        try:
            # فرض می‌کنیم اولین Topic را انتخاب می‌کنیم یا از فرم دریافت می‌کنیم
            topic = Topic.objects.first()  # یا از request دریافت کنید
            
            portfolio = Portfolio.objects.create(
                dealer=request.user,
                subject=subject,
                description=description,
                done_time=done_time,
                topic=topic,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'portfolio': {
                    'id': portfolio.id,
                    'subject': portfolio.subject,
                    'description': portfolio.description,
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'درخواست نامعتبر'})

@login_required
@require_POST
def ajax_add_permission(request):
    resume = getattr(request.user, 'resume', None)
    if not resume:
        return JsonResponse({'ok': False, 'error': 'رزومه‌ای برای شما ثبت نشده است'}, status=400)

    title = (request.POST.get('title') or '').strip()
    raw_issue_date = (request.POST.get('issue_date') or '').strip()
    raw_expiry_date = (request.POST.get('expiry_date') or '').strip()
    issuing_authority = (request.POST.get('issuing_authority') or '').strip()
    description = (request.POST.get('description') or '').strip()
    file_obj = request.FILES.get('file')

    if not title or not file_obj:
        return JsonResponse({'ok': False, 'error': 'عنوان و فایل الزامی است'}, status=400)

    issue_date = parse_date(raw_issue_date) if raw_issue_date else None
    expiry_date = parse_date(raw_expiry_date) if raw_expiry_date else None

    if raw_issue_date and issue_date is None:
        return JsonResponse({'ok': False, 'error': 'تاریخ صدور نامعتبر است.'}, status=400)
    if raw_expiry_date and expiry_date is None:
        return JsonResponse({'ok': False, 'error': 'تاریخ انقضا نامعتبر است.'}, status=400)
    if issue_date and expiry_date and expiry_date < issue_date:
        return JsonResponse({'ok': False, 'error': 'تاریخ انقضا نمی‌تواند قبل از تاریخ صدور باشد.'}, status=400)

    try:
        perm = Permission.objects.create(
            resume=resume,
            title=title,
            file=file_obj,
            description=description or '',
            issue_date=issue_date,
            expiry_date=expiry_date,
            issuing_authority=issuing_authority or '',
            is_selected=True  # مجوز تازه افزوده‌شده پیش‌فرض انتخاب شود
        )
        return JsonResponse({
            'ok': True,
            'permission': {
                'id': perm.id,
                'title': perm.title,
                'description': perm.description or '',
                'issue_date': perm.issue_date.isoformat() if perm.issue_date else '',
                'expiry_date': perm.expiry_date.isoformat() if perm.expiry_date else '',
                'issuing_authority': perm.issuing_authority or '',
                'file_url': perm.file.url,
                'is_selected': perm.is_selected,
            }
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def ajax_add_worklink(request):
    resume = getattr(request.user, 'resume', None)
    if not resume:
        return JsonResponse({'ok': False, 'error': 'ابتدا رزومه را ایجاد کنید.'}, status=400)

    title = (request.POST.get('title') or '').strip()
    url = (request.POST.get('url') or '').strip()
    description = (request.POST.get('description') or '').strip()
    category = (request.POST.get('category') or '').strip()
    raw_completion_date = (request.POST.get('completion_date') or '').strip()
    is_featured = request.POST.get('is_featured') in ['on', 'true', '1']
    order_raw = request.POST.get('order') or '0'

    if not title or not url:
        return JsonResponse({'ok': False, 'error': 'عنوان و لینک الزامی است.'}, status=400)

    # اعتبارسنجی URL
    validator = URLValidator()
    try:
        validator(url)
    except ValidationError:
        return JsonResponse({'ok': False, 'error': 'آدرس لینک نامعتبر است.'}, status=400)

    completion_date = parse_date(raw_completion_date) if raw_completion_date else None
    try:
        order = int(order_raw)
        if order < 0:
            order = 0
    except ValueError:
        order = 0

    try:
        wl = WorkLink.objects.create(
            resume=resume,
            title=title,
            url=url,
            description=description or '',
            category=category or '',
            completion_date=completion_date,
            is_featured=is_featured,
            order=order,
        )
        return JsonResponse({
            'ok': True,
            'worklink': {
                'id': wl.id,
                'title': wl.title,
                'url': wl.url,
                'description': wl.description or '',
                'category': wl.category or '',
                'completion_date': wl.completion_date.isoformat() if wl.completion_date else '',
                'is_featured': wl.is_featured,
                'order': wl.order,
            }
        })
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


