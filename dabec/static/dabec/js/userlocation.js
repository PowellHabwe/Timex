const getlocation = () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            let latitude = position.coords.latitude;
            console.log(latitude)
            let longitude = position.coords.longitude;
            console.log(longitude)

            fetch('http://127.0.0.1:8000/store/nearest_vehicles/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({ latitude: latitude, longitude: longitude })
            })
            .then(response => {
                if (response.ok) {
                    console.log('Latitude and Longitude sent successfully!');
                    // window.location.href = '/store/display_nearest_hospitals/';
                } else {
                    console.log('Failed to send Latitude and Longitude!');
                    throw new Error('Failed to send Latitude and Longitude');
                }
            })
            .catch(error => {
                console.log('Error occurred:', error);
            });
        });
    }
};





function plotDistance(hospitalLat, hospitalLng) {
    // Your JavaScript code to plot the distance between user location and hospital location using Google Maps API
    // Example:
    var userLocation = { lat: USER_LATITUDE, lng: USER_LONGITUDE }; // Replace USER_LATITUDE and USER_LONGITUDE with actual user location
    var hospitalLocation = { lat: hospitalLat, lng: hospitalLng }; // Hospital location from button click
    var directionsService = new google.maps.DirectionsService();
    var directionsRenderer = new google.maps.DirectionsRenderer();
    var mapOptions = {
      zoom: 7,
      center: userLocation
    };
    var map = new google.maps.Map(document.getElementById('map'), mapOptions);
    directionsRenderer.setMap(map);
    var request = {
      origin: userLocation,
      destination: hospitalLocation,
      travelMode: 'DRIVING'
    };
    directionsService.route(request, function(response, status) {
      if (status == 'OK') {
        directionsRenderer.setDirections(response);
      } else {
        window.alert('Directions request failed due to ' + status);
      }
    });
  }

