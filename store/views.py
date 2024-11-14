from store.models import Earnings, Ride, CostManagement,Vehicle,VehicleMaintenance, VehicleInspection
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
from accounts.models import Account


from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from datetime import timedelta
from googlemaps import Client
import googlemaps
import requests
from django.utils import timezone
from django.utils.timezone import now

import json

GOOGLE_API_KEY = 'AIzaSyDz6PPs-S0jojUFcw7JbhGPdnrmp75F5FE'

import logging

logger = logging.getLogger(__name__)


from django.contrib.auth import get_user_model

User = get_user_model()


def store(request):

    vehicles = Vehicle.objects.all()

    context = {
        'vehicles': vehicles,
    }
    
    return render(request, 'store/store.html', context)


def about(request):
    return render(request, 'store/about.html')


def contact_us(request):
    return render(request, 'store/contact.html')

@login_required
def vehicle_detail(request, pk):
    try:
        single_vehicle = Vehicle.objects.get(id=pk)
        vehicle_maintenance = VehicleMaintenance.objects.filter(driver=single_vehicle.driver)
        vehicle_inspection = VehicleInspection.objects.filter(driver=single_vehicle.driver)
        print(vehicle_maintenance)


    except Vehicle.DoesNotExist:
        raise Http404("Vehicle does not exist")
    except Exception as e:
        raise e
        
    context = {
        'single_vehicle':single_vehicle,
        'vehicle_maintenance':vehicle_maintenance,
        'vehicle_inspection':vehicle_inspection

    }
    return render(request, 'store/vehicle_detail.html', context)

@login_required

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



@csrf_exempt
def display_nearest_vehicles(request):
    # Get user's location from IP
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)

    latitude = location_data['lat']
    longitude = location_data['lon']

    print("Received latitude:", latitude)
    print("Received longitude:", longitude)

    # Filter vehicles that are available
    vehicles = Vehicle.objects.filter(vehicle_available=True)
    nearby_vehicles = []
    processed_coordinates = set()

    for vehicle in vehicles:
        try:
            vehicle_latitude = float(vehicle.latitude)
            vehicle_longitude = float(vehicle.longitude)
        except ValueError:
            continue

        # Skip duplicate coordinates
        if (vehicle_latitude, vehicle_longitude) in processed_coordinates:
            continue

        # Calculate distance and cost
        coordinate1 = (latitude, longitude)
        coordinate2 = (vehicle_latitude, vehicle_longitude)
        distance_meters = geodesic(coordinate1, coordinate2).meters
        distance_km = distance_meters / 1000
        ride_cost = distance_km * 50

        vehicle_data = {
            'name': vehicle.vehicle_name,
            'latitude': vehicle_latitude,
            'longitude': vehicle_longitude,
            'user_latitude': latitude,
            'user_longitude': longitude,
            'distance_km': round(distance_km, 2),
            'ride_cost': round(ride_cost, 2),
        }
        nearby_vehicles.append(vehicle_data)
        processed_coordinates.add((vehicle_latitude, vehicle_longitude))

    # Sort and get nearest 70 vehicles
    nearby_vehicles.sort(key=lambda x: x['distance_km'])
    nearest_vehicles = nearby_vehicles[:70]

    # Get driving distances using Google Maps API
    gmaps = googlemaps.Client(key='AIzaSyDz6PPs-S0jojUFcw7JbhGPdnrmp75F5FE')
    origins = [(latitude, longitude)]
    destinations = [(vehicle['latitude'], vehicle['longitude']) for vehicle in nearest_vehicles]

    # Process in batches of 25 to respect API limits
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

    # Update vehicles with Google Maps distance data
    for i, vehicle in enumerate(nearest_vehicles):
        vehicle.update(distances[i])

    # Get final 20 nearest vehicles
    nearest_vehicles.sort(key=lambda x: x['distance_km'])
    twenty_nearest_vehicles = nearest_vehicles[:20]

    return render(request, 'store/display_nearest_vehicles.html', {'vehicles': twenty_nearest_vehicles})
@login_required
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


from django.utils import timezone
from django.db.models import Sum
from .models import Earnings

@login_required
def drivers(request):
    drivers = Account.objects.filter(is_driver=True)
    drivers_with_earnings = []

    for driver in drivers:
        # Get today's earnings
        today = timezone.now().date()
        earnings_today = Earnings.objects.filter(driver=driver, date=today).first()
        daily_earnings = earnings_today.daily_earnings if earnings_today else 0

        # Get cumulative earnings
        cumulative_earnings = Earnings.objects.filter(driver=driver).aggregate(Sum('total_earnings'))['total_earnings__sum'] or 0

        drivers_with_earnings.append({
            'driver': driver,
            'daily_earnings': daily_earnings,
            'total_earnings': cumulative_earnings,
        })

    context = {
        "drivers": drivers_with_earnings,
    }
    return render(request, "store/all_drivers.html", context)




