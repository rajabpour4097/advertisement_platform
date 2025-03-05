# Generated by Django 5.1.6 on 2025-03-04 15:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_alter_editingcampaign_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestForMentor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_mentor', to=settings.AUTH_USER_MODEL)),
                ('requested_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'درخواست مشاور',
                'verbose_name_plural': 'درخواست های مشاور',
                'ordering': ['-created_at'],
            },
        ),
    ]
