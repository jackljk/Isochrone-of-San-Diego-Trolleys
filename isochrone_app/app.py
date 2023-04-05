import sys
sys.path.append('G:/My Drive/CCE/E-Bikes/Isochrone/Isochrone-of-San-Diego-Trolleys/isochrone_app/functions')



import flask
from functions.get_data import get_travel_times, get_census_data
from functions.data_cleaning import union_stations, get_density_by_bg, update_shapes
from functions.make_map import create_new_map, update_map_cp, update_map_isochrone
import json
import geopandas as gpd
import geojson
import folium

# read file
with open('Old Town Transit Center_cycling_10.geojson', 'r') as f:
    temp = f.read()

# CONSTANTS
customLocations = {
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
} # Dictionary of locations given by user
gdf = gpd.read_file(r'CA_shape_file\bg\cb_2021_06_bg_500k.shp') # Shape file for San Diego County


# Create Flask App
app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template('index.html', locations=customLocations)

@app.route('/add_location', methods=['POST'])
def add_location():
    name = flask.request.form['name']
    lat = flask.request.form['lat']
    lng = flask.request.form['lng']


    customLocations[name] = {'lat': lat, 'lng': lng}
    return flask.redirect('/')

@app.route('/remove_location', methods=['POST'])
def remove_location():
    name = flask.request.form['name']
    del customLocations[name]
    return flask.redirect('/')

@app.route('/map', methods=['POST'])
def make_map():
    global customLocations

    # Getting API Key
    API_KEY = flask.request.form['API_KEY']
    APP_ID = flask.request.form['APP_ID']
    TRAVEL_TIME = flask.request.form['travelTime']

    print(customLocations)
    # Getting Isochrone Data
    if type(TRAVEL_TIME) != float:
        travel_times = get_travel_times(customLocations, {"type": "cycling"}, API_KEY, APP_ID)
    else:
        travel_times = get_travel_times(customLocations, {"type": "cycling"}, API_KEY, APP_ID, TRAVEL_TIME)

    # Data Prep
    union = union_stations(travel_times)
    census_data = get_census_data("06", "073")
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