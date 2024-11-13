from django.shortcuts import render, get_object_or_404, redirect
from store.models import Hospital,Vehicle,Doctor,Service,ServiceProvided, PaymentService, Appointment, HospitalService
from accounts.models import Account
from math import radians, sin, cos, sqrt, atan2
from category.models import Category
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
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
        hospitals = Hospital.objects.all()
    context = {
        'hospitals': hospitals,
    }
    
    return render(request, 'store/store.html', context)


def hospital_detail(request, pk):
    try:
        single_hospital = Hospital.objects.get(id=pk)
        
    except Exception as e:
        raise e
        
    context = {
        'single_hospital':single_hospital,
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

    hospitals = get_nearby_hospitals(latitude=location_data['lat'], longitude=location_data['lon'])

    return JsonResponse(hospitals, safe=False)

def get_distance_matrix(origins, destinations, api_key="AIzaSyDz6PPs-S0jojUFcw7JbhGPdnrmp75F5FE"):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origins}&destinations={destinations}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    return data

@csrf_exempt
def get_nearby_hospitals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        print(latitude)
        print(longitude)
        
        # Retrieve hospitals from the database
        hospitals = Hospital.objects.all()  # Assuming Hospital is your model
        nearby_hospitals = []
        
        for hospital in hospitals:
            try:
                hospital_latitude = float(hospital.latitude)
                hospital_longitude = float(hospital.longitude)
            except ValueError:
                continue  # Skip this hospital if latitude or longitude is invalid
            
            destination = f"{hospital_latitude},{hospital_longitude}"
            data = get_distance_matrix(f"{latitude},{longitude}", destination, "Your API Key")
            distance = data['rows'][0]['elements'][0]['distance']['text']
            duration = data['rows'][0]['elements'][0]['duration']['text']
            
            hospital_data = {
                'name': hospital.hospital_name,
                'address': hospital.hospital_address,
                'distance': distance,
                'duration': duration
            }
            nearby_hospitals.append(hospital_data)
        
        # Sort hospitals by distance
        nearby_hospitals.sort(key=lambda x: x['distance'])
        print("nearby_hospitals", nearby_hospitals[0:10])
        
        # Return the list of nearby hospitals
        return JsonResponse({'hospitals': nearby_hospitals, 'status': 'success'})
    
    else:
        return render(request, 'store/hospital_location.html')



# def calculate_distance(lat1, lon1, lat2, lon2):
#     # Convert coordinates to radians
#     lat1 = radians(lat1)
#     lon1 = radians(lon1)
#     lat2 = radians(lat2)
#     lon2 = radians(lon2)

#     # Haversine formula
#     dlon = lon2 - lon1
#     dlat = lat2 - lat1
#     a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#     c = 2 * atan2(sqrt(a), sqrt(1-a))
#     distance = 6371 * c  # Radius of the Earth in kilometers

#     return distance

# @csrf_exempt
# def get_nearby_hospitals(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         latitude = data.get('latitude')
#         longitude = data.get('longitude')

#         print(latitude)
#         print(longitude)


#         # Retrieve hospitals from the database
#         hospitals = Hospital.objects.all()
#         nearby_hospitals = []

#         for hospital in hospitals:
#             try:
#                 hospital_latitude = float(hospital.latitude)

#                 hospital_longitude = float(hospital.longitude)
#             except ValueError:
#                 continue  # Skip this hospital if latitude or longitude is invalid

#             distance = calculate_distance(latitude, longitude, hospital_latitude, hospital_longitude)
#             hospital_data = {
#                 'name': hospital.hospital_name,
#                 'address': hospital.hospital_address,
#                 'distance': distance
#             }
#             nearby_hospitals.append(hospital_data)

#         # Sort hospitals by distance
#         nearby_hospitals.sort(key=lambda x: x['distance'])
#         print("nearby_hospitals", nearby_hospitals[0:10])

