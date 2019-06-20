# Route Dynamics [![Build Status](https://travis-ci.com/metromojo/Route_Dynamics.svg?branch=master)](https://travis-ci.com/metromojo/Route_Dynamics)

![alt text][logo]

[logo]: https://github.com/EricaEgg/Route_Dynamics/blob/master/Documentation/logo.JPG

`route_dynamics` is a python package created to estimate the energy demand of King County Metro bus routes. 
The package implements a simple dynamical model for the bus moving along realistic elevation profiles gathered from LIDAR data. The modular nature of the packege facilitates exoerimentation with different estimations of:

* bus speed : Current implementation assumes constant acceleration away / towards bus stops, where the bus speed is 0. Between bus stops far enough apart, the bus reaches a specified speed limit. 

* bus stop location : Location of bus stops prescribes the bus speed estimation.

* passenger load : can tripple the bus mass, and therefore drastically effects energy demand.  


### Use Cases

* **Read GIS files**: The software first imports geographic information system (GIS) data files and makes them readable by 
Python.

* **Combine shapefile and elevation raster data**: Next, the two data types are merged together so that for every latitude and longitude coordinate along the given route, there is also a z value. 

* **Visualize Network**: All routes are shown on a map with elevation color gradient. 

* **Estimation of bus speed**: Select multiple routes to see how the elevation profiles compare. 

### Work Flow

![alt text][flowchart]

[flowchart]: 

**New flow chart coming soon**



### Folders in the Repository

* **Documentation**: Contains project information, such as Use 
Cases, work flow, and DIRECT poster

* **data**: King County Metro route shapefiles

* **examples**: Example notebook

* **route_dynamics**: module scripts and tests

### Software Dependencies and Packages

* Python 3.6
* folium
* geopandas
* matplotlib
* numpy
* pandas
* rasterio
* rasterstats
* branca

A virtual environment is included in the repository called environment.yml.

### Getting Started

1. Use `git clone` to download the repository.
2. Import the `environment.yml` virtual environment.
3. Download an elevation raster dataset and place it into the repository on your local 
machine. The raster file used for the example (seattle_dtm.tif) can be found 
[here](https://drive.google.com/open?id=1V8-VIPGcNJ4l7Bd7OYDjIstFb1dsyhxH). 

### Example Outputs

#### Elevation and Road Grade Profiles:
Route 45
![elevation]

[elevation]: https://github.com/EricaEgg/Route_Dynamics/blob/master/examples/README_results/route45_profile.png

#### Interactive Map:
Route 45
![map]

[map]: https://github.com/EricaEgg/Route_Dynamics/blob/master/examples/README_results/map45.PNG

#### Route Ranking:

![rank]

[rank]: https://github.com/EricaEgg/Route_Dynamics/blob/master/examples/README_results/ranking_example.png

#### Example notebook video
Check out a short video that runs through the package functions in the example notebook and shows the corresponding results 
[here](https://drive.google.com/open?id=1ZpiIEzNWV0T_pzcjw9jkn3GkSxMLdkwo).

### Nosetest Results

#### `test_base.py`
----------------------------------------------------------------------
Ran 9 tests in 8.113s

OK

#### `test_single_route.py`
----------------------------------------------------------------------
Ran 5 tests in 10.119s

OK

#### `test_multiple_route.py`
----------------------------------------------------------------------
Ran 1 test in 3.397s

OK

### Acknowledements

We would like to thank Dr. David Beck, Chad Curtis, and all DIRECT 2019 TA's for their 
instruction, guidance, and support. 
 
