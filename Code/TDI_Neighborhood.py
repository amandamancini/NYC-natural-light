import qgis
from qgis.core import *
from qgis.analysis import *
import qgis.utils
import processing
import sys
import os
import shutil
from osgeo import ogr

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingFeedback
from qgis.core import QgsProcessingContext
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterFolderDestination
import processing

from TDI_QGIS import select_attribute, clip_shapefile, DSM_generator, wall_height_aspect, sebe, building_buffer
from TDI_Python import mask_by_shapefile, reclassify_aspect, wall_irradiance, building_irradiance, array_to_raster
from TDI_Python import read_walls_full, Extract, full_wall_irradiance, layer_irradiance, floor_irradiance

def neighborhood_irradiance(neighborhood, DEM, meterological, folder):
    ''' Takes in neighborhood name, DEM file name, meterological file name, and folder and will output a
    dictionary with BIN building number keys and values of NSWE (means, std, and all values) of average 
    irradiance per pixel. The BIN can be matched to address from NYC OpenData.
    
    Neighborhood = name of neighborhood in neighborhood.shp
    DEM = name of DEM file without extension
    meterological = name of meterological file without extension
    folder = folder containing this starting and final data'''
    
    ## all files to be deleted will go in the tmp folder
    tmp_folder = os.path.join(f'{folder}', 'tmp/')
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)
    
    os.mkdir(tmp_folder)
    
    ## Initialize feedback and context for QGIS analyses
    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()
    
    ## Extract single neighborhood for analysis 
    neighborhood = ''.join(neighborhood)
    attr_parameters = {'Attribute': 'ntaname',
                       'AttributeValue': f'{neighborhood}',
                       'Shapefile': f'{folder}Neighborhoods.shp',
                       'Selected_shapefile': f'{tmp_folder}{neighborhood}.shp'}
    attr = select_attribute()
    attr.initAlgorithm()
    attr.processAlgorithm(parameters=attr_parameters, context = context, model_feedback = feedback)

    ## Buffer each neighborhood by 50ft for cropping DEM
    neigh_buffer_parameters = {'Bufferft': 50,
                               'Buildings': f'{tmp_folder}{neighborhood}.shp',
                               'Buffered': f'{tmp_folder}{neighborhood}_buffered.shp'}
    neigh_buffer = building_buffer()
    neigh_buffer.initAlgorithm()
    neigh_buffer.processAlgorithm(parameters=neigh_buffer_parameters, context = context, model_feedback = feedback)
    
    ## Crop DEM file to neighborhood extent
    neighbor_shape = f'{tmp_folder}{neighborhood}_buffered.shp'
    in_DEM = f'{folder}{DEM}.tiff'
    DEM_crop = f'{tmp_folder}{neighborhood}_DEM.tiff'
    mask_by_shapefile(raster=in_DEM, shapefile=neighbor_shape, crop_file=DEM_crop)
    
    ## Clip builidng shapefile to neighbohood extent
    clip_parameters = {'Clip': f'{tmp_folder}{neighborhood}.shp',
                       'Shapefile': f'{folder}Buildings.shp',
                       'Clipped': f'{tmp_folder}{neighborhood}_buildings.shp'}
    clip = clip_shapefile()
    clip.initAlgorithm()
    clip.processAlgorithm(parameters=clip_parameters, context = context, model_feedback = feedback)
    
    ## Create DSM for neighborhood
    DSM_parameters = {'DEM': DEM_crop,
                      'Buildings': f'{tmp_folder}{neighborhood}_buildings.shp',
                      'HeightField': 'heightroof',
                      'PixelResolution': 5,
                      'DSM': f'{tmp_folder}{neighborhood}_DSM.tiff'}
    DSM_gen = DSM_generator()
    DSM_gen.initAlgorithm()
    DSM_gen.processAlgorithm(parameters = DSM_parameters, context = context, model_feedback = feedback)

    ## Create TIFFs for wall height and aspect
    wall_parameters = {'DSM': f'{tmp_folder}{neighborhood}_DSM.tiff',
                       'Wallaspect': f'{tmp_folder}{neighborhood}_wall_aspect.tiff',
                       'Wallheight': f'{tmp_folder}{neighborhood}_wall_height.tiff'}
    walls = wall_height_aspect()
    walls.initAlgorithm()
    walls.processAlgorithm(parameters=wall_parameters, context = context, model_feedback = feedback)
    
    ## Calculate irradiance using SEBE
    tmp_sebe = os.path.join(f'{tmp_folder}', 'sebe/')
    if os.path.exists(tmp_sebe):
        shutil.rmtree(tmp_sebe)
    
    os.mkdir(tmp_sebe)
    from qgis.core import QgsProcessingParameterFolderDestination
    
    SEBE_parameters = {'DSM': f'{tmp_folder}{neighborhood}_DSM.tiff',
                       'WallAspect': f'{tmp_folder}{neighborhood}_wall_aspect.tiff',
                       'WallHeight': f'{tmp_folder}{neighborhood}_wall_height.tiff',
                       'Albedo': 0.15,
                       'Meterological': f'{folder}{meterological}.txt',
                       'UTC': -4,
                       'Outputs': f'{tmp_sebe}'} ####
    SEBE = sebe()
    SEBE.initAlgorithm()
    SEBE.processAlgorithm(parameters=SEBE_parameters, context = context, model_feedback = feedback)
    
    ## Calculate average irradiance per wall pixel
    in_irrad = f'{tmp_sebe}Energyyearwall.txt'
    avg_irrad_arr = wall_irradiance(in_irrad)
    
    ## Convert average irradiance array to raster
    avg_irrad_raster = f'{tmp_folder}{neighborhood}_average_irradiance.tiff'
    in_DSM = f'{tmp_folder}{neighborhood}_DSM.tiff'
    array_to_raster(arr=avg_irrad_arr, out_file=avg_irrad_raster, dsm_file=in_DSM)
    
    ## Buffer each builidng by 5ft for irradiance calculation 
    buffer_parameters = {'Bufferft': 5,
                         'Buildings': f'{tmp_folder}{neighborhood}_buildings.shp',
                         'Buffered': f'{tmp_folder}{neighborhood}_buildings_buffer.shp'}
    buffer = building_buffer()
    buffer.initAlgorithm()
    buffer.processAlgorithm(parameters=buffer_parameters, context = context, model_feedback = feedback)
    
    # ## Clip buffered builidng shapefile back to neighbohood extent
    # clip_buffer_parameters = {'Clip': f'{tmp_folder}{neighborhood}.shp',
    #                    'Shapefile': f'{tmp_folder}{neighborhood}_buildings_buffer.shp',
    #                    'Clipped': f'{tmp_folder}{neighborhood}_buildings_buffer_clip.shp'}
    # clip_buffer = clip_shapefile()
    # clip_buffer.initAlgorithm()
    # clip_buffer.processAlgorithm(parameters=clip_buffer_parameters, context = context, model_feedback = feedback)
    
    ## For each building calculate NWSE irradiance
    
    file = ogr.Open(f'{tmp_folder}{neighborhood}_buildings_buffer.shp')
    buildings = file.GetLayer(0) # list of attributes from building shapefile
    
    building_irradiances = {}
    
    for i in range(len(buildings)):
        ## Extract single building at a time
        BIN = buildings.GetFeature(i).GetField('bin')
        
        building_folder = os.path.join(f'{tmp_folder}', f'{int(BIN)}/')
        if os.path.exists(building_folder):
            shutil.rmtree(building_folder)
        
        os.mkdir(building_folder)
        
        building_parameters = {'Attribute': 'bin',
                               'AttributeValue': f'{BIN}',
                               'Shapefile': f'{tmp_folder}{neighborhood}_buildings_buffer.shp',
                               'Selected_shapefile': f'{building_folder}{int(BIN)}.shp'}
        build_attr = select_attribute()
        build_attr.initAlgorithm()
        build_attr.processAlgorithm(parameters=building_parameters, context = context, model_feedback = feedback)
        
        ## Crop aspect and irradiance rasters by building extent
        building_shape = f'{building_folder}{int(BIN)}.shp'
        
        in_aspect = f'{tmp_folder}{neighborhood}_wall_aspect.tiff'
        aspect_crop = f'{building_folder}{int(BIN)}_wall_aspect_crop.tiff'
        mask_by_shapefile(raster=in_aspect, shapefile=building_shape, crop_file=aspect_crop)
        
        in_irrad = f'{tmp_folder}{neighborhood}_average_irradiance.tiff'
        irrad_crop = f'{building_folder}{int(BIN)}_average_irradiance.tiff'
        mask_by_shapefile(raster=in_irrad, shapefile=building_shape, crop_file=irrad_crop)
        
        ## Reclassify wall aspect file
        out_aspect = f'{building_folder}{int(BIN)}_wall_aspect_crop_reclassify.tiff'
        reclassify_aspect(raster_file=aspect_crop, out_file=out_aspect)
        
        ## Calculate irradiance per wall 
        d = building_irradiance(irradiance_file = irrad_crop, aspect_file = out_aspect)
        building_irradiances[int(BIN)] = d
        
        ## Delete building directory with tmp files
        shutil.rmtree(building_folder)
        
    return building_irradiances
    


