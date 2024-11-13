from django.shortcuts import render, get_object_or_404, redirect
from store.models import Hospital,Vehicle
from category.models import Category
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from googlemaps import Client
import googlemaps
import math
import requests
import json


# Create your views here.

def store(request, category_slug=None):
    categories = None
    hospitals = None

    if category_slug !=None:
        categories = get_object_or_404(Category, slug=category_slug)
        hospitals = Hospital.objects.all().filter(category = categories, is_available=True)
    else:
        hospitals = Hospital.objects.all().filter(is_available=True)
    context = {
        'hospitals': hospitals,
    }
    
    return render(request, 'store/store.html', context)


def hospital_detail(request, category_slug, product_slug):
    try:
        single_product = Hospital.objects.get(category__slug=category_slug,slug=product_slug)
        
    except Exception as e:
        raise e
        
    context = {
        'single_product':single_product,
    }
    return render(request, 'store/hospital_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            hospitals = Hospital.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = hospitals.count()

    context = {
        'hospitals':hospitals,
        'product_count':product_count
    }
    return render(request, 'store/store.html', context)




# def location(request):
#     ip = requests.get('https://api.ipify.org?format=json')
#     # print('ip', ip)
#     ip_data = json.loads(ip.text)
#     res = requests.get('http://ip-api.com/json/'+ip_data["ip"])
#     location_data_one = res.text
#     location_data = json.loads(location_data_one)
#     context = {
#         'data': location_data
#     }
#     print("latitude",location_data['lat'])
#     print("longitude",location_data['lon'])
#     # print("latitude",data.lat)
#     return 

from django.http import JsonResponse

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

    hospitals = get_nearby_hospitals(latitude=location_data['lat'], longitude=location_data['lon'])

    return JsonResponse(hospitals, safe=False)

    
    # def hospitals_location(request):
    # # Get the latitude and longitude from the request
    #     latitude = -1.2841
    #     longitude = 36.8155
    #     # latitude = float(request.GET.get('latitude'))
    #     # longitude = float(request.GET.get('longitude'))

    #     # Call the get_nearby_hospitals function
    #     hospitals = get_nearby_hospitals(latitude, longitude)

    #     # Return the hospitals as a JSON response
    #     return JsonResponse({'hospitals': hospitals})




# def get_nearby_hospitals(latitude, longitude):
#     gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

#     # Perform a nearby search for hospitals
#     result = gmaps.places_nearby(
#         location=(latitude, longitude),
#         radius=2000,
#         keyword='hospital',
#         type='hospital'
#     )

#     # Extract the necessary information from the results
#     hospitals = []
#     for place in result.get('results', []):
#         name = place.get('name')
#         # print("name", name)

#         address = place.get('vicinity')

#         db_hospital = Hospital.objects.all().filter(hospital_name = 'Aga khan Hospital').values()
#         print("db_hospital", db_hospital)

#         hospitals.append({'name': name, 'address': address})
#         print()

#     return hospitals




from django.shortcuts import get_list_or_404


def get_nearby_hospitals(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)


    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    # Perform a nearby search for hospitals
    result = gmaps.places_nearby(
        location=(location_data['lat'], location_data['lon']),
        radius=2000,
        keyword='hospital',
        type='hospital'
    )

    # Extract the necessary information from the results
    hospitals = []
    for place in result.get('results', []):
        name = place.get('name')
        address = place.get('vicinity')


        hospitals.append({'name': name, 'address': address})
        print('hospitals', hospitals)

    return JsonResponse(hospitals, safe=False)



def get_vacancy_available_hospitals(request):
    database_hospitals = Hospital.objects.filter(vacancies_available=True)
    vacancy_available_hospitals = []
    
    for hospital in database_hospitals:
        vacancy_available_hospitals.append({
            'name': hospital.hospital_name,
            'address': hospital.location,
            'ambulance_contacts': hospital.ambulance_contacts
        })

    return vacancy_available_hospitals


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from googlemaps import Client
from .models import Hospital

# @csrf_exempt
# def get_nearby_vacancy_available_hospitals(request):
#     ip = requests.get('https://api.ipify.org?format=json')
#     ip_data = json.loads(ip.text)
#     res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
#     location_data_one = res.text
#     location_data = json.loads(location_data_one)
#     gmaps = Client(key=settings.GOOGLE_MAPS_API_KEY)

#     # Get the user's location
#     user_location = location_data

#     # Get the list of all hospitals within a certain radius of the user's location
#     result = gmaps.places_nearby(
#         location=(user_location['lat'], user_location['lon']),
#         radius=2000,
#         keyword='hospital',
#         type='hospital'
#     )

#     # Filter the list of hospitals based on the vacancyavailable boolean
#     vacancy_available_hospitals = []
#     for place in result.get('results', []):
#         name = place.get('name')
#         address = place.get('vicinity')
#         try:
#             hospital = Hospital.objects.get(hospital_name=name)
#             if hospital.vacancies_available:
#                 vacancy_available_hospitals.append({'name': name, 'address': address})
#         except Hospital.DoesNotExist:
#             # Handle the case when the hospital is not found in the database
#             pass

#     # Return the list of nearby vacancy available hospitals
#     return JsonResponse(vacancy_available_hospitals, safe=False)

# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import requests
# from googlemaps import Client
# from .models import Hospital

# @csrf_exempt
# def get_nearby_vacancy_available_hospitals(request):
#     ip = requests.get('https://api.ipify.org?format=json')
#     ip_data = json.loads(ip.text)
#     res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
#     location_data_one = res.text
#     location_data = json.loads(location_data_one)
#     gmaps = Client(key=settings.GOOGLE_MAPS_API_KEY)

#     # Get the user's location
#     user_location = location_data

#     # Get the list of all hospitals within a certain radius of the user's location
#     result = gmaps.places_nearby(
#         location=(user_location['lat'], user_location['lon']),
#         radius=2000,
#         keyword='hospital',
#         type='hospital'
#     )

#     # Filter the list of hospitals based on the vacancyavailable boolean
#     vacancy_available_hospitals = []
#     for place in result.get('results', []):
#         name = place.get('name')
#         address = place.get('vicinity')
#         try:
#             hospital = Hospital.objects.get(hospital_name=name)
#             if hospital.vacancies_available:
#                 hospital_data = {'name': name, 'address': address}
#                 if hospital.ambulance_available:
#                     hospital_data['ambulance_contacts'] = hospital.ambulance_contacts
#                 vacancy_available_hospitals.append(hospital_data)
#         except Hospital.DoesNotExist:
#             # Handle the case when the hospital is not found in the database
#             pass

#     # Return the list of nearby vacancy available hospitals
#     return JsonResponse(vacancy_available_hospitals, safe=False)


@csrf_exempt
def get_nearby_vacancy_available_hospitals(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    gmaps = Client(key=settings.GOOGLE_MAPS_API_KEY)

    # Get the user's location
    user_location = location_data

    # Get the list of all hospitals within a certain radius of the user's location
    result = gmaps.places_nearby(
        location=(user_location['lat'], user_location['lon']),
        radius=2000,
        keyword='hospital',
        type='hospital'
    )

    # Filter the list of hospitals based on the vacancyavailable boolean
    vacancy_available_hospitals = []
    for place in result.get('results', []):
        name = place.get('name')
        address = place.get('vicinity')
        try:
            hospital = Hospital.objects.get(hospital_name=name)
            if hospital.vacancies_available:
                hospital_data = {'name': name, 'address': address}
                if hospital.ambulance_available:
                    # Check if the hospital already exists in the list
                    existing_hospital = next(
                        (
                            h
                            for h in vacancy_available_hospitals
                            if h['name'] == name and h['address'] == address
                        ),
                        None
                    )
                    if existing_hospital:
                        # Update the ambulance_contacts field if the hospital already exists
                        existing_hospital['ambulance_contacts'] = hospital.ambulance_contacts
                    else:
                        # Append a new hospital to the list if it doesn't exist
                        hospital_data['ambulance_contacts'] = hospital.ambulance_contacts
                        vacancy_available_hospitals.append(hospital_data)
        except Hospital.DoesNotExist:
            # Handle the case when the hospital is not found in the database
            pass

    # Return the list of nearby vacancy available hospitals
    return JsonResponse(vacancy_available_hospitals, safe=False)


# VEHICLES
import math
from django.http import JsonResponse

def get_nearest_vehicle(request):
    user_location = get_user_location(request)
    user_latitude = user_location['latitude']
    user_longitude = user_location['longitude']

    # Get the nearest available vehicle
    nearest_vehicle = None
    nearest_distance = math.inf

    available_vehicles = Vehicle.objects.filter(availability=True)
    for vehicle in available_vehicles:
        distance = calculate_distance(user_latitude, user_longitude, vehicle.latitude, vehicle.longitude)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_vehicle = vehicle

    if nearest_vehicle:
        vehicle_info = {
            'vehicle_type': nearest_vehicle.vehicle_type,
            'latitude': nearest_vehicle.latitude,
            'longitude': nearest_vehicle.longitude,
            'contact': nearest_vehicle.contact,
            'distance': nearest_distance
        }
        return JsonResponse(vehicle_info)

    return JsonResponse({'message': 'No available vehicles nearby.'})


def get_user_location(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)

    user_location = {
        'latitude': location_data['lat'],
        'longitude': location_data['lon']
    }

    return user_location


def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert coordinates to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    earth_radius = 6371  # Radius of the Earth in kilometers
    distance_km = earth_radius * c
    distance_m = distance_km * 1000  # Convert distance to meters

    return distance_m



