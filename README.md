# NYC-natural-light
 
This project and [application](https://nyc-natural-light.herokuapp.com/) were created to help tenants (and property owners) in New York City to better understand the amount of natural light they can expect to receive in their building and on different floors, across the year and in different seasons. 

## Data sources
The data for this project were downloaded from two sources, [NYCOpenData](https://opendata.cityofnewyork.us/) and the [National Renewable Energy Laboratory](https://nsrdb.nrel.gov/). Most of the data for this project exceed the storage capacity on GitHub and can be downloaded at the links below. For more details on data manipulation and uses, see the Methods section below.

The geospatial data obtained from NYCOpenData were in the form of shapefiles, CSV files, and TIFFs and are as follows:
- [Borough boundaries](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/tqmj-j8zm) delineating the five boroughs of New York City, used for a borough-specific analysis.
- [Neighborhood Tabulation Areas](https://data.cityofnewyork.us/City-Government/2010-Neighborhood-Tabulation-Areas-NTAs-/cpf4-rkhq) delineating the 195 neighborhoods within the city, used to calculate solar irradiance for each neighborhood individually.
- [Building footprints](https://data.cityofnewyork.us/Housing-Development/Shapefiles-and-base-map/2k7f-6s2k) of over 1M buildings across all five boroughs, used to derive the Digital Surface Model of the city and calculate expected solar irradiance received for the walls of each building.
- [NYC Addresses](https://data.cityofnewyork.us/City-Government/NYC-Address-Points/g6pj-hd8k) detailing nearly 1M addresses across New York City, used to match address search in application to calculated irradiance for each building. Address data were downloaded as a CSV file.
- [Digital Elevation Models](https://gis.ny.gov/elevation/NYC-topobathymetric-DEM.htm) depicting elevation data at ground level across New York City with a 1ft pixel resolution, used to derive the Digital Surface Model of the city and calculate expected solar irradiance received for the walls of each building.

Additionally, meterological data were downloaded from the NREL's National Solar Radiation Database ([NSRDB](https://maps.nrel.gov/nsrdb-viewer/?aL=x8CI3i%255Bv%255D%3Dt%26Jea8x6%255Bv%255D%3Dt%26Jea8x6%255Bd%255D%3D1%26VRLt_G%255Bv%255D%3Dt%26VRLt_G%255Bd%255D%3D2%26mcQtmw%255Bv%255D%3Dt%26mcQtmw%255Bd%255D%3D3&bL=clight&cE=0&lR=0&mC=4.740675384778373%2C22.8515625&zL=2)). Meterological data included Direct Normal Irradiance (DNI; w/m<sup>2</sup>), Diffuse Horizontal Irradiance (DHI; w/m<sup>2</sup>), Global Horizontal Irradiance (GHI; w/m<sup>2</sup>), wind speed (m/s), precipitaion (cm; converted to mm), relative humidity (%), temperature (C), and pressure (mbar; converted to kPa). These data were formatted using the [Meteorological Data: MetPreprocessor](https://umep-docs.readthedocs.io/en/latest/pre-processor/Meteorological%20Data%20MetPreprocessor.html) in the UMEP plugin of QGIS and the formatted data are in the Data folder. For more details, see Methods below.

## Background
The motivation for this project was to create an application for New York City tenants and building owners to better understand the amount of natural light they can expect at different times of the year in their building for NSWE-facing walls. Due to the shading effects of buildings in NYC, adjacent buildings can received vastly different amounts of light throughout the year. The ability to estimate solar irradiance on building walls and rooftops in urban areas has previously been used to assess heat load in cities, as well as solar panel potential. This project aimed to utilize the methods developed for these other applications in a novel way that has real values for millions of people.

The methods used in this project were adapted from those developed by the [Urban Multi-scale Environmental Predictor](https://umep-docs.readthedocs.io/en/latest/index.html) (UMEP) Community. To estimate solar irradiance on building walls, first walls were detected from a Digital Surface Model (DSM) using an edge detection filter and rasters of wall heights and aspect were generated. The DSM, wall heights and aspect rasters, and meterological data (primarily GHI, DNI, and DHI) were then used to generate the shadow volume expected to be cast by each building onto adjacent areas using methods described by Ratti and Richens (1999; 2004). Using a modified shadow-casting algorithm, total solar irradiance was calculated for each wall pixel by summing the amount of direct, diffuse, and reflected radiation on the wall pixel and then subtracting out shadow volume cast from adjacent buildings. 

For a more thorough description of algorithm details, see the following papers:
    - [Ratti CF & Richens P. 1999. Urban texture analysis with image processing techniques. In: Proc CAADFutures99, Atlanta, GA.](http://senseable.mit.edu/papers/pdf/19990608_Ratti_Richens_UrbanTexture_CAAD.pdf)
    - [Ratti CF & Richens P. 2004. Raster analysis of urban form. *Environment and Planning B: Planning and Design* 31, 297–309.](https://senseable.mit.edu/papers/pdf/20040301_Ratti_Richens_RasterAnalysis_EnvironmentPlanning.pdf)
    - [Lindberg F, Jonsson P, Honjo T, and Wästberg D. 2015. Solar energy on building envelopes - 3D modelling in a 2D environment. *Solar Energy* 115: 369–378](https://www.sciencedirect.com/science/article/abs/pii/S0038092X15001164)
    - [Lindberg F, Grimmond CSB, Gabey A, Huang B, Kent C, et al. 2018. Multi-scale Environmental Predictor (UMEP): An integrated tool for city-based climate services. *Environmental Modelling & Software* 99: 70-87](https://www.sciencedirect.com/science/article/pii/S1364815217304140)

## Methods
### In QGIS application
1) I created one DEM for Manhattan by moasicking together DEMs using the GDAL Merge tool in the QGIS application using the following parameters:
    - Output Data Type: Float32
    - Additional Creation Options: High Compression
    - Available upon request.
2) Meterological data were converted to the UMEP format using the Meteorological Data: MetPreprocessor function in the UMEP QGIS plugin. 

### In Python using TDI_Full_Irradiance.py and TDI_Dataframes.py
3) Using `neighborhood_setup` (see TDI_Neighborhood.py) I generated DSMs, wall aspect and height TIFFs, and buffered neighborhood and buidling shapefiles for each neighborhood
    - This function was used to generate required data for modelling irradiance values on building walls in #3.
    - Support functions are found in TDI_Python.py and TDI_QGIS.py.
    - Implementation is found in TDI_Full_Irradiance.py.
4) Using `full_season_irradiances` (see TDI_Neighborhood.py) I generated irradiance values for NSWE walls of each building and for every floor.
    - This function uses the Solar Radiation: Solar Energy on Building Envelopes (SEBE) in the UMEP QGIS plugin to calculated expected irradiance on each building wall pixel. These data were then converted to a list of arrays and for each building irradiance per floor and per wall direction (NSWE) was summarized and stored in a dictionary and exported as a dill file for later use.
    - These calculatations were perfomed for each neighborhood individually and for all seasons (yearly, winter, spring, summer, and autumn).
    - Support functions are found in TDI_Python.py and TDI_QGIS.py.
    - Implementation is found in TDI_Full_Irradiance.py.
5) Dictionaries of irradiance values were converted to pandas dataframes for use in Streamlit application.
    - Dill files were flattened in dataframes decribing NSWE well irradiance values by building, floor, and season. Data were aggregated into one master dataframe (all seasons), as well as exported with eash season individually.
    - Irradiance values were normalized by number of days in each season (or year) into kWh/m<sup>2</sup>/Day.
    - Support functions are found in TDI_Python.py.
    - Implementation is found in TDI_Dataframes.py.

### Application
6) Irradiance values were turned into qualitative descriptions (low, moderate, and strong) of light intensity by visualing a histogram of irradiance values for each season and dividing into the 3 categories along visual breaks in the data.
    - For yearly data, low light is considered irradiance below 1 kWh/m<sup>2</sup>/Day, moderate is between 1-2 kWh/m<sup>2</sup>/Day, and strong is above 2 kWh/m<sup>2</sup>/Day.
    For seasonal data, low light is considered irradiance below 2.5 kWh/m<sup>2</sup>/Day, moderate is between 2.5-5 kWh/m<sup>2</sup>/Day, and strong is above 5 kWh/m<sup>2</sup>/Day.
    - Values different between yearly and seasonal estimated because of the number of days used to normalize data.
    - A similar procedure was taken for generating qualitative descriptions of light variation.
    - Support functions are found in TDI_Streamlit.py

## Notes
Please feel free to reach out to me with questions or suggestions for improvement!