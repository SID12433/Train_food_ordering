# Generated by Django 4.2.5 on 2024-03-23 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin1', '0020_restaurantreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='type',
            field=models.CharField(default='veg', max_length=500),
        ),
    ]
