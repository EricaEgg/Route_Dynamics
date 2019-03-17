# Packages we only need 

Below packages we only need I think so let's remove other unnecessary packasges from the list. 

```
import numpy as np
import pandas as pd
%matplotlib inline
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from folium.features import GeoJson
import rasterio as rio
import rasterstats 
from shapely.geometry import Polygon, mapping, LineString
from geopy.distance import geodesic
import branca.colormap as cm
```


# Bar chart function

* Function module - https://github.com/EricaEgg/Route_Dynamics/blob/master/project/route.py
* Test module - https://github.com/EricaEgg/Route_Dynamics/blob/master/project/Test_bar
* Demonstration functions - https://github.com/EricaEgg/Route_Dynamics/blob/master/project/Demonstration%20.ipynb (I tried all the functions in addition to the bar chart function. Everything is ok). 


# Results after nosetests in my machine

The test results ok in my laptop as shown below. 

Yohan_Min@CBE-30226746 MINGW64 ~/DIRECT/Route_Dynamics/project (master)
$ nosetests

----------------------------------------------------------------------
Ran 0 tests in 0.049s

OK

> As we discussed the tasks you guys were asking are all done before I leave. Sorry that I leave earlier. Please let me know if you need any help. Good luck to your poster presentation and let me know the result! 