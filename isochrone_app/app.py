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
customLocations = {} # Dictionary of locations given by user
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
    # Getting API Key
    print(flask.request.form)
    API_KEY = flask.request.form['API_KEY']
    APP_ID = flask.request.form['APP_ID']
    TRAVEL_TIME = flask.request.form['travelTime']

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