from django.contrib import admin
from django.contrib.admin import register
from .models import ActivityCategory, SpecialityCategory, Topic,\
    Mentor, Customer, Dealer, Campaign, Portfolio,\
        CustomerImages, DealerImages, MentorImages, CampaignImages,\
           PortfolioImages 



class MentorImagesInline(admin.TabularInline):
    model = MentorImages

class CustomerImagesInline(admin.TabularInline):
    model = CustomerImages

class DealerImagesInline(admin.TabularInline):
    model = DealerImages

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


@register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'username', 'created_time', 'is_active']
    search_fields = ['username']
    list_editable = ['is_active']
    list_filter = ['is_active']
    inlines = [MentorImagesInline]
    

@register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'username', 'type', 'customer_mentor', 'created_time']
    list_filter = ['type', 'is_active']
    search_fields = ['username']
    inlines = [CustomerImagesInline]


@register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'username', 'type', 'created_time']
    list_filter = ['type', 'is_active']
    search_fields = ['username']
    inlines = [DealerImagesInline]


@register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['customer','describe', 'purposed_price', 'created_time']
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