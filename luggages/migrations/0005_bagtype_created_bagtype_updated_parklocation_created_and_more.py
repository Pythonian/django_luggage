# Generated by Django 5.0.3 on 2024-03-23 10:33

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luggages', '0004_alter_bagtype_options_alter_bus_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bagtype',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bagtype',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='parklocation',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parklocation',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
