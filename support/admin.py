from django.contrib import admin
from .models import (
    SupportDepartment, SupportSubject, Ticket, TicketMessage, TicketRating,
    LiveChatSession, LiveChatMessage
)


@admin.register(SupportDepartment)
class SupportDepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    filter_horizontal = ('supporters',)


@admin.register(SupportSubject)
class SupportSubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('title', 'department__name')


class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ('sender', 'message', 'attachment', 'created_at')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'department', 'subject', 'supporter', 'status', 'priority', 'created_at', 'last_response_time')
    list_filter = ('status', 'priority', 'department', 'supporter')
    search_fields = ('id', 'title', 'user__email', 'user__first_name', 'user__last_name')
    inlines = [TicketMessageInline]
    autocomplete_fields = ('user', 'department', 'subject', 'supporter')


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'sender', 'is_staff_reply', 'created_at')
    list_filter = ('is_staff_reply',)
    search_fields = ('ticket__id', 'sender__email')


@admin.register(TicketRating)
class TicketRatingAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'supporter', 'user', 'score', 'created_at')
    list_filter = ('score',)
    search_fields = ('ticket__id', 'supporter__email', 'user__email')


class LiveChatMessageInline(admin.TabularInline):
    model = LiveChatMessage
    extra = 0
    readonly_fields = ('sender', 'message', 'created_at')


@admin.register(LiveChatSession)
class LiveChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'department', 'supporter', 'is_active', 'created_at')
    list_filter = ('is_active', 'department', 'supporter')
    search_fields = ('id', 'user__email')
    inlines = [LiveChatMessageInline]


@admin.register(LiveChatMessage)
class LiveChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'is_supporter', 'created_at')
    list_filter = ('is_supporter',)
    search_fields = ('session__id', 'sender__email')
