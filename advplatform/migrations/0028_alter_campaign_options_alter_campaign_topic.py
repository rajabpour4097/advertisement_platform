# Generated by Django 5.1.6 on 2025-03-06 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advplatform', '0027_alter_customuser_phone_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campaign',
            options={'ordering': ['-created_time'], 'verbose_name': 'کمپین', 'verbose_name_plural': 'کمپین ها'},
        ),
        migrations.AlterField(
            model_name='campaign',
            name='topic',
            field=models.ManyToManyField(related_name='topics', to='advplatform.topic', verbose_name='موضوعات کمپین'),
        ),
    ]
