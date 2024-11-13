from store.models import Ride, Vehicle,VehicleMaintenance, AvailableTime, SuccessfulAppointment, VehicleInspection
from django.shortcuts import render, get_object_or_404, Http404, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from category.models import Category
from accounts.models import Account
from geopy.distance import geodesic
from django.core.cache import cache
from accounts.models import Account, DriverProfile


from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from datetime import timedelta
from googlemaps import Client
import googlemaps
import requests
import json


from django.contrib.auth import get_user_model

User = get_user_model()


def store(request):

    vehicles = Vehicle.objects.all()

    context = {
        'vehicles': vehicles,
    }
    
    return render(request, 'store/store.html', context)


def vehicle_detail(request, pk):
    try:
        single_vehicle = Vehicle.objects.get(id=pk)

    except Vehicle.DoesNotExist:
        raise Http404("Vehicle does not exist")
    except Exception as e:
        raise e
        
    context = {
        'single_vehicle':single_vehicle,

    }
    return render(request, 'store/hospital_detail.html', context)



def appointment_form_detail(request, vehicle_id, available_time_id):
    available_time = get_object_or_404(AvailableTime, id=available_time_id)
    hospital_id = available_time.vehicle_id
    
    
    user_id = request.user.id  

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.vehicle_id = vehicle_id
            appointment.available_time_id = available_time_id
            appointment.user_id = user_id
            appointment.user_email = request.user.email


            successful_appointment = SuccessfulAppointment(
                hospital_id=hospital_id,
                available_time_id=available_time_id,
                user_id=user_id,
                user_email=request.user.email,
                phone_number=form.cleaned_data['phone_number'],
                note=form.cleaned_data['note']
            )
            successful_appointment.save()
            # DON'T FORGET TO CREATE THE FUNCTIONALITY TO DELETE ALL THE AVAILABLE TIMES THAT HAVE ELAPSED

            available_time.is_available = False
            available_time.save()

            appointment.save()
        return redirect('appointment_success', vehicle_id=vehicle_id, available_time_id=available_time_id, appointment_id=appointment.pk)
    else:
        form = AppointmentForm()
    
    context = {
        'form': form,
        'available_time': available_time,
        'vehicle_id': vehicle_id,
    }
    
    return render(request, 'store/appointment_form.html', context)


def appointment_success(request, vehicle_id, available_time_id, appointment_id):
    context = {
        'vehicle_id': vehicle_id,
        'available_time_id': available_time_id,
        'appointment_id': appointment_id,
    }
    return render(request, 'store/appointment_success.html', context)




# AIzaSyDz6PPs-S0jojUFcw7JbhGPdnrmp75F5FE
# LOCATION BASED SERVICES

def location(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)

    response_data = {
        'latitude': location_data['lat'],
        'longitude': location_data['lon']
    }

    hospitals = display_nearest_vehicles(latitude=location_data['lat'], longitude=location_data['lon'])

    return JsonResponse(hospitals, safe=False)




# @csrf_exempt
# def get_nearby_vehicles(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         latitude = data.get('latitude')
#         longitude = data.get('longitude')

#         print("Received latitude:", latitude)
#         print("Received longitude:", longitude)

#         vehicles = Vehicle.objects.all()
        

#         nearby_vehicles = []
#         processed_coordinates = set()  

#         # Iterate through each hospital
#         for vehicle in vehicles:
#             try:
#                 vehicle_latitude = float(vehicle.latitude)
#                 vehicle_longitude = float(vehicle.longitude)
#             except ValueError:
#                 continue  

#             if (vehicle_latitude, vehicle_longitude) in processed_coordinates:
#                 continue  

#             coordinate1 = (latitude, longitude)
#             coordinate2 = (vehicle_latitude, vehicle_longitude)
#             distance = geodesic(coordinate1, coordinate2).meters

#             vehicle_data = {
#                 'name': vehicle.vehicle_name,
#                 'latitude': vehicle_latitude,
#                 'longitude': vehicle_longitude,
#                 'user_latitude': latitude,  
#                 'user_longitude': longitude,
#                 'distance': distance
#             }
#             nearby_vehicles.append(vehicle_data)
#             processed_coordinates.add((vehicle_latitude, vehicle_longitude)) 

#         nearby_vehicles.sort(key=lambda x: x['distance'])

#         nearest_vehicles = nearby_vehicles[:70]

#         gmaps = googlemaps.Client(key='AIzaSyDz6PPs-S0jojUFcw7JbhGPdnrmp75F5FE')  

#         origins = [(latitude, longitude)]
#         destinations = [(vehicle['latitude'], vehicle['longitude']) for vehicle in nearest_vehicles]

