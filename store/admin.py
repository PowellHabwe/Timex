from django.contrib import admin
from .models import  Earnings,CostManagement, Ride, VehicleInspection, VehicleMaintenance,Vehicle, AvailableTime,IsDriver, VehicleInspection, SuccessfulAppointment


admin.site.register(Vehicle)
admin.site.register(IsDriver)
admin.site.register(AvailableTime)
admin.site.register(SuccessfulAppointment)
admin.site.register(Ride)
admin.site.register(CostManagement)
admin.site.register(Earnings)



class VehicleMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'driver','maintenance_done', 'maintenance_date', 'description')
    list_filter = ('vehicle', 'driver','maintenance_done', 'maintenance_date')
    search_fields = ('vehicle__vehicle_name', 'driver__email')

    readonly_fields = ('driver',)  # Make the driver field read-only as it is auto-filled

    def save_model(self, request, obj, form, change):
        # Automatically set the driver to the one associated with the selected vehicle
        if obj.vehicle:
            obj.driver = obj.vehicle.driver  # Set the driver to the vehicle's driver
        super().save_model(request, obj, form, change)


class VehicleInspectionAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'driver','inspection_done', 'inspection_date', 'description')
    list_filter = ('vehicle', 'driver','inspection_done', 'inspection_date')
    search_fields = ('vehicle__vehicle_name', 'driver__email')

    readonly_fields = ('driver',)  # Make the driver field read-only as it is auto-filled

    def save_model(self, request, obj, form, change):
        # Automatically set the driver to the one associated with the selected vehicle
        if obj.vehicle:
            obj.driver = obj.vehicle.driver  # Set the driver to the vehicle's driver
        super().save_model(request, obj, form, change)

admin.site.register(VehicleInspection, VehicleInspectionAdmin)

admin.site.register(VehicleMaintenance, VehicleMaintenanceAdmin)
