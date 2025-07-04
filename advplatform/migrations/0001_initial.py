# Generated by Django 3.2 on 2025-05-31 11:10

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=30, unique=True, verbose_name='شماره تماس')),
                ('address', models.TextField(blank=True, null=True, verbose_name='آدرس')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='تاریخ تولد')),
                ('user_type', models.CharField(blank=True, choices=[('', ''), ('customer', 'مشتری'), ('dealer', 'عامل تبلیغ'), ('mentor', 'مشاور')], default='', max_length=30, null=True, verbose_name='نوع کاربر')),
                ('cutomer_type', models.CharField(blank=True, choices=[('', ''), ('juridical', 'حقیقی'), ('private', 'حقوقی')], default='', max_length=30, null=True, verbose_name='نوع مشتری')),
                ('dealer_type', models.CharField(blank=True, choices=[('', ''), ('influencer', 'اینفلوئنسر '), ('private_designer', 'شخص عادی'), ('corporate', 'شرکت')], default='', max_length=30, null=True, verbose_name='نوع عامل تبلیغ')),
                ('rank', models.SmallIntegerField(blank=True, default=2, null=True, verbose_name='رتبه')),
                ('bussines_value', models.BigIntegerField(blank=True, null=True, verbose_name='ارزش کسب و کار')),
                ('modified_time', models.DateTimeField(auto_now=True, verbose_name='آخرین تغییر پروفایل')),
                ('is_am', models.BooleanField(default=False, verbose_name='مدیر تبلیغات')),
            ],
            options={
                'verbose_name': 'کاربر',
                'verbose_name_plural': 'کاربران',
            },
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('describe', models.TextField(verbose_name='شرح کمپین')),
                ('purposed_price', models.BigIntegerField(verbose_name='قیمت پیشنهادی')),
                ('starttimedate', models.DateTimeField(blank=True, null=True, verbose_name='زمان شروع')),
                ('endtimedate', models.DateTimeField(blank=True, null=True, verbose_name='زمان اتمام')),
                ('deadline', models.DateField(blank=True, null=True, verbose_name='تاریخ مهلت اجرا')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('reviewing', 'در حال بررسی'), ('progressing', 'در حال برگزاری'), ('unsuccessful', 'ناموفق'), ('successful', 'موفق'), ('editing', 'اصلاح مشتری'), ('cancel', 'انصراف مشتری')], default='reviewing', max_length=30, verbose_name='وضعیت اجرای کمپین')),
                ('is_active', models.BooleanField(default=False, verbose_name='وضعیت کمپین')),
                ('needs_mentor', models.BooleanField(blank=True, null=True, verbose_name='نیاز به مشاور')),
                ('assigned_mentor', models.ForeignKey(blank=True, limit_choices_to={'is_active': True, 'user_type': 'mentor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_campaigns', to=settings.AUTH_USER_MODEL, verbose_name='مشاور اختصاص داده شده')),
                ('campaign_dealer', models.ForeignKey(blank=True, limit_choices_to={'is_active': True, 'user_type': 'dealer'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='campaign_dealers', to=settings.AUTH_USER_MODEL, verbose_name='مجری کمپین')),
                ('customer', models.ForeignKey(limit_choices_to={'is_active': True, 'user_type': 'customer'}, on_delete=django.db.models.deletion.CASCADE, related_name='customers', to=settings.AUTH_USER_MODEL, verbose_name='کارفرما')),
                ('list_of_participants', models.ManyToManyField(blank=True, limit_choices_to={'is_active': True, 'user_type': 'dealer'}, related_name='campaigns', to=settings.AUTH_USER_MODEL, verbose_name='لیست شرکت کنندگان')),
            ],
            options={
                'verbose_name': 'کمپین',
                'verbose_name_plural': 'کمپین ها',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=50, null=True, verbose_name='عنوان نمونه کار')),
                ('description', models.TextField(blank=True, null=True, verbose_name='شرح نمونه کار')),
                ('done_time', models.DateField(verbose_name='زمان انجام')),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('execution_price', models.BigIntegerField(blank=True, null=True, verbose_name='هزینه اجرا')),
                ('is_active', models.BooleanField(default=True, verbose_name='وضعیت')),
                ('dealer', models.ForeignKey(limit_choices_to={'is_active': True, 'user_type': 'dealer'}, on_delete=django.db.models.deletion.CASCADE, related_name='dealers', to=settings.AUTH_USER_MODEL, verbose_name='نام مجری')),
            ],
            options={
                'verbose_name': 'نمونه کار',
                'verbose_name_plural': 'نمونه کارها',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='UsersImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='users/')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customuserimages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'عکس کاربر',
                'verbose_name_plural': 'عکس های کاربر',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('min_price', models.BigIntegerField(blank=True, null=True, verbose_name='حداقل قیمت')),
                ('icon', models.ImageField(blank=True, null=True, upload_to='topics/', verbose_name='آیکون')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='advplatform.topic')),
            ],
            options={
                'verbose_name': 'موضوع',
                'verbose_name_plural': 'موضوعات',
            },
        ),
        migrations.CreateModel(
            name='SpecialityCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='advplatform.specialitycategory')),
            ],
            options={
                'verbose_name': 'دسته بندی تخصص',
                'verbose_name_plural': 'دسته بندی های تخصص',
            },
        ),
        migrations.CreateModel(
            name='PortfolioImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='portfolios/', verbose_name='عکس های نمونه کار')),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolioimages', to='advplatform.portfolio')),
            ],
            options={
                'verbose_name': 'عکس نمونه کار',
                'verbose_name_plural': 'عکس های نمونه کارها',
            },
        ),
        migrations.AddField(
            model_name='portfolio',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='advplatform.topic', verbose_name='موضوع'),
        ),
        migrations.CreateModel(
            name='CampaignImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='campaigns/', verbose_name='آپلود تصویر کمپین')),
                ('campaigns', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaignsimages', to='advplatform.campaign')),
            ],
            options={
                'verbose_name': 'عکس کمپین',
                'verbose_name_plural': 'عکس های کمپین',
            },
        ),
        migrations.AddField(
            model_name='campaign',
            name='topic',
            field=models.ManyToManyField(related_name='topics', to='advplatform.Topic', verbose_name='موضوعات کمپین'),
        ),
        migrations.CreateModel(
            name='ActivityCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('modified_time', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='advplatform.activitycategory')),
            ],
            options={
                'verbose_name': 'زمینه فعالیت',
                'verbose_name_plural': 'زمینه های فعالیت',
            },
        ),
        migrations.AddField(
            model_name='customuser',
            name='field_of_activity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='advplatform.activitycategory', verbose_name='زمینه فعالیت'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='speciality_field',
            field=models.ManyToManyField(blank=True, null=True, related_name='speciality_field', to='advplatform.Topic', verbose_name='تخصص'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
