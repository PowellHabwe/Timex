# Generated by Django 3.1.1 on 2024-11-11 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_ride'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ride',
            old_name='user',
            new_name='driver',
        ),
        migrations.AddField(
            model_name='ride',
            name='user_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ride',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='active', max_length=20),
        ),
    ]