from django.conf import settings
from django.db import models


class IssueReport(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (STATUS_NEW, 'جدید'),
        (STATUS_IN_PROGRESS, 'در حال بررسی'),
        (STATUS_RESOLVED, 'حل شد'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر')
    page_url = models.URLField(max_length=600, verbose_name='آدرس صفحه')
    description = models.TextField(verbose_name='شرح مشکل')
    attachment = models.FileField(upload_to='issue_reports/', null=True, blank=True, verbose_name='فایل/عکس')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name='وضعیت')
    staff_notes = models.TextField(blank=True, verbose_name='یادداشت پشتیبان')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'گزارش مشکل'
        verbose_name_plural = 'گزارش مشکلات'

    def __str__(self):
        return f"#{self.pk} {self.page_url[:40]}"
