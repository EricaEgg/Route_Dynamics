# Route Dynamics [![Build Status](https://travis-ci.com/metromojo/Route_Dynamics.svg?branch=master)](https://travis-ci.com/metromojo/Route_Dynamics)

`route_dynamics` is a python package created to estimate the load and energy demand for battery-electric bus routes. 
The package implements a simple dynamical model for the bus moving along realistic elevation profiles gathered from LIDAR data, along with speed limit information, bus stop location, and passenger load. 

### Use Cases

* **Matinence Scheduling**:
With a predicitive model of module degredation that is route and ridership specific, module replacement can be coordinated with other time intensive matinence that takes busses out of service and into the shop.

* **Route planning**:
King Country comntains a wide variety of terrien features, and it is likely that certain routes required more energy then other possibilites that would serve the same riders. This package allows route designers to quicky predict energy demand on numerous route possibilities in different conditions to optimize the fleet distribution.  

### Tech. Specs.

The foundation of `route_dynamics` is a `RouteTrajectory` object, that holds route data and wraps a simple Newtonian mechanics model of the bus under force balence between frictional, gravitational, and motive forces. The various components neccesary to compute the energy demand of a particular bus route are;

* **GIS files**: The software first imports geographic information system (GIS) data files containing route coordinates and loads them into GeoPandas DataFrames.

* **Elevation LIDAR data** on King County is loaded for given latitude and longitude coordinate defining a specific route to calculate the route steepnes/grade.

* **Bus stop dependent Ridership**: Bus stop coordinates and associated ridership for specific routes influence the bus speed, acceleration, and mass that can fluctuale up to 3x the unloaded bus mass when at passenger capacity.  

* **Modular integration of bus speed model** will allow for continued development towards parameter free prediction.
The package is currently equiped with a "speed up, speed limt, slow down" model, which assumes,

    1) the bus stops as all, every other, or every third stop (as set by user)

    2) the bus accelerates from a stop following a given acceleration profile, then accelerates constantly until the speed limit is reached. It then decelerates at a constant value. 

    3) the bus travels at the speed limit when between stops far enough apart to fascilitate acceleration and deceleration.


Thanks to modular design, all of the above components can be specified manually to fascilitate optimization of route design and energy demand research.


### Work Flow


![alt text][flowchart]

[flowchart]: https://github.com/metromojo/Route_Dynamics/blob/master/Documentation/FlowChart_2020.PNG





### Repository structure

* **route_dynamics**: The package, contains subpackages, modules and tests.

* **Documentation**: Contains project information, such as Use
Cases, work flow, and DIRECT poster

* **data**: King County Metro route shapefiles

* **examples**: Contains example Jupyter notebooks detailing how the package is used.  


### Software Dependencies and Packages

* python 3.6
* folium
* geopandas
* matplotlib
* numpy
* pandas
* rasterio
* rasterstats
* branca
<!-- * scikit-learn -->

A virtual environment is included in the repository called environment.yml.

### Getting Started

1. Use `git clone` to download the repository.
2. [Follow instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) to set up a conda environment from file `environment.yml`.
3. Download an elevation raster dataset and place it into the repository on your local
machine. The raster file used for the example (seattle_dtm.tif) can be found
[here](https://drive.google.com/open?id=1V8-VIPGcNJ4l7Bd7OYDjIstFb1dsyhxH) with a .uw email address.

### Example Outputs
___

#### Interactive Map:
Route 45
![map]

[map]: https://github.com/metromojo/Route_Dynamics/blob/master/examples/README_results/map45.PNG

#### Example of Load Profile with different constant accelerations:


![acceloutput]

[acceloutput]: https://github.com/metromojo/Route_Dynamics/blob/master/Documentation/Figures/Acceloutput.png

#### Segment of above plot showing loading and unloading:


Green bar indicates maximum loading and unloading power for battery modules
![accelsegment]

[accelsegment]: https://github.com/metromojo/Route_Dynamics/blob/master/Documentation/Figures/Acceloutput_segment.png


#### Route Ranking:

![rank]

[rank]: https://github.com/metromojo/Route_Dynamics/blob/master/examples/README_results/ranking_example.png



