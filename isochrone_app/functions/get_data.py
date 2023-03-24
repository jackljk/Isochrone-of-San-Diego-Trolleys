from datetime import datetime
import json
import requests

APP_ID = '20c42aed'
API_KEY = '92ea72b19d6a1c40d47c6f1737ba920a'
URL = "https://api.traveltimeapp.com/v4/time-map"

def make_payload_search(location_name, lat, lng, transportation_type, travel_time):
    search = {
            "id": location_name,
            "coords": {
                "lat": lat,
                "lng": lng
            },
            "transportation": transportation_type,
            "departure_time": datetime.utcnow().isoformat(),
            "travel_time": travel_time,
            }
    return search

def make_union(locations):
    unions = {
      "id": "last location: " + locations[len(locations) - 1],
      "search_ids": locations
    }
    return [unions]


def get_travel_times(locations, transportation_type, travel_time = 600):

    payload_list = []
    curr_locations = []

    for i, (location_name, location) in enumerate(locations.items()):
        
        payload_list.append(make_payload_search(location_name, location['lat'], location['lng'], transportation_type, travel_time))
        curr_locations.append(location_name)

        if (i + 1) % 10 == 0 or i + 1 == len(locations):
            unions = make_union(curr_locations)


            payload_data = {"departure_searches": payload_list, "unions": unions}
            payload_str = json.dumps(payload_data)
            headers = {
                'Host': 'api.traveltimeapp.com',
                'Content-Type': 'application/json',
                'Accept': 'application/geo+json',
                'X-Application-Id': APP_ID,
                'X-Api-Key': API_KEY
            }



            response = requests.post(URL, headers=headers, data=payload_str)
            filename = f"{location_name}_{transportation_type['type']}_{i+1}.geojson"

            with open('test/' + filename, "w") as text_file:
                text_file.write(response.text)
            # Reset the payload_list for the next group of 10 locations
            payload_list = []
            curr_locations = []


def add_dict(name, lat, long, d):
    if name == '':
        d['Location ' + (len(d) + 1)] = {'lat': lat, 'lng': long}

    if name not in d:
        d[name] = {'lat': lat, 'lng': long}


def make_dict(name, lat, long):
    d = {}
    for i in range(len(name)):
        add_dict(name[i], lat[i], long[i], d)
    return d