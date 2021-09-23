import qgis
from qgis.core import *
from qgis.analysis import *
import qgis.utils
import processing
import sys
import os
import shutil
from osgeo import ogr, gdal
import dill

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

sys.path.append(r'/Users/amandamancini/opt/miniconda3/envs/qgis_tdi/share/qgis/python/plugins/processing/algs/gdal')
sys.path.append(r'/Users/amandamancini/opt/miniconda3/envs/qgis_tdi/share/qgis/python/plugins')
sys.path.append(r'/Users/amandamancini/Dropbox/TDI/Fellowship/Capstone/Python_Code')
sys.path.append(r'/Users/amandamancini/Dropbox/TDI/Fellowship/Capstone/Data/Manhattan')

# Initiating a QGIS application
qgishome = '/Users/amandamancini/opt/miniconda3/envs/qgis_tdi/lib/qgis'
QgsApplication.setPrefixPath(qgishome, True)

from processing.core.Processing import Processing
Processing.initialize()
from processing.tools import *

from processing_umep.processing_umep_provider import ProcessingUMEPProvider
umep_provider = ProcessingUMEPProvider()
QgsApplication.processingRegistry().addProvider(umep_provider)

from TDI_Neighborhood import neighborhood_setup, full_season_irradiances

folder = '/Users/amandamancini/Dropbox/TDI/Fellowship/Capstone/Data/Manhattan/'

from osgeo import ogr

manhattan = f'{folder}Neighborhoods.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')

dataSource = driver.Open(manhattan, 0)
layer = dataSource.GetLayer()
list_field = ['ntaname']

neighborhoods = []
for feature in layer:
    neighborhoods.append(feature.GetField('ntaname'))

neighborhoods_folder = os.path.join(f'{folder}', 'neighborhoods/')
if os.path.exists(neighborhoods_folder):
    shutil.rmtree(neighborhoods_folder)

os.mkdir(neighborhoods_folder)

## neighborhood setup
for neighborhood in neighborhoods[0:-1]: # dont do parks, etc
    neighborhood_setup(neighborhood=neighborhood, DEM='Manhattan_DEM_HighComp', folder=folder)

sebe_folder = os.path.join(f'{folder}', 'sebe_results/')
if os.path.exists(sebe_folder):
    shutil.rmtree(sebe_folder)

os.mkdir(sebe_folder)

## yearly irradiance

neighborhood_irradiances_year = {}

for neighborhood in neighborhoods[0:-1]: # dont do parks, etc
    irrads = full_season_irradiances(neighborhood=neighborhood, meterological='PSMv3_2020_Year_UMEP', season = 'year', folder=folder)
    
    neighborhood_irradiances_year[f'{neighborhood}'] = irrads

    src_dir = os.path.join(f'{neighborhoods_folder}{neighborhood}/', 'year_sebe/')
    dest_dir = os.path.join(f'{sebe_folder}', f'{neighborhood}/year/')

    shutil.copytree(src_dir, dest_dir)

    with open(f'{dest_dir}{neighborhood}_complete_building_irradiances_year.dill', 'wb') as f:
        dill.dump(irrads, f)

    shutil.rmtree(src_dir)

with open(f'{sebe_folder}Complete_building_irradiances_year.dill', 'wb') as f:
    dill.dump(neighborhood_irradiances_year, f)

## winter irradiance
neighborhood_irradiances_winter = {}

for neighborhood in neighborhoods[0:-1]: # dont do parks, etc
    irrads = full_season_irradiances(neighborhood=neighborhood, meterological='PSMv3_2020_Winter_UMEP', season = 'winter', folder=folder)
    
    neighborhood_irradiances_winter[f'{neighborhood}'] = irrads
    
    src_dir = os.path.join(f'{neighborhoods_folder}{neighborhood}/', 'winter_sebe/')
    dest_dir = os.path.join(f'{sebe_folder}', f'{neighborhood}/winter/')

    shutil.copytree(src_dir, dest_dir)

    with open(f'{dest_dir}{neighborhood}_complete_building_irradiances_winter.dill', 'wb') as f:
        dill.dump(irrads, f)

    shutil.rmtree(src_dir)

with open(f'{sebe_folder}Complete_building_irradiances_winter.dill', 'wb') as f:
    dill.dump(neighborhood_irradiances_winter, f)

## spring irradiance
neighborhood_irradiances_spring = {}

for neighborhood in neighborhoods[0:-1]: # dont do parks, etc
    irrads = full_season_irradiances(neighborhood=neighborhood, meterological='PSMv3_2020_Spring_UMEP', season = 'spring', folder=folder)
    
    neighborhood_irradiances_spring[f'{neighborhood}'] = irrads
    
    src_dir = os.path.join(f'{neighborhoods_folder}{neighborhood}/', 'spring_sebe/')
    dest_dir = os.path.join(f'{sebe_folder}', f'{neighborhood}/spring/')

    shutil.copytree(src_dir, dest_dir)

    with open(f'{dest_dir}{neighborhood}_complete_building_irradiances_spring.dill', 'wb') as f:
        dill.dump(irrads, f)

    shutil.rmtree(src_dir)

with open(f'{sebe_folder}Complete_building_irradiances_spring.dill', 'wb') as f:
    dill.dump(neighborhood_irradiances_spring, f)

## summer irradiance
neighborhood_irradiances_summer = {}

for neighborhood in neighborhoods[0:-1]: # dont do parks, etc
    irrads = full_season_irradiances(neighborhood=neighborhood, meterological='PSMv3_2020_Summer_UMEP', season = 'summer', folder=folder)
    
    neighborhood_irradiances_summer[f'{neighborhood}'] = irrads
    
    src_dir = os.path.join(f'{neighborhoods_folder}{neighborhood}/', 'summer_sebe/')
    dest_dir = os.path.join(f'{sebe_folder}', f'{neighborhood}/summer/')

    shutil.copytree(src_dir, dest_dir)

    with open(f'{dest_dir}{neighborhood}_complete_building_irradiances_summer.dill', 'wb') as f:
        dill.dump(irrads, f)

    shutil.rmtree(src_dir)

with open(f'{sebe_folder}Complete_building_irradiances_summer.dill', 'wb') as f:
    dill.dump(neighborhood_irradiances_summer, f)

## autumn irradiance
neighborhood_irradiances_autumn = {}

for neighborhood in neighborhoods[0:-1]: # dont do parks, etc
    irrads = full_season_irradiances(neighborhood=neighborhood, meterological='PSMv3_2020_Autumn_UMEP', season = 'autumn', folder=folder)
    
    neighborhood_irradiances_autumn[f'{neighborhood}'] = irrads
    
    src_dir = os.path.join(f'{neighborhoods_folder}{neighborhood}/', 'autumn_sebe/')
    dest_dir = os.path.join(f'{sebe_folder}', f'{neighborhood}/autumn/')

    shutil.copytree(src_dir, dest_dir)

    with open(f'{dest_dir}{neighborhood}_complete_building_irradiances_autumn.dill', 'wb') as f:
        dill.dump(irrads, f)

    shutil.rmtree(src_dir)

with open(f'{sebe_folder}Complete_building_irradiances_autumn.dill', 'wb') as f:
    dill.dump(neighborhood_irradiances_autumn, f)