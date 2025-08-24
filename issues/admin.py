from django.contrib import admin
from .models import IssueReport


@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'page_url', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('page_url', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'user', 'page_url', 'description', 'attachment')
