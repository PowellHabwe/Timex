# Generated by Django 5.0.2 on 2024-03-05 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_availabletime_hospital_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='email',
            field=models.EmailField(blank=True, max_length=100),
        ),
    ]