def neighborhood_setup(neighborhood, DEM, folder):
    ''' Takes in neighborhood name, DEM file name, and folder and will create DSM, wall height,
    and wall aspect files for each neightborhood.
    
    Neighborhood = name of neighborhood in neighborhood.shp
    DEM = name of DEM file without extension
    folder = folder containing this starting and final data'''
    
    ## create a season and neighborhood file
    neighborhood = ''.join(neighborhood)
    neighborhood_folder = os.path.join(f'{folder}neighborhoods/', f'{neighborhood}/')
    if os.path.exists(neighborhood_folder):
        shutil.rmtree(neighborhood_folder)
    
    os.mkdir(neighborhood_folder)
    
    ## Initialize feedback and context for QGIS analyses
    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()
    
    ## Extract single neighborhood for analysis 
    attr_parameters = {'Attribute': 'ntaname',
                       'AttributeValue': f'{neighborhood}',
                       'Shapefile': f'{folder}Neighborhoods.shp',
                       'Selected_shapefile': f'{neighborhood_folder}{neighborhood}.shp'}
    attr = select_attribute()
    attr.initAlgorithm()
    attr.processAlgorithm(parameters=attr_parameters, context = context, model_feedback = feedback)

    ## Buffer each neighborhood by 50ft for cropping DEM
    neigh_buffer_parameters = {'Bufferft': 50,
                               'Buildings': f'{neighborhood_folder}{neighborhood}.shp',
                               'Buffered': f'{neighborhood_folder}{neighborhood}_buffered.shp'}
    neigh_buffer = building_buffer()
    neigh_buffer.initAlgorithm()
    neigh_buffer.processAlgorithm(parameters=neigh_buffer_parameters, context = context, model_feedback = feedback)
    
    ## Crop DEM file to neighborhood extent
    neighbor_shape = f'{neighborhood_folder}{neighborhood}_buffered.shp'
    in_DEM = f'{folder}{DEM}.tiff'
    DEM_crop = f'{neighborhood_folder}{neighborhood}_DEM.tiff'
    mask_by_shapefile(raster=in_DEM, shapefile=neighbor_shape, crop_file=DEM_crop)
    
    ## Clip builidng shapefile to neighbohood extent
    clip_parameters = {'Clip': f'{neighborhood_folder}{neighborhood}.shp',
                       'Shapefile': f'{folder}Buildings.shp',
                       'Clipped': f'{neighborhood_folder}{neighborhood}_buildings.shp'}
    clip = clip_shapefile()
    clip.initAlgorithm()
    clip.processAlgorithm(parameters=clip_parameters, context = context, model_feedback = feedback)

    ## Buffer each builidng by 5ft for irradiance calculation 
    buffer_parameters = {'Bufferft': 5,
                         'Buildings': f'{neighborhood_folder}{neighborhood}_buildings.shp',
                         'Buffered': f'{neighborhood_folder}{neighborhood}_buildings_buffer.shp'}
    buffer = building_buffer()
    buffer.initAlgorithm()
    buffer.processAlgorithm(parameters=buffer_parameters, context = context, model_feedback = feedback)
    
    ## Create DSM for neighborhood
    DSM_parameters = {'DEM': DEM_crop,
                      'Buildings': f'{neighborhood_folder}{neighborhood}_buildings.shp',
                      'HeightField': 'heightroof',
                      'PixelResolution': 5,
                      'DSM': f'{neighborhood_folder}{neighborhood}_DSM.tiff'}
    DSM_gen = DSM_generator()
    DSM_gen.initAlgorithm()
    DSM_gen.processAlgorithm(parameters = DSM_parameters, context = context, model_feedback = feedback)

    ## Create TIFFs for wall height and aspect
    wall_parameters = {'DSM': f'{neighborhood_folder}{neighborhood}_DSM.tiff',
                       'Wallaspect': f'{neighborhood_folder}{neighborhood}_wall_aspect.tiff',
                       'Wallheight': f'{neighborhood_folder}{neighborhood}_wall_height.tiff'}
    walls = wall_height_aspect()
    walls.initAlgorithm()
    walls.processAlgorithm(parameters=wall_parameters, context = context, model_feedback = feedback)

