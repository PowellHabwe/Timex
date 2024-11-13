# Generated by Django 5.0.2 on 2024-03-06 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_alter_appointment_email'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='email',
            new_name='hospital_email',
        ),
        migrations.AddField(
            model_name='appointment',
            name='user_email',
            field=models.EmailField(blank=True, max_length=100),
        ),
    ]