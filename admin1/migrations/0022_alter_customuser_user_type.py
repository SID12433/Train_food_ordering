# Generated by Django 4.2.5 on 2024-03-25 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin1', '0021_food_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('customer', 'customer'), ('vendor', 'vendor')], max_length=50),
        ),
    ]
