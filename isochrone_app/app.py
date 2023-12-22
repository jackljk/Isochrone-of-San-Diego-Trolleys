import sys
sys.path.append('G:/My Drive/CCE/E-Bikes/Isochrone/Isochrone-of-San-Diego-Trolleys/isochrone_app/functions')



import flask
from functions.get_data import get_travel_times, get_census_data
from functions.data_cleaning import union_stations, get_density_by_bg, update_shapes
from functions.make_map import create_new_map, update_map_cp, update_map_isochrone
from functions.helper import trolley_checklist
import geopandas as gpd
import geojson
import folium
import googlemaps


# CONSTANTS
gmaps = ''
APP_ID = ''
API_KEY = ''
DATAFRAME = {
    'drive': gpd.GeoDataFrame(),
    'walk': gpd.GeoDataFrame(),
    'bike': gpd.GeoDataFrame(),
    'ebike': gpd.GeoDataFrame()
}
# Variables
map_obj = create_new_map()
customLocations = {} # Dictionary of locations given by user
popData = {} # Dictionary of population data for each transportation mode
trolleys = [] # List of trolley stations that are selected
gdf = gpd.read_file('isochrone_app\\CA_shape_file\\bg\\cb_2021_06_bg_500k.shp') # Shape file for San Diego County


# Create Flask App
app = flask.Flask(__name__, template_folder='templates', static_url_path='/static')
app.config['SECRET_KEY'] = "6969696969"


@app.route('/')
def index():
    """
    Renders the index.html page
    """
    return flask.render_template('index.html', locations=customLocations,  map=map_obj._repr_html_(), popData=popData)

@app.route('/APPID_APIKEY', methods=['POST'])
def APPIN_APIKEY():
    """
    Gets the APP ID and API Key from the user
    """
    global APP_ID
    global API_KEY
    global gmaps

    APP_ID_IN = flask.request.form['APP_ID']
    API_KEY_IN = flask.request.form['API_KEY']
    GMAP_API = flask.request.form['GMAP_API']
    
    # If Gmap API is given, set up gmaps client
    if GMAP_API != '':
        gmaps = googlemaps.Client(key=GMAP_API)

     # Error Handling if API Key or APP ID is missing
    if API_KEY_IN == '':
        flask.flash('Missing API Key')
        return flask.redirect('/')
    
    if APP_ID_IN == '':
        flask.flash('Missing APP ID')
        return flask.redirect('/')
    
    
    APP_ID = APP_ID_IN
    API_KEY = API_KEY_IN
    flask.flash('API Key and APP ID have been set')

    return flask.redirect('/')

@app.route('/add_location', methods=['POST'])
def add_location():
    """
    Adds a location to the customLocations dictionary
    """
    global customLocations
    global trolleys
    # For Lat lng
    name = flask.request.form['name']
    lat = flask.request.form['lat']
    lng = flask.request.form['lng']
    # For Address
    address = flask.request.form['address']
    zipcode = flask.request.form['zipcode']
    
    # Handling if location already exists Error
    if name in customLocations.keys() or address in customLocations.keys():
        flask.flash('Location ' + name + ' already exists')
        return flask.redirect('/')
    # Adding location to dictionary
    radio_button = flask.request.form['input_type']
    if radio_button == 'latlng' and lat != '' and lng != '':
        # For when lat lng is given
        customLocations[name] = {'lat': lat, 'lng': lng}
    elif radio_button == 'address' and address != '':    
        address = address + ", San Diego, CA " + zipcode
        
        if gmaps == '':
            # If gmaps client is not set up
            flask.flash('Missing GMAP API Key add from API Key and APP ID page')
            return flask.redirect('/')
        else:
            # For when address is given
            result = gmaps.geocode(address)
        
        # Check if address is valid via gmaps API
        if result:
            customLocations[address] = {'lat': result[0]['geometry']['location']['lat'], 'lng': result[0]['geometry']['location']['lng']}
        else:
            # If address does not return anything handle error
            flask.flash('Invalid Address')
            return flask.redirect('/')
        
    
    # Getting the Trolley Stations
    trolleys = flask.request.form.getlist('trolleys')
    TROLLEY_STATIONS = trolley_checklist(trolleys)

    
    for trolley in TROLLEY_STATIONS.values():
        customLocations = {**customLocations, **trolley}

    return flask.redirect('/')

