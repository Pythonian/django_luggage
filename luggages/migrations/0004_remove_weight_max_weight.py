# Generated by Django 4.1.2 on 2022-11-06 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('luggages', '0003_trip_date_of_journey'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weight',
            name='max_weight',
        ),
    ]