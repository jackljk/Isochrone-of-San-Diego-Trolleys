import shapely.geometry as sg
import geojson
import pandas as pd



def union_stations(stations):
    """
    Takes a list of geojsons and returns a shapely polygon of the union of all the stations
    """
    poly = sg.Polygon()
    if len(stations) > 1:
        for station in stations:
            for i in range(len(station['features'])):
                if "last location: " in station['features'][i]['properties']['search_id']:
                    poly = poly.union(sg.shape(station['features'][i]['geometry']))

        # Convert the unioned polygon into a GeoJSON Feature
        union_feature = geojson.Feature(geometry=poly, properties={})

        # Create a FeatureCollection with just the union feature
        union_feature_collection = geojson.FeatureCollection([union_feature])

        # Convert the FeatureCollection to a GeoJSON string
        union_geojson_str = geojson.dumps(union_feature_collection)
    else:
        union_geojson_str = stations[0]['features'][0]['geometry']
    return union_geojson_str

def get_density_by_bg(df, gdf, unions, county='SD'):
    # Split the "Block Group" from the NAME column into its own column
    df['Block Group'] = df['NAME'].str.split(',', expand=True)[1]

    # Convert the population column to an integer
    df['H1_001N'] = df['H1_001N'].astype(int)

    # groupby tract then block group and sum the population
    df = df.groupby(['state', 'county', 'tract', 'Block Group'])['H1_001N'].sum().reset_index()

    # remove the last row
    df = df[:-1]
    tracts = df['tract'].unique()

    df['Block Group'] = df['Block Group'].str.replace('Block Group ', '')
    df['H1_001N'] = df['H1_001N'].astype(str)

    # ----------------------------
    # get all tracts in df that are in tracts
    temp = gdf[(gdf['TRACTCE'].isin(tracts)) & (gdf['COUNTYFP'] == '073')].sort_values(by='TRACTCE')

    # add population to geojson
    temp['H1_001N'] = df['H1_001N'].values

    # join Tract and Block Group to create a unique identifier
    temp['tract'] = temp['TRACTCE'] + temp['BLKGRPCE']

    # get all polygons that intersect with the union of the biking geojsons
    # wrtite the union to a temp file
    with open('temp.geojson', 'w') as f:
        f.write(unions)
    temp = temp[temp.intersects(sg.shape(geojson.loads(unions)[0]['geometry']))]

    # Save temp as a geojson to a variable
    geojson_str = temp.to_json()

    # ----------------------------

    data_df = pd.DataFrame()
    data_df['GEOID'] = temp['GEOID'].values
    data_df['H1_001N'] = temp['H1_001N'].values

    # convert to int
    data_df['H1_001N'] = data_df['H1_001N'].astype(int)

    return data_df, geojson_str



def update_shapes(gs, transport_poly, df):
    percents = []
    df = df.copy()
    # Get the Polygon of the area covered by transport
    intersection = sg.shape(geojson.loads(transport_poly)[0]['geometry'])
    for feature in gs['features']:
        # Get the intersection of the BG and the transport area
        geometry = sg.shape(feature['geometry']).intersection(intersection)

        # Calculate the percentage of the BG that is covered by the transport area
        inter_percent = geometry.area/sg.shape(feature['geometry']).area
        percents.append(inter_percent)
        # Merge the area if the polygon is a multipolygon
        if isinstance(geometry, sg.MultiPolygon):
            geometry = geometry.buffer(0)  # merge MultiPolygons into a single Polygon
        feature['geometry'] = sg.mapping(geometry)
    
    # Update values on df
    df['H1_001N'] = df['H1_001N'] * percents
    # Update values in gs
    for i in range(len(gs['features'])):
        gs['features'][i]['properties']['H1_001N'] = df['H1_001N'].values[i] * percents[i]

    return gs, df
