# Generated by Django 3.2 on 2025-02-05 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advplatform', '0002_alter_customuser_cutomer_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activitycategory',
            options={'verbose_name': 'زمینه فعالیت', 'verbose_name_plural': 'زمینه های فعالیت'},
        ),
        migrations.AlterModelOptions(
            name='campaign',
            options={'verbose_name': 'کمپین', 'verbose_name_plural': 'کمپین ها'},
        ),
        migrations.AlterModelOptions(
            name='portfolio',
            options={'verbose_name': 'نمونه کار', 'verbose_name_plural': 'نمونه کارها'},
        ),
        migrations.AlterModelOptions(
            name='specialitycategory',
            options={'verbose_name': 'دسته بندی تخصص', 'verbose_name_plural': 'دسته بندی های تخصص'},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'verbose_name': 'موضوع', 'verbose_name_plural': 'موضوعات'},
        ),
    ]
