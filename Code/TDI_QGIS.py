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



"""
Model exported as python.
Name : DSM_Generator
Group : My UMEP Models
With QGIS : 32000
"""

class DSM_generator(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Buildings', 'Buildings', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('DEM', 'DEM', defaultValue=None))
        self.addParameter(QgsProcessingParameterField('HeightField', 'Height Field', type=QgsProcessingParameterField.Any, parentLayerParameterName='Buildings', allowMultiple=False, defaultValue='heightroof'))
        self.addParameter(QgsProcessingParameterNumber('PixelResolution', 'Pixel Resolution', type=QgsProcessingParameterNumber.Integer, defaultValue=5))
        self.addParameter(QgsProcessingParameterRasterDestination('DSM', 'DSM', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Spatial Data: DSM Generator
        alg_params = {
            'BUILDING_LEVEL': 3.1,
            'EXTENT': parameters['Buildings'],
            'INPUT_DEM': parameters['DEM'],
            'INPUT_FIELD': parameters['HeightField'],
            'INPUT_POLYGONLAYER': parameters['Buildings'],
            'PIXEL_RESOLUTION': parameters['PixelResolution'],
            'USE_OSM': False,
            'OUTPUT_DSM': parameters['DSM']
        }
        outputs['SpatialDataDsmGenerator'] = processing.run('umep:Spatial Data: DSM Generator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['DSM'] = outputs['SpatialDataDsmGenerator']['OUTPUT_DSM']
        return results

    def name(self):
        return 'DSM_Generator'

    def displayName(self):
        return 'DSM_Generator'

    def group(self):
        return 'My UMEP Models'

    def groupId(self):
        return 'My UMEP Models'

    def createInstance(self):
        return DSM_generator()

"""
Model exported as python.
Name : Wall_Height_Aspect
Group : My UMEP Models
With QGIS : 32000
"""

class wall_height_aspect(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('DSM', 'DSM', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Wallaspect', 'WallAspect', optional=True, createByDefault=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Wallheight', 'WallHeight', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Urban Geometry: Wall Height and Aspect
        alg_params = {
            'INPUT': parameters['DSM'],
            'INPUT_LIMIT': 3,
            'OUTPUT_ASPECT': parameters['Wallaspect'],
            'OUTPUT_HEIGHT': parameters['Wallheight']
        }
        outputs['UrbanGeometryWallHeightAndAspect'] = processing.run('umep:Urban Geometry: Wall Height and Aspect', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Wallaspect'] = outputs['UrbanGeometryWallHeightAndAspect']['OUTPUT_ASPECT']
        results['Wallheight'] = outputs['UrbanGeometryWallHeightAndAspect']['OUTPUT_HEIGHT']
        return results

    def name(self):
        return 'Wall_Height_Aspect'

    def displayName(self):
        return 'Wall_Height_Aspect'

    def group(self):
        return 'My UMEP Models'

    def groupId(self):
        return 'My UMEP Models'

    def createInstance(self):
        return wall_height_aspect()

"""
Model exported as python.
Name : SEBE
Group : My UMEP Models
With QGIS : 32000
"""

class sebe(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber('Albedo', 'Albedo', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=1, defaultValue=0.15))
        self.addParameter(QgsProcessingParameterRasterLayer('DSM', 'DSM', defaultValue=None))
        self.addParameter(QgsProcessingParameterFile('Meterological', 'Meterological', behavior=QgsProcessingParameterFile.File, fileFilter='All Files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('UTC', 'UTC', type=QgsProcessingParameterNumber.Integer, minValue=-12, maxValue=12, defaultValue=0))
        self.addParameter(QgsProcessingParameterRasterLayer('WallAspect', 'Wall_Aspect', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('WallHeight', 'Wall_Height', defaultValue=None))
        self.addParameter(QgsProcessingParameterFolderDestination('Outputs', 'Outputs', defaultValue=None)) # createByDefault=True,

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Solar Radiation: Solar Energy of Builing Envelopes (SEBE)
        alg_params = {
            'ALBEDO': parameters['Albedo'],
            'INPUTMET': parameters['Meterological'],
            'INPUT_ASPECT': parameters['WallAspect'],
            'INPUT_CDSM': None,
            'INPUT_DSM': parameters['DSM'],
            'INPUT_HEIGHT': parameters['WallHeight'],
            'INPUT_TDSM': None,
            'INPUT_THEIGHT': 25,
            'ONLYGLOBAL': False,
            'SAVESKYIRR': False,
            'TRANS_VEG': 3,
            'UTC': parameters['UTC'],
            'IRR_FILE': QgsProcessing.TEMPORARY_OUTPUT,
            'OUTPUT_DIR': parameters['Outputs']
        }
        outputs['SolarRadiationSolarEnergyOfBuilingEnvelopesSebe'] = processing.run('umep:Solar Radiation: Solar Energy of Builing Envelopes (SEBE)', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Outputs'] = outputs['SolarRadiationSolarEnergyOfBuilingEnvelopesSebe']['OUTPUT_DIR']
        return results

    def name(self):
        return 'SEBE'

    def displayName(self):
        return 'SEBE'

    def group(self):
        return 'My UMEP Models'

    def groupId(self):
        return 'My UMEP Models'

    def createInstance(self):
        return sebe()


"""
Model exported as python.
Name : Building_Buffer
Group : Capstone
With QGIS : 32000
"""

class building_buffer(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber('Bufferft', 'Buffer_ft', type=QgsProcessingParameterNumber.Integer, minValue=0, defaultValue=5))
        self.addParameter(QgsProcessingParameterVectorLayer('Buildings', 'Buildings', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Buffered', 'Buffered', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': parameters['Bufferft'],
            'END_CAP_STYLE': 0,  # Round
            'INPUT': parameters['Buildings'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': parameters['Buffered']
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Buffered'] = outputs['Buffer']['OUTPUT']
        return results

    def name(self):
        return 'Building_Buffer'

    def displayName(self):
        return 'Building_Buffer'

    def group(self):
        return 'Capstone'

    def groupId(self):
        return 'Capstone'

    def createInstance(self):
        return building_buffer()


"""
Model exported as python.
Name : Clip_Shapefile
Group : Capstone
With QGIS : 32000
"""


class clip_shapefile(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Clip', 'Clip', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Shapefile', 'Shapefile', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Clipped', 'Clipped', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Clip
        alg_params = {
            'INPUT': parameters['Shapefile'],
            'OVERLAY': parameters['Clip'],
            'OUTPUT': parameters['Clipped']
        }
        outputs['Clip'] = processing.run('native:clip', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Clipped'] = outputs['Clip']['OUTPUT']
        return results

    def name(self):
        return 'Clip_Shapefile'

    def displayName(self):
        return 'Clip_Shapefile'

    def group(self):
        return 'Capstone'

    def groupId(self):
        return 'Capstone'

    def createInstance(self):
        return clip_shapefile()


"""
Model exported as python.
Name : Select_Attribute
Group : Capstone
With QGIS : 32000
"""

class select_attribute(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterField('Attribute', 'Attribute', type=QgsProcessingParameterField.String, parentLayerParameterName='Shapefile', allowMultiple=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterString('AttributeValue', 'Attribute Value', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterVectorLayer('Shapefile', 'Shapefile', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Selected_shapefile', 'Selected_Shapefile', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # Extract by attribute
        alg_params = {
            'FIELD': parameters['Attribute'],
            'INPUT': parameters['Shapefile'],
            'OPERATOR': 0,  # =
            'VALUE': parameters['AttributeValue'],
            'OUTPUT': parameters['Selected_shapefile']
        }
        outputs['ExtractByAttribute'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Selected_shapefile'] = outputs['ExtractByAttribute']['OUTPUT']
        return results

    def name(self):
        return 'Select_Attribute'

    def displayName(self):
        return 'Select_Attribute'

    def group(self):
        return 'Capstone'

    def groupId(self):
        return 'Capstone'

    def createInstance(self):
        return select_attribute()
