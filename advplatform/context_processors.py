from django.apps import apps
from django.contrib.auth.models import Group




def get_model_meta_info(request):
    # لیست ممنوعه (اینجا تعریف می‌کنید یا از تنظیمات می‌خوانید)
    restricted_names = ['عکس نمونه کار', 'عکس کمپین', 'عکس کاربر']

    # استخراج مدل‌های اپلیکیشن
    app_models = apps.get_app_config('advplatform').get_models()

    valid_models = []

    for model in app_models:
        # بررسی نام مدل یا هر فیلدی که لازم دارید
        if model._meta.verbose_name not in restricted_names:  # چک verbose_name
            valid_models.append({
                'verbose_name': model._meta.verbose_name,
                'verbose_name_plural': model._meta.verbose_name_plural,
                'model_name': model._meta.model_name,
                'app_label': model._meta.app_label,
            })

    return {'valid_models': valid_models}


def get_admin_groups(request):
    # دریافت تمام گروه‌ها
    groups = Group.objects.all()

    # آماده‌سازی داده‌ها برای قالب
    group_list = [{'id': group.id, 'name': group.name} for group in groups]

    return {'admin_groups': group_list}
