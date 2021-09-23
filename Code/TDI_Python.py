from statistics import mean
import scipy.sparse as sp
import numpy, sys
from osgeo import gdal, ogr
from osgeo.gdalconst import *
import numpy as np
from os import remove
from os.path import exists, basename, splitext
import pandas as pd

def mask_by_shapefile(raster, shapefile, crop_file):
    """ Mask a raster by a shapefile."""
    OutTile = gdal.Warp(crop_file, raster, cutlineDSName=shapefile, cropToCutline=True)
    OutTile = None

def reclassify_aspect(raster_file, out_file):
    """ Take in raster filename and an output filename and
    get out a raster with describing NSWE directions and NA values changed to 0"""
    
    
    raster = gdal.Open(raster_file)
    band = raster.GetRasterBand(1)
    arr = band.ReadAsArray()
    arr = np.where(arr >= 315, 360, arr) # north
    arr = np.where((arr > 0) & (arr < 45), 360, arr) # north
    arr = np.where((arr >= 45) & (arr < 135), 90, arr) # east
    arr = np.where((arr >= 135) & (arr < 225), 180, arr) # south
    arr = np.where((arr >= 225) & (arr < 315), 270, arr) # west
    arr = np.where(arr < 0, 0, arr) # nodata

    y, x = arr.shape

    driver = raster.GetDriver()
    
    out_raster = driver.Create(out_file, x, y, 1, gdal.GDT_Float32)
    out_raster.GetRasterBand(1).WriteArray(arr)

    # follow code is adding GeoTranform and Projection
    geotrans=raster.GetGeoTransform()
    proj=raster.GetProjection()
    
    out_raster.SetGeoTransform(geotrans)
    out_raster.SetProjection(proj)
    out_raster.FlushCache()

def array_to_raster(arr, out_file, dsm_file):
    """ Take in arr, output filename, and associated DSM file name;
    get out a raster with averaged wall irradiance values"""
    
    y, x = arr.shape
    
    dsm = gdal.Open(dsm_file)
    driver = dsm.GetDriver()
    
    out_raster = driver.Create(out_file, x, y, 1, gdal.GDT_Float32)
    out_raster.GetRasterBand(1).WriteArray(arr)

    # follow code is adding GeoTranform and Projection
    geotrans=dsm.GetGeoTransform()
    proj=dsm.GetProjection()
    
    out_raster.SetGeoTransform(geotrans)
    out_raster.SetProjection(proj)
    out_raster.FlushCache()


def get_building_code(building_file):
    """ Extract building BIN number from building footprint shapefile."""
    file = ogr.Open(building_file)
    shape = file.GetLayer(0)

    #first feature of the shapefile
    feature = shape.GetFeature(0)
    BIN = feature.GetField('bin')
    
    return int(BIN)

def fillna(raster_file, out_file):
    """ Take in raster filename and an output filename
    get out a raster with NA values changed to 0"""
    
    raster = gdal.Open(raster_file)
    band = raster.GetRasterBand(1)
    arr = band.ReadAsArray()
    arr = np.where(arr < 0, 0, arr) 

    y, x = arr.shape

    driver = raster.GetDriver()
    
    out_raster = driver.Create(out_file, x, y, 1, gdal.GDT_Float32)
    out_raster.GetRasterBand(1).WriteArray(arr)

    # follow code is adding GeoTranform and Projection
    geotrans=raster.GetGeoTransform()
    proj=raster.GetProjection()
    
    out_raster.SetGeoTransform(geotrans)
    out_raster.SetProjection(proj)
    out_raster.FlushCache()


def building_irradiance(irradiance_file, aspect_file):
    """Takes in file paths for building wall irradiance and wall aspect
    and returns a dictionary specifying mean, std, and all irradiance for NSWE walls"""
    
    irrad = gdal.Open(irradiance_file)
    irrad_arr = np.array(irrad.GetRasterBand(1).ReadAsArray())
    
    aspect = gdal.Open(aspect_file)
    aspect_arr = np.array(aspect.GetRasterBand(1).ReadAsArray())
    
    d = {}
    if 360 in aspect_arr:
        d['N'] = irrad_arr[aspect_arr == 360]
        d['N_mean'] = np.mean(d['N'])
        d['N_std'] = np.std(d['N'])
    
    if 90 in aspect_arr:
        d['E'] = irrad_arr[aspect_arr == 90]
        d['E_mean'] = np.mean(d['E'])
        d['E_std'] = np.std(d['E'])
    
    if 180 in aspect_arr:
        d['S'] = irrad_arr[aspect_arr == 180]
        d['S_mean'] = np.mean(d['S'])
        d['S_std'] = np.std(d['S'])
    
    if 270 in aspect_arr:
        d['W'] = irrad_arr[aspect_arr == 270]
        d['W_mean'] = np.mean(d['W'])
        d['W_std'] = np.std(d['W'])
    
    return d


