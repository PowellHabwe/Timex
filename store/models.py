import uuid
from django.utils import timezone
from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
# from django.contrib.postgres.fields import JSONField

from decimal import Decimal


# Create your models here.

class Vehicle(models.Model):
    vehicle_name = models.CharField(max_length=200)
    vehicle_plate = models.CharField(max_length=200)
    driver = models.ForeignKey(Account, on_delete=models.CASCADE)

    latitude = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200)
    vehicle_type = models.CharField(max_length=5000)
    phone_number = models.CharField(max_length=200,default="no phone number")
    vehicle_available = models.BooleanField(default=True)


    def get_url(self):
        return reverse('hospital_detail', kwargs={'pk': self.pk})#'uuid':self.uuid

    def __str__(self):
        return self.vehicle_name
    

class AvailableTime(models.Model):
    hospital = models.ForeignKey(Vehicle, on_delete=models.CASCADE, default="ffea3154-ed09-4d89-a7a6-de74ee5a1742")
    time = models.DateTimeField()
    is_available = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.time}"
    
    def get_url(self):
        return reverse('appointment_form_detail', kwargs={'vehicle_id': self.vehicle_id, 'available_time_id': self.pk})


class SuccessfulAppointment(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    available_time = models.ForeignKey(AvailableTime, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Successful Appointment for {self.available_time.time} by {self.user.email}"


class IsDriver(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    license_number = models.CharField(max_length = 200)

    def __str__(self):
        return f"{self.user}"
    

class VehicleMaintenance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'is_driver': True})  # Only drivers can be selected
    maintenance_date = models.DateTimeField()
    description = models.TextField()
    maintenance_done = models.BooleanField(default=False)

    def __str__(self):
        return f"Maintenance for {self.vehicle.vehicle_name} on {self.maintenance_date}"

    class Meta:
        verbose_name = "Vehicle Maintenance"
        verbose_name_plural = "Vehicle Maintenances"


class VehicleInspection(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'is_driver': True})  # Only drivers can be selected
    inspection_date = models.DateTimeField()
    description = models.TextField()
    inspection_done = models.BooleanField(default=False)

    def __str__(self):
        return f"Inspection for {self.vehicle.vehicle_name} on {self.inspection_date}"

    class Meta:
        verbose_name = "Vehicle Inspection"
        verbose_name_plural = "Vehicle Inspections"



class Ride(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # user_id = models.IntegerField()  # Store the user's primary key as an integer
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='user_rides')  # User who booked the ride
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='driver_rides')  # Driver assigned to the ride
    start_latitude = models.FloatField()
    start_longitude = models.FloatField()
    end_latitude = models.FloatField()
    end_longitude = models.FloatField()
    distance_km = models.FloatField()
    cost = models.FloatField()
    duration_minutes = models.IntegerField()
    ride_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    destination_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Ride {self.id} - {self.status}"
    


class CostManagement(models.Model):
    cost_per_km = models.IntegerField( help_text="Cost per kilometer")
    promotional_message = models.TextField(blank=True, null=True, help_text="Promotional message related to cost management")

    def __str__(self):
        return f"Cost per KM: {self.cost_per_km}"
    


class Earnings(models.Model):
    driver = models.ForeignKey(Account, on_delete=models.CASCADE)  # Assuming Account is the User model for the driver
    date = models.DateField(default=timezone.now)  # Store earnings for each day
    daily_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)  # Earnings for the current day (24 hours)
    total_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)  # Cumulative earnings over time

    def add_earning(self, amount):
        """ Adds the amount to both daily and total earnings. """
        amount = Decimal(amount)

        self.daily_earnings += amount
        self.total_earnings += amount
        self.save()

    def reset_daily_earnings(self):
        """ Resets the daily earnings at the end of each day. """
        self.daily_earnings = 0.0
        self.save()

    def __str__(self):
        return f"{self.driver} - {self.date} - Ksh{self.daily_earnings} (Daily), Ksh{self.total_earnings} (Total)"