#         # Return the list of nearby hospitals
#         return JsonResponse({'hospitals': nearby_hospitals, 'status': 'success'})
#     else:
#         return render(request, 'store/hospital_location.html')



import csv
import os
from django.conf import settings

# def read_csv_data(request):
#     csv_file = os.path.join(settings.BASE_DIR, 'hosi.csv')
#     existing_hospitals = []

#     with open(csv_file, 'r') as file:
#         reader = csv.reader(file)

#         for row in reader:
#             longitude = row[0]
#             latitude = row[1]
#             hospital_name = row[2]
#             hospital_address = row[4]
#             placepageUri = row[6]

#             # Check if a hospital with the same name already exists in the database
#             existing_hospital = Hospital.objects.filter(hospital_name=hospital_name).first()

#             if existing_hospital:
#                 existing_hospitals.append(existing_hospital)

#     return HttpResponse(existing_hospitals)

# def read_csv_data(request):
#     csv_file = os.path.join(settings.BASE_DIR, 'latestmerged.csv')

#     with open(csv_file, 'r') as file:
#         reader = csv.reader(file)

#         for row in reader:
#             longitude = row[0]
#             latitude = row[1]
#             hospital_name = row[2]
#             hospital_address = row[4]
#             placepageUri = row[6]

#             # Check if a hospital with the same name already exists in the database
#             existing_hospital = Hospital.objects.filter(hospital_name=hospital_name).first()
#             # print("existing_hospital", existing_hospital)

#             if existing_hospital:
#                 # Hospital already exists, update its details
#                 existing_hospital.longitude = longitude
#                 existing_hospital.latitude = latitude
#                 existing_hospital.hospital_address = hospital_address
#                 existing_hospital.placepageUri = placepageUri
#                 existing_hospital.save()
#             else:
#                 # Hospital does not exist, create a new object and save it
#                 new_hospital = Hospital(
#                     hospital_name=hospital_name,
#                     hospital_address=hospital_address,
#                     longitude=longitude,
#                     latitude=latitude,
#                     placepageUri=placepageUri
#                 )
#                 new_hospital.save()

#     return HttpResponse("successfull")

def read_csv_data(request):
    # Construct the file path to the CSV file
    csv_file = os.path.join(settings.BASE_DIR, 'data.csv')

    # Open the CSV file
    with open(csv_file, 'r') as file:
        # Create a CSV reader object
        reader = csv.reader(file)

        # Process each row in the CSV file
        for row in reader:
            # Access the data in each row
            longitude = row[0]
            latitude = row[1]
            hospital_name = row[2]
            hospital_address = row[4]
            placepageUri = row[6]
            # print(hospital_address)
            # Add more fields as needed

            # Process the data or save it to the database
            # For example, create a new Django model object and save it
            obj = Hospital(hospital_name=hospital_name, hospital_address=hospital_address, longitude=longitude, latitude=latitude, placepageUri=placepageUri)
            obj.save()

    return HttpResponse('CSV data has been read.')



































import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def get_distance_matrix(origins, destinations, api_key):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origins}&destinations={destinations}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    return data

@csrf_exempt
def get_nearby_hospitals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        print(latitude)
        print(longitude)
        
        # Retrieve hospitals from the database
        hospitals = Hospital.objects.all()  # Assuming Hospital is your model
        nearby_hospitals = []
        
        for hospital in hospitals:
            try:
                hospital_latitude = float(hospital.latitude)
                hospital_longitude = float(hospital.longitude)
            except ValueError:
                continue  # Skip this hospital if latitude or longitude is invalid
            
            destination = f"{hospital_latitude},{hospital_longitude}"
            data = get_distance_matrix(f"{latitude},{longitude}", destination, "Your API Key")
            distance = data['rows'][0]['elements'][0]['distance']['text']
            duration = data['rows'][0]['elements'][0]['duration']['text']
            
            hospital_data = {
                'name': hospital.hospital_name,
                'address': hospital.hospital_address,
                'distance': distance,
                'duration': duration
            }
            nearby_hospitals.append(hospital_data)
        
        # Sort hospitals by distance
        nearby_hospitals.sort(key=lambda x: x['distance'])
        print("nearby_hospitals", nearby_hospitals[0:10])
        
        # Return the list of nearby hospitals
        return JsonResponse({'hospitals': nearby_hospitals, 'status': 'success'})
    
    else:
        return render(request, 'store/hospital_location.html')