#         batch_size = 25  #
#         batches = [destinations[i:i + batch_size] for i in range(0, len(destinations), batch_size)]

#         distances = []

#         # Perform distance matrix requests in batches
#         for batch in batches:
#             response = gmaps.distance_matrix(origins, batch, mode='driving')
#             for row in response['rows']:
#                 for element in row['elements']:
#                     distance = element['distance']['value']
#                     duration = round(element['duration']['value'] / 60)
#                     distances.append({'distance': distance, 'duration': duration})

#         for i, vehicle in enumerate(nearest_vehicles):
#             vehicle.update(distances[i]) 

#         nearest_vehicles.sort(key=lambda x: x['distance'])

#         twenty_nearest_vehicles= nearest_vehicles[:20]

#         for i, vehicle in enumerate(twenty_nearest_vehicles):
#             cache_key = f'vehicle_{i}'
#             print("cache_key",cache_key)
#             cache.set(cache_key, {
#                 'name': vehicle['name'],
#                 'latitude': vehicle['latitude'],
#                 'longitude': vehicle['longitude'],
#                 'user_latitude': vehicle['user_latitude'], 
#                 'user_longitude': vehicle['user_longitude'],
#                 'distance': vehicle['distance'],
#                 'duration': vehicle['duration'],
  
#             }, timeout=24*60*60)
#             print("Cache successful")
#         return JsonResponse({'twenty_nearest_vehicles': twenty_nearest_vehicles})
       
#     else:
#         return render(request, 'store/hospital_location.html')


# def display_nearest_vehicles(request):
#     cached_vehicles = []
#     for i in range(10):  
#         cache_key = f'vehicle_{i}'
#         vehicle_data = cache.get(cache_key)
#         # print("cached_hospital_data", hospital_data)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
#         if vehicle_data:
#             cached_vehicles.append(vehicle_data)  # Append vehicle data directly
#         else:
#             print(f"Hospital data for key '{cache_key}' is not cached.")

#     # Optionally, you can sort the cached hospitals by some criteria if needed
#     # cached_hospitals.sort(key=lambda x: x['distance_from_origin'])  # Adjust as per your sorting criteria

#     return render(request, 'store/display_nearest_hospitals.html', {'cached_vehicles': cached_vehicles})



@csrf_exempt
def display_nearest_vehicles(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)

    latitude = location_data['lat']
    longitude = location_data['lon']

    print("Received latitude:", latitude)
    print("Received longitude:", longitude)

    vehicles = Vehicle.objects.all()
    nearby_vehicles = []
    processed_coordinates = set()

    for vehicle in vehicles:
        try:
            vehicle_latitude = float(vehicle.latitude)
            vehicle_longitude = float(vehicle.longitude)
        except ValueError:
            continue

        if (vehicle_latitude, vehicle_longitude) in processed_coordinates:
            continue

        coordinate1 = (latitude, longitude)
        coordinate2 = (vehicle_latitude, vehicle_longitude)
        distance_meters = geodesic(coordinate1, coordinate2).meters
        distance_km = distance_meters / 1000  # Convert meters to kilometers
        ride_cost = distance_km * 50  # Calculate cost at 50 shillings per kilometer

        vehicle_data = {
            'name': vehicle.vehicle_name,
            'latitude': vehicle_latitude,
            'longitude': vehicle_longitude,
            'user_latitude': latitude,
            'user_longitude': longitude,
            'distance_km': round(distance_km, 2),  # Round for readability
            'ride_cost': round(ride_cost, 2),  # Round for readability
        }
        nearby_vehicles.append(vehicle_data)
        processed_coordinates.add((vehicle_latitude, vehicle_longitude))

    nearby_vehicles.sort(key=lambda x: x['distance_km'])
    nearest_vehicles = nearby_vehicles[:70]

    gmaps = googlemaps.Client(key='AIzaSyDz6PPs-S0jojUFcw7JbhGPdnrmp75F5FE')
    origins = [(latitude, longitude)]
    destinations = [(vehicle['latitude'], vehicle['longitude']) for vehicle in nearest_vehicles]

    batch_size = 25
    batches = [destinations[i:i + batch_size] for i in range(0, len(destinations), batch_size)]
    distances = []

    for batch in batches:
        response = gmaps.distance_matrix(origins, batch, mode='driving')
        for row in response['rows']:
            for element in row['elements']:
                distance = element['distance']['value']
                duration = round(element['duration']['value'] / 60)
                distances.append({'distance': distance, 'duration': duration})

    for i, vehicle in enumerate(nearest_vehicles):
        vehicle.update(distances[i])

    nearest_vehicles.sort(key=lambda x: x['distance_km'])
    twenty_nearest_vehicles = nearest_vehicles[:20]

    cached_vehicles = []
    for i, vehicle in enumerate(twenty_nearest_vehicles):
        cache_key = f'vehicle_{i}'
        vehicle['ride_cost'] = round(vehicle['distance_km'] * 50, 2)  # Ensure cost is added to cache

        # Attempt to cache the vehicle data
        success = cache.set(cache_key, vehicle, timeout=24*60*60)

        # Check if the cache was set successfully
        if success:
            print(f"Cache set successfully for key: {cache_key}")
        else:
            print(f"Cache set failed for key: {cache_key}")

        # Verify by retrieving it immediately
        cached_vehicle = cache.get(cache_key)
        if cached_vehicle:
            print(f"Cache retrieval successful for key: {cache_key}")
        else:
            print(f"Cache retrieval failed for key: {cache_key}")

        cached_vehicles.append(vehicle)

    return render(request, 'store/display_nearest_hospitals.html', {'cached_vehicles': cached_vehicles})




