# Generated by Django 5.0.4 on 2024-05-01 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luggages', '0005_bagtype_created_bagtype_updated_parklocation_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='state',
            name='name',
            field=models.CharField(max_length=20, unique=True, verbose_name='Name'),
        ),
    ]
