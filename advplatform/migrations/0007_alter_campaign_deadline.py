# Generated by Django 3.2 on 2025-02-06 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advplatform', '0006_auto_20250206_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='deadline',
            field=models.DateField(blank=True, null=True),
        ),
    ]
