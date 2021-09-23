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

with open(f'{sebe_folder}Year_Irradiance_df.dill', 'wb') as f:
    dill.dump(year_df, f)
with open(f'{sebe_folder}Winter_Irradiance_df.dill', 'wb') as f:
    dill.dump(winter_df, f)
with open(f'{sebe_folder}Spring_Irradiance_df.dill', 'wb') as f:
    dill.dump(spring_df, f)
with open(f'{sebe_folder}Summer_Irradiance_df.dill', 'wb') as f:
    dill.dump(summer_df, f)
with open(f'{sebe_folder}Autumn_Irradiance_df.dill', 'wb') as f:
    dill.dump(autumn_df, f)

dfs = [year_df, winter_df, spring_df, summer_df, autumn_df]
full_df = pd.concat(dfs)

with open(f'{sebe_folder}Full_Irradiance_df.dill', 'wb') as f:
    dill.dump(full_df, f)