def read_walls_full(file):
    """ Read in generated irradiance txt file and output a list of tuples decribing
    (row, columns, values) for each sparse array in z plane."""
    f = open(file, 'r')
    f.readline()
    file = f.read()
    f.close()

    file_list = file.split('\n')

    reduce_file_list = []
    for element in file_list[:-1]:
        li_str = element.split()
        li_nums = list(map(float, li_str))
        reduce_file_list.append((int(li_nums[0]), int(li_nums[1]), li_nums[2:]))
        
    return reduce_file_list

def Extract(lst, pos):
    return [item[pos] for item in lst]

def full_wall_irradiance(file):
    '''Takes in a list of tuples (row, columns, values)
    and outputs an list of full arrays of irradiance values
    for a given wall layer (z plane)'''
    
    li = read_walls_full(file)
    
    rows, cols, vals = zip(*li)
    
    floor_vals = []
    for i in range(len(vals[0])):
        if i < 400:
            floor_vals.append(Extract(vals, i))
    
    full_matrix_list = []
    for layer in floor_vals:
        arr = sp.coo_matrix((layer, (rows, cols))).todense()
        arr_corrected = arr[1:, 1:]
    
        x, y = arr_corrected.shape
        arr_corrected2 = numpy.insert(arr_corrected, x, 0, axis = 0)
        arr_corrected3 = numpy.insert(arr_corrected2, y, 0, axis = 1)
    
        full_matrix_list.append(numpy.array(arr_corrected3))
    
    return  full_matrix_list

def layer_irradiance(irradiance_file, aspect_file):
    """Takes in file paths for building wall irradiance and wall aspect
    and returns a dictionary specifying all irradiance for NSWE layer (z plane)"""
    
    irrad = gdal.Open(irradiance_file)
    irrad_arr = np.array(irrad.GetRasterBand(1).ReadAsArray())
    
    aspect = gdal.Open(aspect_file)
    aspect_arr = np.array(aspect.GetRasterBand(1).ReadAsArray())
    
    d = {}
    if 360 in aspect_arr:
        d['N'] = irrad_arr[aspect_arr == 360]
    
    if 90 in aspect_arr:
        d['E'] = irrad_arr[aspect_arr == 90]
    
    if 180 in aspect_arr:
        d['S'] = irrad_arr[aspect_arr == 180]
    
    if 270 in aspect_arr:
        d['W'] = irrad_arr[aspect_arr == 270]
    
    return d

def floor_irradiance(dict_list): 
    """ Will take in a list of dictionaries of layer irradiances (z plane) and 
    combine them into one dictionary as well as calculate mean and std for each wall
    direction. This is concatenate layers up to the level of floors."""
    d = {}
    for k in dict_list[0].keys():
        d[k] = np.concatenate(list(d[k] for d in dict_list))
    
    directions = list(d.keys())
    for direction in directions:
        data = list(d[direction])
        data = [x for x in data if x !=0]

        d[f'{direction}_mean'] = np.mean(data)
        d[f'{direction}_std'] = np.std(data)
    
    return d

def flatten_to_df(old_dict, season = None):
    """Take in dictionary of irradiance values for each building and floor 
    and string for the season. Will output a dataframe of irrandiance values for each 
    building and floor."""

    full_data = []
    
    days = {'Year': 366, 'Winter': 90, 'Spring': 92, 'Summer': 94, 'Autumn': 90}
    
    for neighborhood, buildings in old_dict.items():
        for building, floors in buildings.items():
            for floor, values in floors.items():
                for key, value in values.items():
                    values[key] = value/days[season]
                values['Floor'] = floor
                values['BIN'] = building
                values['Neighborhood'] = neighborhood
                values['Season'] = season
            
                full_data.append(values)

    df = pd.DataFrame.from_dict(full_data)

    return df
