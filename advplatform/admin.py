from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from .models import ActivityCategory, CustomUser, Resume, SpecialityCategory, Topic,\
    Campaign, Portfolio, UsersImages, CampaignImages, PortfolioImages, \
    Permission, Province, City, WorkLink
    
    

class UsersImageInline(admin.TabularInline):
    model = UsersImages

class CampaignImagesInline(admin.TabularInline):
    model = CampaignImages

class PortfolioImagesInline(admin.TabularInline):
    model = PortfolioImages

class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 1
    fields = ['title', 'file', 'description', 'issue_date', 'expiry_date', 'issuing_authority']
    readonly_fields = ['created_at', 'modified_at']


class WorkLinkInline(admin.TabularInline):
    model = WorkLink
    extra = 1
    fields = ['title', 'url', 'category', 'completion_date', 'is_featured', 'order']
    readonly_fields = ['created_at', 'modified_at']

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

@register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'province', 'created_at']
    list_filter = ['province']
    search_fields = ['name', 'province__name']

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'company_name','user_type', 'cutomer_type', 'is_staff', 'created_at')
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
             'is_am',
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
    list_display = ['user', 'title', 'status', 'is_seen_by_manager', 'get_permissions_count', 'get_work_links_count', 'created_at']
    list_filter = ['status', 'dealer_type', 'created_at', 'is_seen_by_manager']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'title']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PermissionInline, WorkLinkInline]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'title', 'dealer_type', 'describe')
        }),
        ('تخصص و خدمات', {
            'fields': ('specialty_categories', 'services', 'service_area')
        }),
        ('اطلاعات تکمیلی', {
            'fields': ('file', 'socialmedia_and_sites', 'tools_and_platforms', 'portfolios')
        }),
        ('اطلاعات مالی', {
            'fields': ('bank_account',)
        }),
        ('وضعیت و بررسی', {
            'fields': ('status', 'manager_comment', 'is_seen_by_manager')
        }),
        ('زمان‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_work_links_count(self, obj):
        return obj.get_work_links_count()
    get_work_links_count.short_description = 'تعداد لینک‌ها'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'dealer_type').prefetch_related(
            'permission_files', 'work_links', 'service_area', 'specialty_categories'
        )

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'resume', 'issue_date', 'expiry_date', 'is_expired', 'created_at']
    list_filter = ['issue_date', 'expiry_date', 'created_at']
    search_fields = ['title', 'resume__user__username', 'issuing_authority']
    readonly_fields = ['created_at', 'modified_at']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'منقضی شده'

@admin.register(WorkLink)
class WorkLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'resume', 'category', 'is_featured', 'completion_date', 'created_at']
    list_filter = ['category', 'is_featured', 'completion_date', 'created_at']
    search_fields = ['title', 'url', 'resume__user__username', 'category']
    readonly_fields = ['created_at', 'modified_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('resume__user')

