# Generated by Django 3.1.1 on 2024-11-12 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0037_auto_20241112_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costmanagement',
            name='cost_per_km',
            field=models.IntegerField(help_text='Cost per kilometer'),
        ),
    ]
