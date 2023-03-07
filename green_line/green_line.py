from datetime import datetime

import requests
import json

WALKING = {"type": "walking"}
BIKE = {"type": "cycling"}
TRAVEL_TIME = 600
URL = "https://api.traveltimeapp.com/v4/time-map"

green_line_stops = {
    "Santee Trolley Station": {'lat': 32.84163050968567, 'lng': -116.98089080932846},
    "Gillespie Field Station": {'lat': 32.82689235204705, 'lng': -116.98214599689385}, 
    "Arnele Avenue Station": {'lat': 32.80468375793681, 'lng': -116.97571236812209},
    "El Cajon Station": {'lat': 32.7920630558047, 'lng': -116.97620078493772}, 
    "Amaya Drive Station": {'lat': 32.78542564084955, 'lng': -117.00171319704818}, 
    "Grossmont Station": {'lat': 32.781828139058966, 'lng': -117.0110805611153}, 
    "70th Street Station": {'lat': 32.77225233791844, 'lng': -117.04248062264315}, 
    "Alvarado Station": {'lat': 32.77729625836487, 'lng': -117.05681571714611},
    "SDSU Station": {'lat': 32.77331650211465, 'lng': -117.0704777042407},
    "Grantville Station": {'lat': 32.78044605254656, 'lng': -117.09737489356071},
    "Mission San Diego Station": {'lat': 32.780855272780116, 'lng': -117.11078483300741},
    "SDSU Mission Valley / Aztec Stadium": {'lat': 32.78094499333704, 'lng': -117.12018485291216},
    "Fenton Parkway Station": {'lat': 32.77826155125899, 'lng': -117.12739865491132},
    "Rio Vista Station": {'lat': 32.77371345242011, 'lng': -117.14209479194207},
    "Mission Valley Center Station": {'lat': 32.771063145873725, 'lng': -117.14986169566542},
    "Hazard Center": {'lat': 32.77027265148022, 'lng': -117.15802784822571},
    "Fashion Valley Station": {'lat': 32.76546485206357, 'lng': -117.1690575584483},
    "Morena/Linda Vista": {'lat': 32.76362402489263, 'lng': -117.19681490412725},
    'Old Town Transit Center': {'lat': 32.754742157629835, 'lng': -117.19959896218734},
    'Washington Street Station': {'lat': 32.74179391362213, 'lng': -117.18421605916004}, 
    'Middletown Street Station': {'lat': 32.73377452104155, 'lng': -117.17487732001435}, 
    'County Center Little Italy Station': {'lat': 32.72128485344502, 'lng': -117.16989991419166}, 
    'Santa Fe Depot': {'lat': 32.71870225936083, 'lng': -117.17005580342646}, 
    "Seaport Village Station" :{'lat': 32.71209312361107, 'lng': -117.16862111181871}, 
    "Convention Center Station": {'lat': 32.70910464453388, 'lng': -117.16367254612264},
    "Gaslamp Quarter Station": {'lat': 32.70678491001947, 'lng': -117.15970101085334}, 
    "12th & Imperial": {'lat': 32.705273258820704, 'lng': -117.15413884468562}, 
}

def make_payload_search(station_name, lat, lng, transportation_type):
    search = {
            "id": station_name,
            "coords": {
                "lat": lat,
                "lng": lng
            },
            "transportation": transportation_type,
            "departure_time": datetime.utcnow().isoformat(),
            "travel_time": TRAVEL_TIME,
            }
    return search

def make_union(stations):
    unions = {
      "id": "last station: " + stations[len(stations) - 1],
      "search_ids": stations
    }
    return [unions]

def get_travel_times(trolley_line, transportation_type):

    payload_list = []
    curr_stations = []
    for i, (station_name, station) in enumerate(trolley_line.items()):
        
        payload_list.append(make_payload_search(station_name, station['lat'], station['lng'], transportation_type))
        curr_stations.append(station_name)

        if (i + 1) % 10 == 0 or i + 1 == len(green_line_stops):
            unions = make_union(curr_stations)


            payload_data = {"departure_searches": payload_list, "unions": unions}
            payload_str = json.dumps(payload_data)
            headers = {
                'Host': 'api.traveltimeapp.com',
                'Content-Type': 'application/json',
                'Accept': 'application/geo+json',
                'X-Application-Id': '20c42aed',
                'X-Api-Key': '92ea72b19d6a1c40d47c6f1737ba920a'
            }



            response = requests.post(URL, headers=headers, data=payload_str)
            filename = f"{station_name}_{transportation_type['type']}_{i+1}.geojson"

            # Write the response to a file
            with open('green_line/' + filename, "w") as text_file:
                text_file.write(response.text)

            # Reset the payload_list for the next group of 10 locations
            payload_list = []
            curr_stations = []

get_travel_times(green_line_stops, WALKING)
get_travel_times(green_line_stops, BIKE)