@app.route('/remove_location', methods=['POST'])
def remove_location():
    """
    Removes a location from the customLocations dictionary
    """
    name = flask.request.form['remove']
    del customLocations[name]

    # add option to clear the entire list
    return flask.redirect('/')

@app.route('/', methods=['POST'])
def make_map():
    """
    Using information given by user, creates a map with isochrone and census data
    """
    # Constants
    STATE_CODE = '06'
    COUNTY_CODE = '073'
    COLORS_CHOLOR = ["YlOrRd", "PuBuGn", "GnBu", "YlGnBu"]
    COLORS_ISO = ["#FFA500", "#6495ED", "#228B22", "#00CED1"]
    global customLocations, trolleys, map_obj, APP_ID, API_KEY, popData, DATAFRAMES
    
    
    # Getting Mode of Transportation
    mode_of_transport = flask.request.form['modeTransport']
    travel_time_val = float(flask.request.form['travelTime']) * 60
    avg_speed = flask.request.form['avgSpeed']
    
    # Reset Pop Data
    popData = {}
    
    # Get list of Mode of Transportation
    mode_of_transport = flask.request.form.getlist('modeTransport')

    # Creating Map
    map_obj = create_new_map()

    # add multiple dictionaries into one dictionary
    locations = {**customLocations}
    
    for transport in mode_of_transport: # Loop through all the selected modes of transports
        
        # Fixing mode of transport for API
        if transport == "drive":
            transport_API = {"type": "driving"}
            CP_COLOR = COLORS_CHOLOR[0]
            ISO_COLOR = COLORS_ISO[0]
        if transport == "walk":
            transport_API = {"type": "walking"}
            CP_COLOR = COLORS_CHOLOR[1]
            ISO_COLOR = COLORS_ISO[1]
        if transport == "bike":
            transport_API = {"type": "cycling"}
            CP_COLOR = COLORS_CHOLOR[2]
            ISO_COLOR = COLORS_ISO[2]
        if transport == "ebike":
            transport_API = {"type": "cycling"}
            CP_COLOR = COLORS_CHOLOR[3]
            ISO_COLOR = COLORS_ISO[3]
            travel_time_val = (float(avg_speed)/10) * float(travel_time_val)

        # Getting Isochrone Data
        if type(travel_time_val) != float:
            travel_times = get_travel_times(locations, transport_API, API_KEY, APP_ID, 600)
        else:
            travel_times = get_travel_times(locations, transport_API, API_KEY, APP_ID, travel_time_val)

        # Data Prep
        union = union_stations(travel_times)
        census_data = get_census_data(STATE_CODE, COUNTY_CODE)
        DATAFRAME[transport], geojson_str = get_density_by_bg(census_data, gdf, union)

        geojson_json = geojson.loads(geojson_str)
        geojson_json, DATAFRAME[transport]  = update_shapes(geojson_json, union, DATAFRAME[transport])


        update_map_cp(map_obj, geojson_json, DATAFRAME[transport], 'Populations-' + transport, fill_color=CP_COLOR)
        update_map_isochrone(map_obj, union, 'Isochrone-' + transport, ISO_COLOR)

        # Add the data of the population to a table.
        popData[transport] = round(DATAFRAME[transport]['H1_001N'].sum())
    layerControl = folium.LayerControl()
    layerControl.add_to(map_obj)
    return flask.render_template('index.html', map=map_obj._repr_html_(), locations=customLocations, popData=popData,
                                 selected_checkboxes = trolleys)


@app.route('/reset', methods=['POST'])
def reset():
    """
    Resets everything except for the API keys
    """ 
    
    global customLocations, trolleys, map_obj, APP_ID, API_KEY, popData
    
    # Resetting variables
    customLocations = {}
    trolleys = []
    map_obj = create_new_map()
    popData = {}
    
    return flask.redirect('/')

if __name__ == '__main__':
    app.run(debug=True)