import json
import requests
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Hospital

API_KEY = "YOUR_API_KEY"

def get_distance_matrix(origins, destinations):
    cache_key = f"distance_matrix:{origins}:{destinations}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origins}&destinations={destinations}&key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    cache.set(cache_key, data, timeout=3600)  # Cache for 1 hour
    return data

@csrf_exempt
def get_nearby_hospitals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        hospitals = Hospital.objects.all()
        nearby_hospitals = []

        for hospital in hospitals:
            try:
                hospital_latitude = float(hospital.latitude)
                hospital_longitude = float(hospital.longitude)
            except ValueError:
                continue

            destination = f"{hospital_latitude},{hospital_longitude}"
            data = get_distance_matrix(f"{latitude},{longitude}", destination)
            
            if data.get('status') == 'OK':
                distance = data['rows'][0]['elements'][0]['distance']['text']
                duration = data['rows'][0]['elements'][0]['duration']['text']
                
                hospital_data = {
                    'name': hospital.hospital_name,
                    'address': hospital.hospital_address,
                    'distance': distance,
                    'duration': duration
                }
                nearby_hospitals.append(hospital_data)

        nearby_hospitals.sort(key=lambda x: x['distance'])
        return JsonResponse({'hospitals': nearby_hospitals, 'status': 'success'})
    else:
        return JsonResponse({'error': 'Invalid request method'})














































you gave me this def get_nearby_hospitals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        print("Received latitude:", latitude)
        print("Received longitude:", longitude)

        # Retrieve hospitals from the database
        hospitals = Hospital.objects.all()
        nearby_hospitals = []
        processed_coordinates = set()  # Set to store processed coordinates

        # Iterate through each hospital
        for hospital in hospitals:
            try:
                hospital_latitude = float(hospital.latitude)
                hospital_longitude = float(hospital.longitude)
            except ValueError:
                continue  # Skip this hospital if latitude or longitude is invalid

            # Check if the hospital coordinates have already been processed
            if (hospital_latitude, hospital_longitude) in processed_coordinates:
                continue  # Skip if already processed

            # Calculate distance using GeoPy's geodesic function
            coordinate1 = (latitude, longitude)
            coordinate2 = (hospital_latitude, hospital_longitude)
            distance = geodesic(coordinate1, coordinate2).meters

            # Store the hospital details
            hospital_data = {
                'name': hospital.hospital_name,
                'address': hospital.hospital_address,
                'latitude': hospital_latitude,
                'longitude': hospital_longitude,
                'distance': distance
            }
            nearby_hospitals.append(hospital_data)
            processed_coordinates.add((hospital_latitude, hospital_longitude))  # Mark coordinates as processed

        # Sort hospitals by distance
        nearby_hospitals.sort(key=lambda x: x['distance'])

        # Extract the nearest 30 hospitals
        nearest_hospitals = nearby_hospitals[:70]

        # Use Google Maps Distance Matrix API to calculate distances
        gmaps = googlemaps.Client(key='YOUR_API_KEY')  # Replace 'YOUR_API_KEY' with your actual API key

        # Define origins and destinations
        origins = [(latitude, longitude)]
        destinations = [(hospital['latitude'], hospital['longitude']) for hospital in nearest_hospitals]

        # Perform distance matrix request
        response = gmaps.distance_matrix(origins, destinations, mode='driving')

        # Extract distances from the response
        distances = [element['distance']['value'] for row in response['rows'] for element in row['elements']]

        # Update nearest hospitals with distances
        for i, hospital in enumerate(nearest_hospitals):
            hospital['distance_from_origin'] = distances[i]

        print('Nearest hospitals with distances:', nearest_hospitals)

        # Return the response as JSON
        return JsonResponse({'nearest_hospitals': nearest_hospitals})

    else:
        return render(request, 'store/hospital_location.html')
 and this correction # Use Google Maps Distance Matrix API to calculate distances
