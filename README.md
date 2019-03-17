# Route Dynamics
![alt text][logo]

[logo]: https://github.com/EricaEgg/Route_Dynamics/blob/master/logo.JPG

This tool was created to visualize the elevation changes for King County Metro bus routes. More broadly, it can be 
used to analyze any path along any terrain. The required inputs are a shapefile (.shp) for the route of interest and a 
raster file (.tif) for the elevation data. 

### Use Cases

* **Read GIS files**: The software first imports geographic information system (GIS) data files and makes them readable by 
Python.

* **Combine shapefile and raster data**: Next, the two data types are merged together so that for every x and y coordinate 
along the given route, there is also a z value. 

* **Visualize Network**: All routes are shown on a map with elevation color gradient. 

* **Qualitatively compare routes**: Select multiple routes to see how the elevation profiles compare. 

### Work Flow

![alt text][flowchart]

[flowchart]: https://github.com/EricaEgg/Route_Dynamics/blob/master/FlowChart.PNG 

### Software Dependencies and Packages

* Python 3.6
* folium
* geopandas
* matplotlib
* numpy
* pandas
* rasterio
* rasterstats

A virtual environment is included in the repository.

 
 