def season_irradiances(neighborhood, meterological, season, folder):
    ''' Takes in neighborhood name, meterological file name, season, and folder and will output a
    dictionary with BIN building number keys and values of NSWE (means, std, and all values) of average 
    irradiance per pixel. The BIN can be matched to address from NYC OpenData.
    
    Neighborhood = name of neighborhood in neighborhood.shp
    meterological = name of meterological file without extension
    season = string of season name
    folder = folder containing this starting and final data'''
    
    ## assign variable for neighborhood file
    neighborhood = ''.join(neighborhood)
    neighborhood_folder = os.path.join(f'{folder}neighborhoods/', f'{neighborhood}/')
    
    ## Initialize feedback and context for QGIS analyses
    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()
    
    ## Calculate irradiance using SEBE
    season_sebe = os.path.join(f'{neighborhood_folder}', f'{season}_sebe/')
    if os.path.exists(season_sebe):
        shutil.rmtree(season_sebe)
    
    os.mkdir(season_sebe)
    from qgis.core import QgsProcessingParameterFolderDestination
    
    SEBE_parameters = {'DSM': f'{neighborhood_folder}{neighborhood}_DSM.tiff',
                       'WallAspect': f'{neighborhood_folder}{neighborhood}_wall_aspect.tiff',
                       'WallHeight': f'{neighborhood_folder}{neighborhood}_wall_height.tiff',
                       'Albedo': 0.15,
                       'Meterological': f'{folder}{meterological}.txt',
                       'UTC': -4,
                       'Outputs': f'{season_sebe}'}
    SEBE = sebe()
    SEBE.initAlgorithm()
    SEBE.processAlgorithm(parameters=SEBE_parameters, context = context, model_feedback = feedback)
    
    ## Calculate average irradiance per wall pixel
    in_irrad = f'{season_sebe}Energyyearwall.txt'
    avg_irrad_arr = wall_irradiance(in_irrad)
    
    ## Convert average irradiance array to raster
    tmp_season = os.path.join(f'{neighborhood_folder}', f'tmp_{season}/')
    if os.path.exists(tmp_season):
        shutil.rmtree(tmp_season)
    
    os.mkdir(tmp_season)
    avg_irrad_raster = f'{tmp_season}{season}_{neighborhood}_average_irradiance.tiff' ######

    in_DSM = f'{neighborhood_folder}{neighborhood}_DSM.tiff'
    array_to_raster(arr=avg_irrad_arr, out_file=avg_irrad_raster, dsm_file=in_DSM)
    
    ## For each building calculate NWSE irradiance
    
    file = ogr.Open(f'{neighborhood_folder}{neighborhood}_buildings_buffer.shp')
    buildings = file.GetLayer(0) # list of attributes from building shapefile
    
    building_irradiances = {}
    
    for i in range(len(buildings)):
        ## Extract single building at a time
        BIN = buildings.GetFeature(i).GetField('bin')
        
        building_folder = os.path.join(f'{tmp_season}', f'{int(BIN)}/')
        if os.path.exists(building_folder):
            shutil.rmtree(building_folder)
        
        os.mkdir(building_folder)
        
        building_parameters = {'Attribute': 'bin',
                               'AttributeValue': f'{BIN}',
                               'Shapefile': f'{neighborhood_folder}{neighborhood}_buildings_buffer.shp',
                               'Selected_shapefile': f'{building_folder}{int(BIN)}.shp'}
        build_attr = select_attribute()
        build_attr.initAlgorithm()
        build_attr.processAlgorithm(parameters=building_parameters, context = context, model_feedback = feedback)
        
        ## Crop aspect and irradiance rasters by building extent
        building_shape = f'{building_folder}{int(BIN)}.shp'
        
        in_aspect = f'{neighborhood_folder}{neighborhood}_wall_aspect.tiff'
        aspect_crop = f'{building_folder}{int(BIN)}_wall_aspect_crop.tiff'
        mask_by_shapefile(raster=in_aspect, shapefile=building_shape, crop_file=aspect_crop)
        
        in_irrad = f'{tmp_season}{season}_{neighborhood}_average_irradiance.tiff'
        irrad_crop = f'{building_folder}{int(BIN)}_average_irradiance.tiff'
        mask_by_shapefile(raster=in_irrad, shapefile=building_shape, crop_file=irrad_crop)
        
        ## Reclassify wall aspect file
        out_aspect = f'{building_folder}{int(BIN)}_wall_aspect_crop_reclassify.tiff'
        reclassify_aspect(raster_file=aspect_crop, out_file=out_aspect)
        
        ## Calculate irradiance per wall 
        d = building_irradiance(irradiance_file = irrad_crop, aspect_file = out_aspect)
        building_irradiances[int(BIN)] = d
        
        ## Delete building directory with tmp files
        shutil.rmtree(building_folder)
    
    shutil.rmtree(tmp_season)

    return building_irradiances


