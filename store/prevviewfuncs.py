@csrf_exempt
def get_nearby_vacancy_available_hospitals(request):
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/' + ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    gmaps = Client(key=settings.GOOGLE_MAPS_API_KEY)
    available = Hospital.objects.all().filter(home_available = True)

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
        name = place.get('name').lower()  # Convert the name to lowercase
        address = place.get('vicinity')
        try:
            hospital = Hospital.objects.get(hospital_name__iexact=name)
            if hospital.vacancies_available:
                hospital_data = {'name': name, 'address': address, 'phone_number': hospital.phone_number, 'ambulance_available': hospital.ambulance_available}
                if hospital.ambulance_available:
                    # Check if the hospital already exists in the list
                    existing_hospital = next(
                        (
                            h
                            for h in vacancy_available_hospitals
                            if h['name'].lower() == name and h['address'] == address  # Compare lowercase names
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
    return render(request, 'store/hospital_location.html', {'hospitals': vacancy_available_hospitals, 'available':available})



def get_nearby_vacancy_available_hospitals(request):
    if request.method == 'POST':
        # Retrieve the raw JSON data from the request body
        data = json.loads(request.body)

        # Extract the latitude and longitude values
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        print(latitude)
        print(longitude)

        # Process the latitude and longitude data
        # You can perform any necessary operations or save the data to the database

        # Return a JSON response indicating success
        return JsonResponse({'status': 'success'})
    else:
        return render(request, 'store/hospital_location.html')
















def get_nearby_hospitals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        print(latitude)
        print(longitude)

        # Process the latitude and longitude data
        # You can perform any necessary operations or save the data to the database

        # Retrieve hospitals from the database
        hospitals = Hospital.objects.all()
        nearby_hospitals = []

        for hospital in hospitals:
            try:
                hospital_latitude = float(hospital.latitude)

                hospital_longitude = float(hospital.longitude)
            except ValueError:
                continue  # Skip this hospital if latitude or longitude is invalid

            distance = calculate_distance(latitude, longitude, hospital_latitude, hospital_longitude)
            hospital_data = {
                'name': hospital.hospital_name,
                'address': hospital.hospital_address,
                'distance': distance
            }
            nearby_hospitals.append(hospital_data)

        # Sort hospitals by distance
        nearby_hospitals.sort(key=lambda x: x['distance'])
        print("nearby_hospitals", nearby_hospitals)

        # Return the list of nearby hospitals
        return JsonResponse({'hospitals': nearby_hospitals, 'status': 'success'})
    else:
        return render(request, 'store/hospital_location.html')

