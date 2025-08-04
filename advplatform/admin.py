from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from .models import ActivityCategory, CustomUser, Resume, SpecialityCategory, Topic,\
    Campaign, Portfolio,UsersImages, CampaignImages, PortfolioImages 



class UsersImageInline(admin.TabularInline):
    model = UsersImages


class CampaignImagesInline(admin.TabularInline):
    model = CampaignImages

class PortfolioImagesInline(admin.TabularInline):
    model = PortfolioImages
    

@register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_time']
    search_fields = ['name']


@register(SpecialityCategory)
class SpecialityCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_time']
    search_fields = ['name']    


@register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_time']
    search_fields = ['name']


class CustomUserAdmin(UserAdmin):
    # فرم‌های ایجاد و ویرایش کاربر
    # form = UserChangeForm
    # add_form = UserCreationForm

    # فیلدهایی که در پنل ادمین نمایش داده می‌شوند
    list_display = ('email', 'first_name', 'last_name', 'company_name','user_type', 'cutomer_type', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 'last_name', 'company_name',
            'phone_number', 'address', 
            'birth_date', 'field_of_activity',
            'user_type','cutomer_type','dealer_type',
            'rank','bussines_value',
             'speciality_field',
             'is_am'
            )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    inlines = [UsersImageInline]

    def save_model(self, request, obj, form, change):
        # اگر کاربر جدید است یا رمز عبور تغییر کرده است، آن را هش می‌کنیم
        if not change or 'password1' in form.changed_data:
            obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)

admin.site.register(CustomUser, CustomUserAdmin)

    

@register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['customer','describe', 'purposed_price', 'created_time', 'modified_time', 'status']
    list_filter = ['customer', 'is_active']
    search_fields = ['topic']
    inlines = [CampaignImagesInline]
    

@register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['dealer','description', 'done_time', 'created_time', 'is_active']
    list_filter = ['dealer', 'is_active']
    list_editable = ['is_active']
    search_fields = ['topic']
    inlines = [PortfolioImagesInline]


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'is_seen_by_manager', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'title']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')