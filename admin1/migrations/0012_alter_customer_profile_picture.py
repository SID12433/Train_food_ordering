# Generated by Django 4.2.5 on 2024-01-29 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin1', '0011_remove_offer_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='profile_picture',
            field=models.ImageField(null=True, upload_to='images'),
        ),
    ]
