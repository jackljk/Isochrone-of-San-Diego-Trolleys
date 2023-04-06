import sys
sys.path.append('G:/My Drive/CCE/E-Bikes/Isochrone/Isochrone-of-San-Diego-Trolleys/isochrone_app/functions')



import flask
from functions.get_data import get_travel_times, get_census_data
from functions.data_cleaning import union_stations, get_density_by_bg, update_shapes
from functions.make_map import create_new_map, update_map_cp, update_map_isochrone
from functions.helper import trolley_checklist
import json
import geopandas as gpd
import geojson
import folium
import googlemaps


# CONSTANTS
GMAPI = "AIzaSyDSbu_7Yc_uqzjni4DboQS53L14pulaMj4"
gmaps = googlemaps.Client(key=GMAPI)
# Variables
customLocations = {} # Dictionary of locations given by user
# gdf = gpd.read_file('isochrone_app\\CA_shape_file\\bg\\cb_2021_06_bg_500k.shp') # Shape file for San Diego County


# Create Flask App
app = flask.Flask(__name__, template_folder='templates', static_url_path='/static')
app.config['SECRET_KEY'] = "6969696969"


@app.route('/')
def index():
    """
    Renders the index.html page
    """
    return flask.render_template('index.html', locations=customLocations)

@app.route('/add_location', methods=['POST'])
def add_location():
    """
    Adds a location to the customLocations dictionary
    """
    # For Lat lng
    name = flask.request.form['name']
    lat = flask.request.form['lat']
    lng = flask.request.form['lng']
    # For Address
    address = flask.request.form['address']
    address = address + ", San Diego, CA " + flask.request.form['zipcode']
    
    # Handling if location already exists Error
    if name in customLocations.keys() or address in customLocations.keys():
        flask.flash('Location ' + name + ' already exists')
        return flask.redirect('/')
    
    # Handling if information is missing
    if lat == '' or lng == '' or address == '' or name == '': 
        flask.flash('Missing information')
        return flask.redirect('/')
    
    # Adding location to dictionary
    radio_button = flask.request.form['input_type']
    if radio_button == 'latlng':
        # For when lat lng is given
        customLocations[name] = {'lat': lat, 'lng': lng}
    else:
        # For when address is given
        result = gmaps.geocode(address)
        
        # Check if address is valid via gmaps API
        if result:
            customLocations[address] = {'lat': result[0]['geometry']['location']['lat'], 'lng': result[0]['geometry']['location']['lng']}
        else:
            # If address is invalid handle error
            flask.flash('Invalid Address')
            return flask.redirect('/')
            
    return flask.redirect('/')

@app.route('/remove_location', methods=['POST'])
def remove_location():
    """
    Removes a location from the customLocations dictionary
    """
    name = flask.request.form['name']
    del customLocations[name]
    return flask.redirect('/')

@app.route('/map', methods=['POST'])
def make_map():
    """
    Using information given by user, creates a map with isochrone and census data
    """
    # Constants
    STATE_CODE = '06'
    COUNTY_CODE = '073'
    global customLocations
    
    # Getting the Trolley Stations
    trolleys = flask.request.form.getlist('trolley')
    TROLLEY_STATIONS = trolley_checklist(trolleys)
    
    
    # Getting Mode of Transportation
    mode_of_transport = flask.request.form['modeTransport']
    travel_time_val = flask.request.form['travelTime']
    
    # Fixing mode of transport for API
    if mode_of_transport == "driving":
        mode_of_transport = {"type": "driving"}
    if mode_of_transport == "walking":
        mode_of_transport = {"type": "walking"}
    if mode_of_transport == "cycling":
        mode_of_transport = {"type": "cycling"}
    if mode_of_transport == "eBike":
        mode_of_transport = {"type": "cycling"}
        travel_time_val = 2 * travel_time_val

    # Getting API Key
    API_KEY = flask.request.form['API_KEY']
    APP_ID = flask.request.form['APP_ID']

    # add multiple dictionaries into one dictionary
    locations = {**customLocations}
    for trolley in TROLLEY_STATIONS.values():
        locations = {**locations, **trolley}
    
    # Getting Isochrone Data
    if type(travel_time_val) != float:
        travel_times = get_travel_times(locations, mode_of_transport, API_KEY, APP_ID)
    else:
        travel_times = get_travel_times(locations, mode_of_transport, API_KEY, APP_ID, travel_time_val)

    # Data Prep
    union = union_stations(travel_times)
    census_data = get_census_data(STATE_CODE, COUNTY_CODE)
    data_df, geojson_str = get_density_by_bg(census_data, gdf, union)

    geojson_json = geojson.loads(geojson_str)
    geojson_json, data_df  = update_shapes(geojson_json, union, data_df)

    # Create Map
    map_obj = create_new_map()
    update_map_cp(map_obj, geojson_json, data_df, 'test')
    update_map_isochrone(map_obj, union, 'test', 'red')

    # add layer control
    folium.LayerControl().add_to(map_obj)

    return flask.render_template('map.html', map=map_obj._repr_html_())

if __name__ == '__main__':
    app.run(debug=True)