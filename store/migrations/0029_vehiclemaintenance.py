# Generated by Django 3.1.1 on 2024-11-11 12:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0028_vehicle_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleMaintenance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maintenance_date', models.DateTimeField()),
                ('description', models.TextField()),
                ('driver', models.ForeignKey(limit_choices_to={'is_driver': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.vehicle')),
            ],
            options={
                'verbose_name': 'Vehicle Maintenance',
                'verbose_name_plural': 'Vehicle Maintenances',
            },
        ),
    ]
