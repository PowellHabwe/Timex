# Generated by Django 3.1.1 on 2024-11-12 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0035_auto_20241112_0701'),
    ]

    operations = [
        migrations.AddField(
            model_name='ride',
            name='destination_name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
