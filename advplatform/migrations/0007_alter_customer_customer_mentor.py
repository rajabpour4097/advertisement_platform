# Generated by Django 3.2 on 2025-01-28 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('advplatform', '0006_alter_customer_customer_mentor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_mentor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='advplatform.mentor'),
        ),
    ]