def full_season_irradiances(neighborhood, meterological, season, folder):
    ''' Takes in neighborhood name, meterological file name, season, and folder and will output a
    dictionary with BIN building number keys and values of NSWE (means, std, and all values) 
    irradiance for each floor. The BIN can be matched to address from NYC OpenData.
    
    Neighborhood = name of neighborhood in neighborhood.shp
    meterological = name of meterological file without extension
    season = string of season name
    folder = folder containing this starting and final data'''
    
    ## assign variable for neighborhood file
    neighborhood = ''.join(neighborhood)
    neighborhood_folder = os.path.join(f'{folder}neighborhoods/', f'{neighborhood}/')
    
    ## Initialize feedback and context for QGIS analyses
    feedback = QgsProcessingFeedback()
    context = QgsProcessingContext()
    
    ## Pull out irradiance per wall and layer
    season_sebe = f'{folder}sebe_results/{neighborhood}/{season}/'

    in_irrad = f'{season_sebe}Energyyearwall.txt'
    full_irrad_list = full_wall_irradiance(in_irrad)

    ## Convert irradiance arrays to set of rasters
    tmp_season = os.path.join(f'{folder}', f'tmp_{season}/')
    if os.path.exists(tmp_season):
        shutil.rmtree(tmp_season)

    os.mkdir(tmp_season)

    tmp_irrad = os.path.join(f'{tmp_season}', f'tmp_irrad/')
    os.mkdir(tmp_irrad)

    in_DSM = f'{neighborhood_folder}{neighborhood}_DSM.tiff'

    for i in range(len(full_irrad_list)):
        irrad_raster = f'{tmp_irrad}{season}_{neighborhood}_average_irradiance{i+1}.tiff' ###### makes X number of rasters
        array_to_raster(arr=full_irrad_list[i], out_file=irrad_raster, dsm_file=in_DSM)
    
    ## For each building calculate NWSE irradiance

    file = ogr.Open(f'{neighborhood_folder}{neighborhood}_buildings_buffer.shp')
    buildings = file.GetLayer(0) # list of attributes from building shapefile

    building_irradiances = {}

    for i in range(len(buildings)):
        ## Extract single building at a time
        BIN = buildings.GetFeature(i).GetField('bin')
        FLOORS = buildings.GetFeature(i).GetField('num_floors')

        building_folder = os.path.join(f'{tmp_season}', f'{int(BIN)}/')
        if os.path.exists(building_folder):
            shutil.rmtree(building_folder)

        os.mkdir(building_folder)

        building_parameters = {'Attribute': 'bin',
                            'AttributeValue': f'{BIN}',
                            'Shapefile': f'{neighborhood_folder}{neighborhood}_buildings_buffer.shp',
                            'Selected_shapefile': f'{building_folder}{int(BIN)}.shp'}
        build_attr = select_attribute()
        build_attr.initAlgorithm()
        build_attr.processAlgorithm(parameters=building_parameters, context = context, model_feedback = feedback)

        
        ## Crop aspect raster by building extent
        building_shape = f'{building_folder}{int(BIN)}.shp'

        in_aspect = f'{neighborhood_folder}{neighborhood}_wall_aspect.tiff'
        aspect_crop = f'{building_folder}{int(BIN)}_wall_aspect_crop.tiff'
        mask_by_shapefile(raster=in_aspect, shapefile=building_shape, crop_file=aspect_crop)
        
        ## Reclassify wall aspect file
        out_aspect = f'{building_folder}{int(BIN)}_wall_aspect_crop_reclassify.tiff'
        reclassify_aspect(raster_file=aspect_crop, out_file=out_aspect)
        
        ## Crop irradiance raster by building extent and extract values
        steps = 2 # average ceiling height is 10 ft
        floor = 0
        floor_irradiances = {}

        for i in range(0, len(full_irrad_list), steps): ## this might not include top-most layers..
            if floor < int(FLOORS): ## some buildings have 0 floors listed so those will be skipped...
                dicts = []
                floor += 1
                
                if i+steps < len(full_irrad_list):
                    for j in range(i, i+steps):
                    
                        in_irrad = f'{tmp_irrad}{season}_{neighborhood}_average_irradiance{j+1}.tiff'
                        irrad_crop = f'{building_folder}{int(BIN)}_average_irradiance{j+1}.tiff'
                        mask_by_shapefile(raster=in_irrad, shapefile=building_shape, crop_file=irrad_crop)

                    ## Calculate irradiance per wall 
                    d = layer_irradiance(irradiance_file = irrad_crop, aspect_file = out_aspect)
                    dicts.append(d)
                
                if i+steps >= len(full_irrad_list):
                    for j in range(i, len(full_irrad_list)):
                    
                        in_irrad = f'{tmp_irrad}{season}_{neighborhood}_average_irradiance{j+1}.tiff'
                        irrad_crop = f'{building_folder}{int(BIN)}_average_irradiance{j+1}.tiff'
                        mask_by_shapefile(raster=in_irrad, shapefile=building_shape, crop_file=irrad_crop)

                    ## Calculate irradiance per wall 
                    d = layer_irradiance(irradiance_file = irrad_crop, aspect_file = out_aspect)
                    dicts.append(d)
                
                floor_irradiances[floor] = floor_irradiance(dicts)
            
        building_irradiances[int(BIN)] = floor_irradiances

        ## Delete building directory with tmp files
        shutil.rmtree(building_folder)

    shutil.rmtree(tmp_season)

    return building_irradiances