import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import folium
from streamlit_folium import folium_static
import requests
import sys
import dill
import geopandas as gpd
import rtree
import s3fs
from s3fs.core import S3FileSystem
from TDI_Streamlit import relative_light, floor_number, color_change, geocode
    
def app():
    st.title('Understanding Natural Light in NYC')

    st.markdown("""The amount of natural light you receive in NYC can change immensely across the year, so use this app to get a better understanding of the amount and variation of light you can expect to receive across the year and in different seasons.""")
    st.markdown("""Enter an address to get information on natural light in your apartment building, office, etc.""")
    st.markdown("""
    - For now, this app only works for Manhattan addresses (other boroughs coming soon)
    - Please enter the address as: Street, City, State Abbreviation, Zipcode (optional)
    - If your address is not found, consider changing abbreviations to the full word (e.g., W to West or St to Street)
    - Ground floor is considered to be floor #1""")
    
    st.sidebar.markdown("""**About this project:**""")
    st.sidebar.markdown("""
    - This app was created for tenants (and property owners) to better understand the amount of natural light they can expect to receive across the year on different floors of their building.
    - Per-floor irradiance values were calculated assuming a ceiling height of 10ft, and are therefore unlikely to be accurate for commericial buildings that deviate from this value.
    - Data for this app were downloaded from [NYCOpenData](https://opendata.cityofnewyork.us/) and the [NREL](https://nsrdb.nrel.gov/).
    - For a full description of the project methods and access to code, check out my [GitHub] (https://github.com/amandamancini) repo.""")
    
    # create connection to s3
    s3_file = S3FileSystem(anon=True)
    
    # @st.cache() # caching doesnt seem to work
    def load_data(bucket, filename):
        data = s3_file.open('{}/{}'.format(bucket, filename))
        return data
        
    #geocode location
    location = str(st.text_input('Enter your address here:', '285 Fulton St, New York, NY 10048'))
    latlng = geocode(location)
    
    # convert location to geopandas df
    location_df = pd.DataFrame([list(latlng)],columns = ['lat', 'long'])
    location_gdf = gpd.GeoDataFrame(location_df, geometry=gpd.points_from_xy(location_df.long, location_df.lat))
    
    # set CRS and convert to NAD
    location_gdf = location_gdf.set_crs('EPSG:4326', inplace=True)
    location_gdf_NAD = location_gdf.to_crs('EPSG:2263')
    
    # load building shapefile and convert to geopandas df
    buildings = gpd.read_file(load_data('nyc-natural-light', 'Buildings.geojson'))
    
    # join gpds and find BIN
    sjoined = gpd.sjoin(location_gdf_NAD, buildings, how='inner')
    if len(sjoined) == 1:
        BIN = int(sjoined['bin'])   
    else:
        st.header("""**Oops! We can't seem to locate your address in our database. Please try another.**""")
    
    ## load all irradiance files
    irradiance_df = dill.load(load_data('nyc-natural-light', 'Year_Irradiance_df.dill')) # year_
    # winter_irradiance_df = dill.load(load_data('nyc-natural-light', 'Winter_Irradiance_df.dill'))
    # spring_irradiance_df = dill.load(load_data('nyc-natural-light', 'Spring_Irradiance_df.dill'))
    # summer_irradiance_df = dill.load(load_data('nyc-natural-light', 'Summer_Irradiance_df.dill'))
    # autumn_irradiance_df = dill.load(load_data('nyc-natural-light', 'Autumn_Irradiance_df.dill'))

    # dfs = [year_irradiance_df, winter_irradiance_df, spring_irradiance_df, summer_irradiance_df, autumn_irradiance_df]

    irradiance_df = pd.concat(dfs)

    building = irradiance_df[irradiance_df['BIN'] == BIN]

    left_column, right_column = st.columns(2)

    with left_column:
        season = st.selectbox('Choose a season:', ('Year', 'Winter', 'Spring', 'Summer', 'Autumn'))

    floors = building['Floor'].unique()
    with right_column:
        floor = st.selectbox('Choose a floor:', tuple(['All'] + list(floors)))

    building_final = building[building['Season'] == season]

    if floor != 'All':
        building_final = building_final[building_final['Floor'] == floor]

    dataN = np.concatenate(tuple(building_final['N']), axis=None)
    dataS = np.concatenate(tuple(building_final['S']), axis=None)
    dataW = np.concatenate(tuple(building_final['W']), axis=None)
    dataE = np.concatenate(tuple(building_final['E']), axis=None)

    north_light, north_var = relative_light(dataN, season)
    south_light, south_var = relative_light(dataS, season)
    west_light, west_var = relative_light(dataW, season)
    east_light, east_var = relative_light(dataE, season)

    description = floor_number(floor)

    if season == 'Year':
        st.markdown(f'''{description} **across the year**:''')
    elif season == 'Winter':
        st.markdown(f'''{description} **in the winter**:''')
    elif season == 'Spring':
        st.markdown(f'''{description} **in the spring**:''')        
    elif season == 'Summer':
        st.markdown(f'''{description} **in the summer**:''')        
    elif season == 'Autumn':
        st.markdown(f'''{description} **in the autumn**:''')

    st.markdown(f'''
    - You can execpt to receive {south_light} light for south-facing windows, with {south_var} variation across the southern wall. 
    - East-facing windows should receive {east_light} light, with {east_var} variation across the eastern wall. 
    - To the west, you will likely receive {west_light} light with {west_var} variation across the western wall. 
    - Finally, you can execpt north-facing windows to recieve {north_light} light with {north_var} variation across the northern wall.''')

    if season == 'Year':
        x_max = 3.5   
    else:
        x_max = 9.0        

    fig = plt.figure(figsize=(12, 12))
    gs = fig.add_gridspec(2, 2)

    with sns.axes_style("whitegrid"):
        ax = fig.add_subplot(gs[0, 0])
        sns.distplot(dataN, kde = False).set_title('North', y = 0.9, x=0.9, fontsize = 20)
        ax.set(xlim=(0, x_max), xlabel='Daily Irradiance (kWh/$\mathregular{m^2}$/Day)', ylabel='Count of Wall Pixels (25$\mathregular{ft^2}$)')
        color_change(ax, season)

    with sns.axes_style("whitegrid"):
        ax = fig.add_subplot(gs[0, 1])
        sns.distplot(dataS, kde = False).set_title('South', y = 0.9, x=0.9, fontsize = 20)
        ax.set(xlim=(0, x_max), xlabel='Daily Irradiance (kWh/$\mathregular{m^2}$/Day)', ylabel='Count of Wall Pixels (25$\mathregular{ft^2}$)')
        color_change(ax, season)

    with sns.axes_style("whitegrid"):
        ax = fig.add_subplot(gs[1, 0])
        sns.distplot(dataW, kde = False).set_title('West', y = 0.9, x=0.9, fontsize = 20)
        ax.set(xlim=(0, x_max), xlabel='Daily Irradiance (kWh/$\mathregular{m^2}$/Day)', ylabel='Count of Wall Pixels (25$\mathregular{ft^2}$)')
        color_change(ax, season)

    with sns.axes_style("whitegrid"):
        ax = fig.add_subplot(gs[1, 1])
        sns.distplot(dataE, kde = False).set_title('East', y = 0.9, x=0.9, fontsize = 20)
        ax.set(xlim=(0, x_max), xlabel='Daily Irradiance (kWh/$\mathregular{m^2}$/Day)', ylabel='Count of Wall Pixels (25$\mathregular{ft^2}$)')
        color_change(ax, season)

    fig.tight_layout()
    st.pyplot(fig)
    
    st.caption('Colors are strictly for visualizing abundance of low (cool colors) to strong light intensity (warm colors) on each wall. Irradiance values range from 0-3.5 kWh/$\mathregular{m^2}$/Day for yearly estimates and from 0-9 kWh/$\mathregular{m^2}$/Day for seasonal estimates.')
    
    map_ = folium.Map(location=latlng, zoom_start=25)
    folium.Marker(latlng, popup=folium.Popup(location, parse_html=True)).add_to(map_)
    (folium.CircleMarker(latlng,
                         popup=folium.Popup(location, parse_html=True),
                         radius=5,
                         color='#3186cc',
                         fill_color='#3186cc')
     .add_to(map_))
    
    folium_static(map_)
    
if __name__ == '__main__':
    app()