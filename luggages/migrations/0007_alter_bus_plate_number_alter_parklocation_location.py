# Generated by Django 5.0.4 on 2024-05-01 02:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luggages', '0006_alter_state_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='plate_number',
            field=models.CharField(max_length=9, unique=True, validators=[django.core.validators.RegexValidator(message='Plate number must be in the format: AAA-111-AAA', regex='^[A-Z]{3}-\\d{3}-[A-Z]{3}$')], verbose_name='Plate Number'),
        ),
        migrations.AlterField(
            model_name='parklocation',
            name='location',
            field=models.CharField(help_text='The city the park is located in.', max_length=50, unique=True, verbose_name='Location'),
        ),
    ]