def plot_distance(request, vehicle_latitude, vehicle_longitude, user_latitude, user_longitude):
    context = {
        'vehicle_latitude': vehicle_latitude,
        'vehicle_longitude': vehicle_longitude,
        'user_latitude': user_latitude,
        'user_longitude': user_longitude,
    }

    print("vehicle_latitude", vehicle_latitude)
    print("vehicle_longitude", vehicle_longitude)
    print("user_latitude", user_latitude)
    print("user_longitude", user_longitude)

    return render(request, 'store/plot_distance.html', context)




@login_required
def user_admin_page(request):
    return render(request, 'accounts/user_dashboard')

  
# @login_required
# def doc_admin_page(request):
#     if request.user.is_authenticated and hasattr(request.user, 'is_doc'):
#         if request.method == 'POST':
#             form = DoctorTelemedicineAvailableTimeForm(request.POST)
#             if form.is_valid():
#                 doctor = request.user  # Get the IsDoctor instance related to the logged-in user
#                 print("doctor", doctor)
#                 time = form.cleaned_data['time']
#                 date = form.cleaned_data['date']
#                 is_available = form.cleaned_data['is_available']
#                 DoctorTelemedicineAvailableTime.objects.create(doctor = doctor,time = time , date = date, is_available=is_available)
#                 return redirect('accounts/success')  # Replace 'success_page' with the name of your success URL
#         else:
#             form = DoctorTelemedicineAvailableTimeForm()
#         return render(request, 'accounts/doc_dashboard.html', {'form': form})
#     elif request.user.is_authenticated:
#         return render(request, 'accounts/user_dashboard.html')
#     else:
#         return redirect('login')  # Use named URL for login page

# @login_required
# def doc_admin_page(request):
#     if request.user.is_authenticated and request.user.is_doc:
#         if request.method == 'POST':
#             form = DoctorTelemedicineAvailableTimeForm(request.POST)
#             if form.is_valid():
#                 doctor = request.user 
#                 time = form.cleaned_data['time']
#                 date = form.cleaned_data['date']
#                 is_available = form.cleaned_data['is_available']
#                 DoctorTelemedicineAvailableTime.objects.create(
#                     doctor= doctor,
#                     time=time,
#                     date=date,
#                     is_available=is_available
#                 )
#                 return render(request, 'accounts/doc_success_appointment.html')
#         else:
#             form = DoctorTelemedicineAvailableTimeForm()
#         return render(request, 'accounts/doc_dashboard.html', {'form': form})
#     elif request.user.is_authenticated:
#         return render(request, 'accounts/user_dashboard.html')
#     else:
#         return redirect('login') 

@login_required
def driver_success_appointment(request):
    return render(request, 'accounts/doc_success_appointment.html')


@login_required
def drivers(request):
    all_users = Account.objects.all()
    drivers = all_users.filter(is_driver = True)
    context = {
        "drivers":drivers
    }
    return render(request, "store/all_doctors.html", context)


# def doc_detail(request, pk):
#     try:
#         single_doc = get_object_or_404(Account, pk=pk)
#         available_appointments = DoctorTelemedicineAvailableTime.objects.filter(doctor=single_doc, is_available=True)

#     except Account.DoesNotExist:
#         raise Http404("Account does not exist")
#     except Exception as e:
#         raise e
        
#     context = {
#         'single_doc':single_doc,
#         'available_appointments': available_appointments,

#     }
#     return render(request, 'store/doc_detail.html', context)