gmaps = googlemaps.Client(key='YOUR_API_KEY')  # Replace 'YOUR_API_KEY' with your actual API key

# Define origins and destinations
origins = [(latitude, longitude)]
destinations = [(hospital['latitude'], hospital['longitude']) for hospital in nearest_hospitals]

# Initialize variables
batch_size = 25  # Maximum number of destinations per request
batches = [destinations[i:i + batch_size] for i in range(0, len(destinations), batch_size)]
distances = []

# Perform distance matrix requests in batches
for batch in batches:
    response = gmaps.distance_matrix(origins, batch, mode='driving')
    for row in response['rows']:
        for element in row['elements']:
            distance = element['distance']['value']
            distances.append(distance)

# Update nearest hospitals with distances
for i, hospital in enumerate(nearest_hospitals):
    hospital['distance_from_origin'] = distances[i]

print('Nearest hospitals with distances:', nearest_hospitals)













def get_nearby_hospitals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        print("Received latitude:", latitude)
        print("Received longitude:", longitude)

        # Retrieve hospitals from the database
        hospitals = Hospital.objects.all()
        nearby_hospitals = []
        processed_coordinates = set()  # Set to store processed coordinates

        # Iterate through each hospital
        for hospital in hospitals:
            try:
                hospital_latitude = float(hospital.latitude)
                hospital_longitude = float(hospital.longitude)
            except ValueError:
                continue  # Skip this hospital if latitude or longitude is invalid

            # Check if the hospital coordinates have already been processed
            if (hospital_latitude, hospital_longitude) in processed_coordinates:
                continue  # Skip if already processed

            # Calculate distance using GeoPy's geodesic function
            coordinate1 = (latitude, longitude)
            coordinate2 = (hospital_latitude, hospital_longitude)
            distance = geodesic(coordinate1, coordinate2).meters

            # Store the hospital details
            hospital_data = {
                'name': hospital.hospital_name,
                'address': hospital.hospital_address,
                'latitude': hospital_latitude,
                'longitude': hospital_longitude,
                'distance': distance
            }
            nearby_hospitals.append(hospital_data)
            processed_coordinates.add((hospital_latitude, hospital_longitude))  # Mark coordinates as processed

        # Sort hospitals by distance
        nearby_hospitals.sort(key=lambda x: x['distance'])

        # Extract the nearest 70 hospitals
        nearest_hospitals = nearby_hospitals[:70]

        # Use Google Maps Distance Matrix API to calculate distances
        gmaps = googlemaps.Client(key='AIzaSyDz6PPs-S0jojUFcw7JbhGPdnrmp75F5FE')  # Replace 'YOUR_API_KEY' with your actual API key

        # Define origins and destinations
        origins = [(latitude, longitude)]
        destinations = [(hospital['latitude'], hospital['longitude']) for hospital in nearest_hospitals]

        # Initialize variables
        batch_size = 25  # Maximum number of destinations per request
        batches = [destinations[i:i + batch_size] for i in range(0, len(destinations), batch_size)]
        distances = []

        # Perform distance matrix requests in batches
        for batch in batches:
            response = gmaps.distance_matrix(origins, batch, mode='driving')
            for row in response['rows']:
                for element in row['elements']:
                    distance = element['distance']['value']
                    distances.append(distance)

        # Update nearest hospitals with distances
        for i, hospital in enumerate(nearest_hospitals):
            hospital['distance_from_origin'] = distances[i]

        print('Nearest hospitals with distances:', nearest_hospitals)

        # Return the response as JSON
        return JsonResponse({'nearest_hospitals': nearest_hospitals})

    else:
        return render(request, 'store/hospital_location.html')
