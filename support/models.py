from django.db import models
from django.conf import settings
from advplatform.models import BaseModel
from django.utils import timezone
from datetime import timedelta

User = settings.AUTH_USER_MODEL


class SupportDepartment(BaseModel):
    """دسته بندی اصلی (دپارتمان) که فقط is_staff می تواند مدیریت کند"""
    name = models.CharField(max_length=120, unique=True, verbose_name='نام دپارتمان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    supporters = models.ManyToManyField(
        User,
        blank=True,
        related_name='departments',
        limit_choices_to={'is_supporter': True, 'is_active': True},
        verbose_name='پشتیبان های منتسب'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'دپارتمان پشتیبانی'
        verbose_name_plural = 'دپارتمان های پشتیبانی'
        ordering = ['name']

    def __str__(self):
        return self.name


class SupportSubject(BaseModel):
    """فرزند دپارتمان: موضوع تیکت"""
    department = models.ForeignKey(
        SupportDepartment,
        on_delete=models.CASCADE,
        related_name='subjects',
        verbose_name='دپارتمان'
    )
    title = models.CharField(max_length=150, verbose_name='عنوان موضوع')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    class Meta:
        verbose_name = 'موضوع تیکت'
        verbose_name_plural = 'موضوعات تیکت'
        unique_together = ('department', 'title')
        ordering = ['department__name', 'title']

    def __str__(self):
        return f"{self.department.name} - {self.title}"


class Ticket(BaseModel):
    STATUS_CHOICES = (
        ('open', 'باز'),
        ('waiting', 'در انتظار کاربر'),
        ('answering', 'در حال بررسی'),
        ('closed', 'بسته شده'),
    )
    PRIORITY_CHOICES = (
        ('low', 'کم'),
        ('normal', 'معمولی'),
        ('high', 'بالا'),
        ('urgent', 'فوری'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets', verbose_name='کاربر ارسال کننده')
    department = models.ForeignKey(SupportDepartment, on_delete=models.PROTECT, related_name='tickets', verbose_name='دپارتمان')
    subject = models.ForeignKey(SupportSubject, on_delete=models.PROTECT, related_name='tickets', verbose_name='موضوع')
    supporter = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, limit_choices_to={'is_supporter': True}, related_name='assigned_tickets', verbose_name='پشتیبان پاسخگو')
    title = models.CharField(max_length=180, verbose_name='عنوان (نمایشی در لیست)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='وضعیت')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='اولویت')
    attachment = models.FileField(upload_to='tickets/attachments/', blank=True, null=True, verbose_name='فایل پیوست')
    last_response_time = models.DateTimeField(blank=True, null=True, verbose_name='آخرین پاسخ')
    closed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ بستن')
    user_rate = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='امتیاز کاربر (۱ تا ۵)')

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title}"

    def is_closed(self):
        return self.status == 'closed'


class TicketMessage(BaseModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages', verbose_name='تیکت')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_messages', verbose_name='ارسال کننده')
    message = models.TextField(verbose_name='متن پیام')
    attachment = models.FileField(upload_to='tickets/messages/', blank=True, null=True, verbose_name='فایل پیوست')
    is_staff_reply = models.BooleanField(default=False, verbose_name='پاسخ پشتیبان')
    seen_by_user = models.BooleanField(default=False, verbose_name='دیده شده توسط کاربر')

    class Meta:
        verbose_name = 'پیام تیکت'
        verbose_name_plural = 'پیام های تیکت'
        ordering = ['created_at']

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.sender_id}"


class TicketRating(BaseModel):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='rating', verbose_name='تیکت')
    supporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_ratings', verbose_name='پشتیبان')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_support_ratings', verbose_name='کاربر')
    score = models.PositiveSmallIntegerField(verbose_name='امتیاز (۱ تا ۵)')
    comment = models.TextField(blank=True, null=True, verbose_name='توضیح امتیاز')

    class Meta:
        verbose_name = 'امتیاز پشتیبان'
        verbose_name_plural = 'امتیازات پشتیبان'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(score__gte=1, score__lte=5), name='support_score_range')
        ]

    def __str__(self):
        return f"Rating {self.score} for ticket {self.ticket_id}"


# --- بخش گفتگوی آنلاین ---
class LiveChatSession(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_chats', verbose_name='کاربر')
    department = models.ForeignKey(SupportDepartment, on_delete=models.PROTECT, related_name='live_chats', verbose_name='دپارتمان')
    supporter = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, limit_choices_to={'is_supporter': True}, related_name='assigned_live_chats', verbose_name='پشتیبان')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    closed_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان پایان')

    class Meta:
        verbose_name = 'جلسه گفتگوی آنلاین'
        verbose_name_plural = 'جلسات گفتگوهای آنلاین'
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat {self.id} - {self.user}"


class LiveChatMessage(BaseModel):
    session = models.ForeignKey(LiveChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='جلسه')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_chat_messages', verbose_name='ارسال کننده')
    message = models.TextField(verbose_name='پیام')
    attachment = models.FileField(upload_to='livechat/messages/', blank=True, null=True, verbose_name='فایل')
    is_supporter = models.BooleanField(default=False, verbose_name='پیام پشتیبان')
    seen = models.BooleanField(default=False, verbose_name='دیده شده')

    class Meta:
        verbose_name = 'پیام گفتگوی آنلاین'
        verbose_name_plural = 'پیام های گفتگوی آنلاین'
        ordering = ['created_at']

    def __str__(self):
        return f"ChatMsg {self.session_id} - {self.sender_id}"


class SupporterPresence(BaseModel):
    """وضعیت آنلاین بودن پشتیبان"""
    supporter = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='supportpresence',
        limit_choices_to={'is_supporter': True},
        verbose_name='پشتیبان'
    )
    last_seen = models.DateTimeField(auto_now=True, verbose_name='آخرین مشاهده')
    is_manual_offline = models.BooleanField(default=False, verbose_name='آفلاین دستی')

    ONLINE_THRESHOLD_SECONDS = 90

    class Meta:
        verbose_name = 'حضور پشتیبان'
        verbose_name_plural = 'حضور پشتیبانان'

    def __str__(self):
        return f"Presence {self.supporter_id}"

    @property
    def is_online(self):
        if self.is_manual_offline:
            return False
        return self.last_seen >= timezone.now() - timedelta(seconds=self.ONLINE_THRESHOLD_SECONDS)