@login_required
def driver_dashboard(request):
    user = request.user
    if user.is_driver:
        booked_vehicles = Vehicle.objects.filter(driver=user, vehicle_available=False)
        rides = Ride.objects.filter(driver=user, status='active')
        scheduled_maintenance = VehicleMaintenance.objects.filter(driver=user, maintenance_done=False)
        scheduled_inspection = VehicleInspection.objects.filter(driver=user, inspection_done=False)

        # Get the current day's earnings and total earnings for the driver
        today_earnings = Earnings.objects.filter(driver=user, date=timezone.now().date()).first()
        total_earnings = Earnings.objects.filter(driver=user).order_by('-date').first()

        # Fallback if no earnings records are found
        daily_earnings_amount = today_earnings.daily_earnings if today_earnings else 0.00
        total_earnings_amount = total_earnings.total_earnings if total_earnings else 0.00

    else:
        scheduled_maintenance = []  # No maintenance for non-drivers
        daily_earnings_amount = 0.00
        total_earnings_amount = 0.00

    driver_vehicles = Vehicle.objects.filter(driver=request.user)

    context = {
        'user_vehicles': driver_vehicles,
        'scheduled_maintenance': scheduled_maintenance,
        'scheduled_inspection': scheduled_inspection,
        'booked_vehicles': booked_vehicles,
        'rides': rides,
        'daily_earnings': daily_earnings_amount,
        'total_earnings': total_earnings_amount,
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


# Define Google API Key directly in views

# Configure logging directly in views
log_file = 'ride_distances.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_current_location():
    """
    Get current location using Google Maps Geolocation API
    Returns latitude and longitude
    """
    url = 'https://www.googleapis.com/geolocation/v1/geolocate'
    
    params = {
        'key': GOOGLE_API_KEY
    }
    
    try:
        response = requests.post(url, json={}, params=params)
        data = response.json()
        
        if 'location' in data:
            latitude = data['location']['lat']
            longitude = data['location']['lng']
            logger.info(f"Successfully got current location: ({latitude}, {longitude})")
            return {
                'success': True,
                'latitude': latitude,
                'longitude': longitude
            }
        else:
            logger.error(f"Geolocation API error: {data.get('error', {}).get('message')}")
            return {'success': False, 'error': 'Could not determine location'}
            
    except Exception as e:
        logger.error(f"Error calling Geolocation API: {str(e)}")
        return {'success': False, 'error': str(e)}

def get_distance_matrix(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Get distance and duration using Google Distance Matrix API
    Returns distance in meters and duration in seconds
    """
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    
    params = {
        'origins': f'{origin_lat},{origin_lng}',
        'destinations': f'{dest_lat},{dest_lng}',
        'mode': 'driving',
        'departure_time': 'now',  # For real-time traffic
        'key': GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            result = data['rows'][0]['elements'][0]
            
            if result['status'] == 'OK':
                distance = result['distance']['value']  # Distance in meters
                duration = result['duration']['value']  # Duration in seconds
                duration_in_traffic = result.get('duration_in_traffic', {}).get('value', duration)  # Duration with traffic
                
                logger.info(f"""
                    Distance Matrix API Results:
                    From: ({origin_lat}, {origin_lng})
                    To: ({dest_lat}, {dest_lng})
                    Distance: {distance/1000:.2f} km
                    Normal Duration: {duration/60:.2f} minutes
                    Duration in Traffic: {duration_in_traffic/60:.2f} minutes
                """)
                
                return {
                    'distance': distance,
                    'duration': duration,
                    'duration_in_traffic': duration_in_traffic,
                    'success': True
                }
            else:
                logger.error(f"Route calculation failed: {result['status']}")
                return {'success': False, 'error': 'Route calculation failed'}
        else:
            logger.error(f"Distance Matrix API error: {data['status']}")
            return {'success': False, 'error': 'Distance Matrix API error'}
            
    except Exception as e:
        logger.error(f"Error calling Distance Matrix API: {str(e)}")
        return {'success': False, 'error': str(e)}

def get_place_details(place_id):
    """Get detailed information about a place using its place_id"""
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'place_id': place_id,
        'fields': 'geometry,formatted_address,name',
        'key': GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            logger.info(f"Successfully retrieved place details for place_id: {place_id}")
            return data
        else:
            logger.error(f"Place Details API error: {data['status']}")
            return None
            
    except Exception as e:
        logger.error(f"Error calling Place Details API: {str(e)}")
        return None

@login_required
def book_vehicle(request, vehicle_latitude, vehicle_longitude):
    vehicle = get_object_or_404(Vehicle, latitude=str(vehicle_latitude), longitude=str(vehicle_longitude))

    if not vehicle.vehicle_available:
        logger.warning(f"Attempt to book unavailable vehicle ID: {vehicle.id}")
        return HttpResponse("This vehicle is currently unavailable.", status=400)

    # Get current location using Google Geolocation API
    current_location = get_current_location()
    if not current_location['success']:
        return HttpResponse("Unable to determine your location. Please try again.", status=400)
    
    user_latitude = current_location['latitude']
    user_longitude = current_location['longitude']

    if request.method == 'POST':
        place_id = request.POST.get('place_id')
        if not place_id:
            logger.error("Missing place_id in booking request")
            return HttpResponse("Please select a valid destination.", status=400)

        # Get place details from Google Places API
        place_details = get_place_details(place_id)
        if not place_details or 'result' not in place_details:
            return HttpResponse("Unable to process destination. Please try again.", status=400)

        location = place_details['result']['geometry']['location']
        end_latitude = location['lat']
        end_longitude = location['lng']
        destination_name = place_details['result']['formatted_address']

        # Get distance and duration from Distance Matrix API
        matrix_result = get_distance_matrix(
            user_latitude, 
            user_longitude, 
            end_latitude, 
            end_longitude
        )

        if not matrix_result['success']:
            logger.error(f"Distance Matrix API error: {matrix_result.get('error')}")
            return JsonResponse({
                'success': False,
                'error': 'Unable to calculate route. Please try again.'
            }, status=400)

        # Calculate fare
        rate_km_one = get_object_or_404(CostManagement)
        rate_km = rate_km_one.cost_per_km

        BASE_FARE = 100  # Base fare in shillings
        PER_KM_RATE = rate_km  # Rate per kilometer
        SURGE_MULTIPLIER = 1.0  # Can be adjusted based on demand
        
        distance_km = matrix_result['distance'] / 1000
        duration_minutes = matrix_result['duration_in_traffic'] / 60
        
        # Fare calculation with surge pricing and traffic consideration
        ride_cost = (BASE_FARE + 
                    (distance_km * PER_KM_RATE) + 
                    (duration_minutes * 2))  # 2 shillings per minute
        ride_cost *= SURGE_MULTIPLIER

        logger.info(f"""
            Ride Booking Details:
            User ID: {request.user.id}
            From: ({user_latitude}, {user_longitude})
            To: {destination_name} ({end_latitude}, {end_longitude})
            Distance: {distance_km:.2f} km
            Duration: {duration_minutes:.2f} minutes
            Cost: KES {ride_cost:.2f}
        """)

        try:
            # Create ride record
            ride = Ride.objects.create(
                user=request.user,
                vehicle=vehicle,
                driver=vehicle.driver,
                start_latitude=user_latitude,
                start_longitude=user_longitude,
                end_latitude=end_latitude,
                end_longitude=end_longitude,
                destination_name=destination_name,
                distance_km=round(distance_km, 2),
                cost=round(ride_cost, 2),
                duration_minutes=round(duration_minutes),
                ride_time=now(),
                status='pending'
            )


            vehicle.save()

            logger.info(f"Successfully created ride ID: {ride.id}")

            return JsonResponse({
                'success': True,
                'ride_id': ride.id,
                'estimated_cost': round(ride_cost, 2),
                'estimated_duration': round(duration_minutes),
                'distance': round(distance_km, 2),
                'redirect_url': reverse('ride_confirmation', kwargs={'ride_id': ride.id})
            })

        except Exception as e:
            logger.error(f"Error creating ride: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    context = {
        'vehicle': vehicle,
        'user_latitude': user_latitude,
        'user_longitude': user_longitude,
        'google_api_key': GOOGLE_API_KEY,
    }

    return render(request, 'store/book_vehicle.html', context)



# views.py
@login_required
def ride_confirmation(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, user=request.user)
    

    # Retrieve the vehicle associated with the ride
    vehicle = ride.vehicle


    if request.method == 'POST' and ride.status == 'pending':
        ride.status = 'active'
        ride.save()

        vehicle.vehicle_available = False
        vehicle.save()


        logger.info(f"Ride {ride_id} status updated to active and vehicle {vehicle.id} set to unavailable")
        return JsonResponse({'success': True, 'message': 'Ride activated successfully'})
    
    context = {
        'ride': ride,
        'google_api_key': GOOGLE_API_KEY,
        'start_latitude': ride.start_latitude,
        'start_longitude': ride.start_longitude,
        'end_latitude': ride.end_latitude,
        'end_longitude': ride.end_longitude,
            #         vehicle.vehicle_available = False
            # vehicle.save()
    }
    
    return render(request, 'store/ride_confirmation.html', context)


@login_required
def mark_ride_completed(request, ride_id):
    # Fetch the ride and ensure it belongs to the driver
    ride = get_object_or_404(Ride, id=ride_id, driver=request.user)

    if request.method == 'POST' and ride.status == 'active':
        # Mark the ride as completed
        ride.status = 'completed'
        ride.save()

        # Log the earnings into both daily and total earnings
        earnings, created = Earnings.objects.get_or_create(
            driver=request.user,
            date=timezone.now().date()  # Date of the ride
        )

        # Add the ride's cost to both daily and total earnings
        earnings.add_earning(ride.cost)

        return JsonResponse({'success': True, 'message': 'Ride marked as completed and earnings logged successfully.'})

    return JsonResponse({'success': False, 'message': 'Ride cannot be marked as completed.'})


def user_dashboard(request):
    active_ride = Ride.objects.filter(user=request.user, status='active').first()
    messages = CostManagement.objects.all()
    context = {
        'active_ride': active_ride,
        'messages': messages,
    }
    return render(request, 'store/user_dashboard.html', context)