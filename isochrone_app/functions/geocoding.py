import requests


def geocode(address):
    out = {}
    # Define the API endpoint and parameters
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "YOUR_API_KEY"
    }
    
    # Send a GET request to the API endpoint
    response = requests.get(endpoint, params=params)

    # Extract the latitude and longitude from the API response
    if response.status_code == 200:
        result = response.json()["results"][0]
        location = result["geometry"]["location"]
        latitude = location["lat"]
        longitude = location["lng"]
        
        out = {result["formatted_address"]: {"lat": latitude, "lng": longitude}}
        
        return out
    else:
        return response.status_code
