# Route Dynamics [![Build Status](https://travis-ci.com/metromojo/Route_Dynamics.svg?branch=master)](https://travis-ci.com/metromojo/Route_Dynamics)

![alt text][logo]

[logo]: https://github.com/metromojo/Route_Dynamics/blob/master/Documentation/logo.JPG

`route_dynamics` is a python package created to estimate the energy demand of King County Metro bus routes.
The package implements a simple dynamical model for the bus moving along realistic elevation profiles gathered from LIDAR data. The modular nature of the packege facilitates exoerimentation with different estimations of:

* bus speed : Current implementation assumes constant acceleration away / towards bus stops, where the bus speed is 0. Between bus stops far enough apart, the bus reaches a specified speed limit.

* bus stop location : Location of bus stops prescribes the bus speed estimation.

* passenger load : can tripple the bus mass, and therefore drastically effects energy demand.  


### Quick Pitch

`route_dynamics` was (and continues to be) developed in partnership with King County metro to resolve inefficiencies in their hybrid electric bus fleet through predictive modeling.
Although the now electrified bus fleet is 20% more efficient than the old diesel busses, this gain in air quality, sound pollution, and environmental impact is seriously diminished by the fact that replacing batteries is expensive and currently unpredictable.
We are working to plug this efficient leak by building an open-source python package to predict battery degradation along specific King Country Metro hybrid bus routes using publicly available geographic data and ridership data from KCM. These data are fed into a simple dynamical model for the bus trajectory used to compute the time integrated power output of the bus and procide a tool for both cost efficient matinence schedualing and energy efficient route design and optimization.

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

    1) the bus stops as all declared bus stops,

    2) the bus accelerates with constant acceleration away from bus stops and deccelerates at the same rate towards oncoming stops,

    3) the bus travels at the speed limit when between stops far enough apart to fascilitate acceleration and deceleration.

* **Visualize Subpackage**: All routes can be displayed on interactive maps with elevation in color.

Thanks to modular design, all of the above components can be specified manually to fascilitate optimization of route design and energy demand research.


### Work Flow

<!-- !!! UPDATE !!! -->

The storage capacity of any battery module decays with the battery's power output, which can be predicted from the simple force balence on a bus moving along it's route. This dynamical model is contained in the module `route_dynamics/route_elevation/long_dynam_model`, and use is demonstrated in the jupyter notebook `examples/use_example__longi_dynam_model.ipynb`.

The flexibility of model for setting the passenger load per bus stop is demonstrated the jupyter notebook `examples/use_example__loaded_bus_mass_per_stop.ipynb`.

Total package structure and function is illustrated in notebook `examples/spring_quarter_example.ipynb`.

![alt text][flowchart]

[flowchart]: https://github.com/metromojo/Route_Dynamics/blob/master/Documentation/flowchart_spring.png





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
#### Elevation and Road Grade Profiles:
Route 45
![elevation]

[elevation]: https://github.com/metromojo/Route_Dynamics/blob/master/examples/README_results/route45_profile.png

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

#### Example notebook video
Check out a short video that runs through the package functions in the example notebook and shows the corresponding results
[here](https://drive.google.com/open?id=1ZpiIEzNWV0T_pzcjw9jkn3GkSxMLdkwo).



### Acknowledements

We would like to thank Dr. David Beck, Chad Curtis, and all DIRECT 2019 TA's for their
instruction, guidance, and support.