def driver_detail(request, pk):
    try:
        single_diver = get_object_or_404(Account, pk=pk)
        driver_profile = None
        if single_diver.is_driver:
            try:
                driver_profile = DriverProfile.objects.get(user=single_diver)
            except DriverProfile.DoesNotExist:
                driver_profile = None

    except Account.DoesNotExist:
        raise Http404("Account does not exist")
    except Exception as e:
        raise e
        
    context = {
        'single_diver': single_diver,
        'driver_profile': driver_profile,
    }
    return render(request, 'store/doc_detail.html', context)

# def book_appointment(request, pk):
#     try:
#         appointment = get_object_or_404(DoctorTelemedicineAvailableTime, id=pk, is_available=True)
#         if request.method == 'GET':
#             appointment.is_available = False
#             appointment.save()
#             return HttpResponse(" You have made a successfull appointment ")
#             # return redirect('appointment_success')
#     except DoctorTelemedicineAvailableTime.DoesNotExist:
#         return redirect('error_page')


from django.utils.timezone import now


def book_vehicle(request, user_latitude, user_longitude, vehicle_latitude, vehicle_longitude):
    # Retrieve the vehicle using its latitude and longitude
    vehicle = get_object_or_404(Vehicle, latitude=str(vehicle_latitude), longitude=str(vehicle_longitude))

    # Check if the vehicle is available
    if not vehicle.vehicle_available:
        return HttpResponse("Sorry, this vehicle is already booked.", status=400)

    # Calculate the distance between the user and the vehicle (in kilometers)
    coordinate1 = (user_latitude, user_longitude)
    coordinate2 = (vehicle_latitude, vehicle_longitude)
    distance_meters = geodesic(coordinate1, coordinate2).meters
    distance_km = distance_meters / 1000  # Convert to kilometers

    # Calculate the cost (50 shillings per kilometer)
    ride_cost = distance_km * 50  # 50 shillings per kilometer

    # Calculate the duration (example: 1 minute per 50 meters, adjust as needed)
    ride_duration = int(distance_meters / 50)  # Duration in minutes (simple estimate)

    # Get the driver of the vehicle directly from the vehicle's driver field
    driver = vehicle.driver

    # Create the Ride object and save it to the database
    ride = Ride.objects.create(
        user_id=request.user.id,  # Save the user's primary key
        vehicle=vehicle,
        driver=driver,  # Saving the driver from the vehicle
        start_latitude=user_latitude,
        start_longitude=user_longitude,
        end_latitude=vehicle_latitude,
        end_longitude=vehicle_longitude,
        distance_km=round(distance_km, 2),
        cost=round(ride_cost, 2),
        duration_minutes=ride_duration,
        ride_time=now(),
        status='active',  # Mark the ride as active
    )

    # Optionally, mark the vehicle as unavailable
    vehicle.vehicle_available = False
    vehicle.save()

    # Prepare the context to display in the booking confirmation page
    context = {
        'vehicle': vehicle,
        'user_latitude': user_latitude,
        'user_longitude': user_longitude,
        'vehicle_latitude': vehicle_latitude,
        'vehicle_longitude': vehicle_longitude,
        'distance_km': round(distance_km, 2),
        'ride_cost': round(ride_cost, 2),
        'ride_duration': ride_duration,
        'ride_time': ride.ride_time,
        'driver': driver,  # Directly show the driver's information
    }

    # Render the page where the user can confirm the booking details
    return render(request, 'store/book_vehicle.html', context)





@login_required

def driver_dashboard(request):
    user = request.user
    if user.is_driver:
        booked_vehicles = Vehicle.objects.filter(driver=user, vehicle_available=False)
        rides = Ride.objects.filter(driver=user, status='active')

        scheduled_maintenance = VehicleMaintenance.objects.filter(driver=user, maintenance_done=False)
        scheduled_inspection = VehicleInspection.objects.filter(driver=user, inspection_done=False)
    else:
        scheduled_maintenance = []  # No maintenance for non-drivers
    # Fetch the vehicles that belong to the logged-in user
    driver_vehicles = Vehicle.objects.filter(driver=request.user)

    context = {
        'user_vehicles': driver_vehicles,
        'scheduled_maintenance': scheduled_maintenance,
        'scheduled_inspection': scheduled_inspection,
        'booked_vehicles': booked_vehicles,
        'rides': rides
    
    }
    return render(request, 'store/driver_dashboard.html', context)



@login_required
@csrf_exempt
def update_vehicle_status(request, vehicle_id):
    if request.method == 'POST':
        try:
            # Get the specific vehicle by ID and check if the logged-in user is the driver
            vehicle = Vehicle.objects.get(id=vehicle_id, driver=request.user)

            # Mark the vehicle as available
            vehicle.vehicle_available = True
            vehicle.save()

            return JsonResponse({'success': True, 'message': 'Vehicle status updated successfully'})
        except Vehicle.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Vehicle not found or unauthorized access'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

