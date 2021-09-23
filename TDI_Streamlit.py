import streamlit as st
import numpy as np
import requests
import seaborn as sns
import matplotlib.pyplot as plt

def relative_light(data, season):
    """ Returns one word descriptor of irradiance intensity and variation.
    Intensity values different for year vs season bc of number of days averaged."""

    data_mean = np.mean(data)
    data_std = np.std(data)

    if season == 'Year':
        if data_mean < 1:
            data_light = 'low'
        elif data_mean >= 1 and data_mean < 2:
            data_light = 'moderate'
        elif data_mean >= 2:
            data_light = 'strong'

        if data_std < 0.1:
            data_var = 'little'
        elif data_std >= 0.1 and data_std < 0.6:
            data_var = 'some'
        elif data_std >= 0.6:
            data_var = 'large'
    else:
        if data_mean < 2.5:
            data_light = 'low'
        elif data_mean >= 2.5 and data_mean < 5:
            data_light = 'moderate'
        elif data_mean >= 5:
            data_light = 'strong'

        if data_std < 0.5:
            data_var = 'little'
        elif data_std >= 0.5 and data_std < 1.0:
            data_var = 'some'
        elif data_std >= 1.0:
            data_var = 'large'

    return (data_light, data_var)

def floor_number(floor):
    """ Returns a short description for the floor number."""
    
    if floor == 'All':
        description = 'For this building'
    elif str(floor)[-1] == '1' and floor != 11:
        description = f'On the {floor}st floor'
    elif str(floor)[-1] == '2' and floor != 12:
        description = f'On the {floor}nd floor'
    elif str(floor)[-1] == '3' and floor != 13:
        description = f'On the {floor}rd floor'
    else:
        description = f'On the {floor}th floor'
    
    return description

def color_change(ax, season):
    """ Change values of histogram plot to show a heat-map color change with increasing light
    intensity. Intensity values different for year vs season bc of number of days averaged."""

    colors = ('#0343df', '#fffe7a', '#e50000')
    blend = sns.blend_palette(colors, n_colors=7, as_cmap=False, input='rgb')
    if season == 'Year':
        for p in ax.patches:
            if  p.get_x() <= 0.5:
                p.set_color(blend[0]) #blue
            elif  p.get_x() > 0.5 and p.get_x() <= 1.0:
                p.set_color(blend[1])
            elif  p.get_x() > 1.0 and p.get_x() <= 1.5:
                p.set_color(blend[2])
            elif  p.get_x() > 1.5 and p.get_x() <= 2.0:
                p.set_color(blend[3])
            elif  p.get_x() > 2.0 and p.get_x() <= 2.5:
                p.set_color(blend[4])  
            elif  p.get_x() > 2.5 and p.get_x() <= 3.0:
                p.set_color(blend[5])
            elif  p.get_x() > 3.0:
                p.set_color(blend[6])
    else: 
        for p in ax.patches:
            if  p.get_x() <= 1.0:
                p.set_color(blend[0]) #blue
            elif  p.get_x() > 1.0 and p.get_x() <= 2.0:
                p.set_color(blend[1])
            elif  p.get_x() > 2.0 and p.get_x() <= 3.0:
                p.set_color(blend[2])
            elif  p.get_x() > 3.0 and p.get_x() <= 4.0:
                p.set_color(blend[3])
            elif  p.get_x() > 4.0 and p.get_x() <= 5.0:
                p.set_color(blend[4])  
            elif  p.get_x() > 5.0 and p.get_x() <= 6.0:
                p.set_color(blend[5])
            elif  p.get_x() > 6.0:
                p.set_color(blend[6])

def geocode(address):
    params = {'format': 'json', 
                'addressdetails': 1,
                'q': address}

    headers = {'user-agent': 'TDI'}   

    r = requests.get('http://nominatim.openstreetmap.org/search', params=params, headers=headers).json()
    return (float(r[0]['lat']), float(r[0]['lon']))

    