# Generated by Django 3.2 on 2025-04-27 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advplatform', '0032_auto_20250426_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='needs_mentor',
            field=models.BooleanField(blank=True, null=True, verbose_name='نیاز به مشاور'),
        ),
    ]
