# Generated by Django 5.0.1 on 2024-01-18 13:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='vendors',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='admin1.vendor'),
        ),
        migrations.AddField(
            model_name='offer',
            name='vendors',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='admin1.vendor'),
        ),
    ]
