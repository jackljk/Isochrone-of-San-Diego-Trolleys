import folium

lat, lng = 32.86926550131975, -117.21402645890504 # Center of Map
thresholds = [0, 250, 500, 750, 1000, 1250, 2000] # Thresholds for choropleth map
southwest, northeast= [32.528832, -117.203757], [33.080276, -116.912583] # Bounds of San Diego County



def create_new_map():
    map_obj = folium.Map(location=[lat, lng], zoom_start=13)
    # map_obj.fit_bounds([southwest, northeast])

    return map_obj


def update_map_cp(map_obj, geoData, data_df, name, fill_color='YlGn'):
    tooltip = folium.GeoJsonTooltip(fields=['GEOID', 'H1_001N']) # Tooltip for choropleth map

    cp = folium.Choropleth(
    geo_data=geoData,
    name=name,
    data=data_df,
    columns=['GEOID', 'H1_001N'],
    key_on='feature.properties.GEOID',
    fill_color=fill_color,
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Population',
    threshold_scale = thresholds,
    tooltip=tooltip,
    highlight=True
    ).add_to(map_obj)



    # Add tooltip
    folium.GeoJsonTooltip(['GEOID', 'H1_001N']).add_to(cp.geojson)

def update_map_isochrone(map_obj, union, name, color):
    # add bike in red
    custom_data = folium.FeatureGroup(name=name)
    folium.GeoJson(union, style_function=lambda x: {'color':color}).add_to(custom_data)

    # add feature groups to map
    map_obj.add_child(custom_data)
