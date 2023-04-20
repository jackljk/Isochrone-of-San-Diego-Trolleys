from datetime import datetime
import json
import requests
import pandas as pd

URL = "https://api.traveltimeapp.com/v4/time-map"

def make_payload_search(location_name, lat, lng, transportation_type, travel_time):
    search = {
            "id": location_name,
            "coords": {
                "lat": float(lat),
                "lng": float(lng)
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


def get_travel_times(locations, transportation_type, API_KEY, APP_ID, travel_time):
    geojsons = []
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



            geojsons.append(json.loads(response.text))

            # Reset the payload_list for the next group of 10 locations
            payload_list = []
            curr_locations = []

    return geojsons



def get_census_data(state_code, county_code):
    """
    Pull the census data for a given state and county and return a dataframe
    """
    API_KEY = "1e1f8670c9944ee8269a8d7065315bcd2f3eb0c8"
    url = f'https://api.census.gov/data/2020/dec/pl?get=NAME,H1_001N&for=block:*&in=state:{state_code}&in=county:{county_code}&key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    return df