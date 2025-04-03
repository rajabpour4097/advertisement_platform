from django.db import models
from django.conf import settings
from advplatform.models import CustomUser

class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='فرستنده'
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='گیرنده'
    )
    subject = models.CharField(max_length=255, verbose_name='موضوع')
    body = models.TextField(verbose_name='متن پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    is_starred = models.BooleanField(default=False, verbose_name='ستاره‌دار')
    is_deleted = models.BooleanField(default=False, verbose_name='حذف شده')
    is_spam = models.BooleanField(default=False, verbose_name='هرزنامه')
    has_attachment = models.BooleanField(default=False, verbose_name='دارای پیوست')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'
    
    def __str__(self):
        return f'از {self.sender} به {self.receiver}: {self.subject}'

    @staticmethod
    def get_allowed_receivers(user):
        """دریافت لیست کاربران مجاز برای ارسال پیام"""
        if user.is_staff:
            return CustomUser.objects.all().exclude(id=user.id)
        
        if user.user_type == 'customer':
            # مشاور مربوطه و مدیران سیستم
            return CustomUser.objects.filter(
                models.Q(id=user.customer_mentor.id) |
                models.Q(is_staff=True)
            ).exclude(id=user.id)
            
        if user.user_type == 'mentor':
            # مشتریان مربوطه و مدیران سیستم
            return CustomUser.objects.filter(
                models.Q(customer_mentor=user) |
                models.Q(is_staff=True)
            ).exclude(id=user.id)
            
        if user.user_type == 'dealer':
            # فقط مدیران سیستم
            return CustomUser.objects.filter(is_staff=True)