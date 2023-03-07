from datetime import datetime

import requests
import json

WALKING = {"type": "walking"}
BIKE = {"type": "cycling"}
TRAVEL_TIME = 600
URL = "https://api.traveltimeapp.com/v4/time-map"

blue_line_stops = {
    'UTC Station': {'lat': 32.86926550131975, 'lng': -117.21402645890504},
    'Executive Drive': {'lat': 32.8741479616388, 'lng': -117.21404708489588},
    'UCSD Health La Jolla': {'lat': 32.881854765126135, 'lng': -117.2235149089188},
    'UCSD Central Campus': {'lat': 32.8783759569827, 'lng': -117.23185294205638},
    'VA Medical Campus': {'lat': 32.8741832776601, 'lng': -117.22990481910972},
    'Nobel Drive': {'lat': 32.866943061484974, 'lng': -117.23041628225606},
    'Balboa Avenue': {'lat': 32.80576889086113, 'lng': -117.21405587587091},
    'Clairemont Drive': {'lat': 32.79006019677253, 'lng': -117.20612374239639},
    'Tecolote Road Station': {'lat': 32.76990781403746, 'lng': -117.20513206139343},
    'Old Town Transit Center': {'lat': 32.754742157629835, 'lng': -117.19959896218734},
    'Washington Street Station': {'lat': 32.74179391362213, 'lng': -117.18421605916004}, 
    'Middletown Street Station': {'lat': 32.73377452104155, 'lng': -117.17487732001435}, 
    'County Center Little Italy Station': {'lat': 32.72128485344502, 'lng': -117.16989991419166}, 
    'Santa Fe Depot': {'lat': 32.71870225936083, 'lng': -117.17005580342646}, 
    'American Plaza': {'lat': 32.7161724791036, 'lng': -117.1690383244911}, 
    'Civil Center': {'lat': 32.71667694275258, 'lng': -117.16228709163657},
    '5th Avenue Station': {'lat': 32.71670009462461, 'lng': -117.15948440280998},
    'City College Station': {'lat': 32.715844293440114, 'lng': -117.15405856996712},
    'Parks and Market Station': {'lat': 32.71097815841969, 'lng': -117.15377287447741},
    '12th & Imperial Station': {'lat': 32.70600058967276, 'lng': -117.15338036010606},
    'Barrio Logan Station': {'lat': 32.69806362693328, 'lng': -117.1467535290435},
    'Harborside Station': {'lat': 32.691240157058104, 'lng': -117.13302045798486},
    'Pacific fleet Station': {'lat': 32.686172418415104, 'lng': -117.12487081582847},
    '8th Street Station': {'lat': 32.67502229264786, 'lng': -117.11307237565377},
    '24th Street Station': {'lat': 32.66185677812119, 'lng': -117.10801700111236},
    'E Street Station': {'lat': 32.63889071753163, 'lng': -117.0989310849813},
    'H Street Station': {'lat': 32.63017324338384, 'lng': -117.09554385669355},
    'Palormar Street Station': {'lat': 32.603383153219816, 'lng': -117.08524425142537},
    'Palm Avenue Station': {'lat': 32.58461881180676, 'lng': -117.08380571120409},
    'Iris Avenue Station': {'lat': 32.56965801342579, 'lng': -117.0671074010019},
    'Beyer Boulevard Station': {'lat': 32.55768093757492, 'lng': -117.04706544440957},
    'San Ysidro Station': {'lat': 32.544568639554825, 'lng': -117.02954582607477},
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

        if (i + 1) % 10 == 0 or i + 1 == len(blue_line_stops):
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

            with open('blue_line/' + filename, "w") as text_file:
                text_file.write(response.text)
            # Reset the payload_list for the next group of 10 locations
            payload_list = []
            curr_stations = []

get_travel_times(blue_line_stops, WALKING)
get_travel_times(blue_line_stops, BIKE)
