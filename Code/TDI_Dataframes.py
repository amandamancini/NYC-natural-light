import sys
import pandas as pd
import dill
import numpy as np
from TDI_Python import flatten_to_df, convert_address

sys.path.append(r'/Users/amandamancini/Dropbox/TDI/Fellowship/Capstone/Data/Manhattan/sebe_results/')
sys.path.append(r'/Users/amandamancini/Dropbox/TDI/Fellowship/Capstone/Python_Code/')

## merge all irrandiance files into single df

sebe_folder = '/Users/amandamancini/Dropbox/TDI/Fellowship/Capstone/Data/Manhattan/sebe_results/'

with open(f'{sebe_folder}Complete_building_irradiances_year.dill', 'rb') as f:
    year = dill.load(f)

with open(f'{sebe_folder}Complete_building_irradiances_winter.dill', 'rb') as f:
    winter = dill.load(f)
    
with open(f'{sebe_folder}Complete_building_irradiances_spring.dill', 'rb') as f:
    spring = dill.load(f)
    
with open(f'{sebe_folder}Complete_building_irradiances_summer.dill', 'rb') as f:
    summer = dill.load(f)
    
with open(f'{sebe_folder}Complete_building_irradiances_autumn.dill', 'rb') as f:
    autumn = dill.load(f)

year_df = flatten_to_df(year, season= 'Year')
winter_df = flatten_to_df(winter, season= 'Winter')
spring_df = flatten_to_df(spring, season= 'Spring')
summer_df = flatten_to_df(summer, season= 'Summer')
autumn_df = flatten_to_df(autumn, season= 'Autumn')

dfs = [year_df, winter_df, spring_df, summer_df, autumn_df]

full_df = pd.concat(dfs)

full_df.to_csv(f'{sebe_folder}irradiance_full.csv', encoding='utf-8', index=False)

## Create df of Manhattan addresses
address = pd.read_csv('/Users/amandamancini/Dropbox/TDI/Fellowship/Capstone/Data/NYCOpenData/Address_Point.csv')
manhattan_address = address[address['BOROCODE'] == 1][['the_geom', 'BIN', 'H_NO', 'FULL_STREE', 'ZIPCODE']].copy()

manhattan_address.dropna(subset=['ZIPCODE'], inplace=True)
manhattan_address['Full_Address'] = manhattan_address.apply(convert_address, axis=1)

manhattan_address.to_csv('/Users/amandamancini/Dropbox/TDI/Fellowship/Capstone/Data/Manhattan/manhattan_address.csv', encoding='utf-8', index=False)