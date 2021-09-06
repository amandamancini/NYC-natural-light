# NYC-natural-light
 
This project and [application](https://nyc-natural-light.herokuapp.com/) were created to help tenants (and property owners) in New York City to better understand the amount of natural light they can expect to receive in their building and on different floors, across the year and in different seasons. 

## Data sources
The data for this project were downloaded from two sources, [NYCOpenData](https://opendata.cityofnewyork.us/) and the [National Renewable Energy Laboratory](https://nsrdb.nrel.gov/). Most of the data for this project exceed storage capacity on GitHub and can we downloaded at the links below.

The geospatial data obtained from NYCOpenData were in the form of shapefiles, CSV files, and TIFFs and are as follows:
- [Borough boundaries](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/tqmj-j8zm) delineating the five boroughs of New York City, used for a borough-specific analysis.
- [Neighborhood Tabulation Areas](https://data.cityofnewyork.us/City-Government/2010-Neighborhood-Tabulation-Areas-NTAs-/cpf4-rkhq) delineating the 195 neighborhoods within the city, used to calculate solar irradiance for each neighborhood individually.
- [Building footprints](https://data.cityofnewyork.us/Housing-Development/Shapefiles-and-base-map/2k7f-6s2k) of over 1M buildings across all five boroughs, used to derive the Digital Surface Model of the city and calculate expected solar irradiance received for the walls of each building.
- [NYC Addresses](https://data.cityofnewyork.us/City-Government/NYC-Address-Points/g6pj-hd8k) detailing nearly 1M addresses across New York City, used to match address search in application to calculated irradiance for each building. Address data were downloaded as a CSV file.
- [Digital Elevation Models](https://gis.ny.gov/elevation/NYC-topobathymetric-DEM.htm) depicting elevation data at ground level across New York City with a 1ft pixel resolution, used to derive the Digital Surface Model of the city and calculate expected solar irradiance received for the walls of each building.

Additionally, meterological data were downloaded from the NREL's National Solar Radiation Database ([NSRDB](https://maps.nrel.gov/nsrdb-viewer/?aL=x8CI3i%255Bv%255D%3Dt%26Jea8x6%255Bv%255D%3Dt%26Jea8x6%255Bd%255D%3D1%26VRLt_G%255Bv%255D%3Dt%26VRLt_G%255Bd%255D%3D2%26mcQtmw%255Bv%255D%3Dt%26mcQtmw%255Bd%255D%3D3&bL=clight&cE=0&lR=0&mC=4.740675384778373%2C22.8515625&zL=2)). Meterological data included Direct Normal Irradiance (DNI; w/$m^2$), Diffuse Horizontal Irradiance (DHI; w/$\mathregular{m^2}$), Global Horizontal Irradiance (GHI; w/$\mathregular{m^2}$), wind speed (m/s), precipitaion (cm; converted to mm), relative humidity (%), temperature (C), and pressure (mbar; converted to kPa). These data were formatted using the [Meteorological Data: MetPreprocessor](https://umep-docs.readthedocs.io/en/latest/pre-processor/Meteorological%20Data%20MetPreprocessor.html) in the UMEP plugin of QGIS and the formatted data are in the Data folder. For more details, see methods below.

## Methods

