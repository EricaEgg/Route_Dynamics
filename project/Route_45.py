# Import useful Modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
# import geopandas as gpd
import folium
from folium.features import ColorLine

# Functions
def alt_color(route_45_z):
    colors = ['#0000FF', '#0040FF', '#0080FF', '#00FFB0', '#00E000',
              '#80FF00', '#FFFF00', '#FFC000', '#FF0000']
    route_alt_range = np.linspace(min(route_45_z), max(route_45_z), len(colors))
    color_alt = []
    for idx in range(len(route_45_z) - 1):
        alt_1 = route_45_z[idx]
        index_1 = np.where(route_alt_range <= alt_1)[0][-1]
        color_alt.append(colors[index_1])

    return color_alt

# Read in data
fp = './data/route45_xyz.csv'
route_45_full = pd.read_csv(fp)
route_45_full.head()

# Extract xyz data from the full route data
route_45 = route_45_full[['Lat', 'Long', 'Z (ft)']]
route_45 = route_45.rename(columns = {'Z (ft)':'Alt'})
route_45.head()

# Split extracted data into lat and long (xy) and elevation(z)
route_45_xyz = np.array(route_45)
route_45_xy = route_45_xyz[:, :2].tolist()
route_45_z = route_45_xyz[:,2].tolist()

# Add lat and long data to map and display
route_line = folium.PolyLine(route_45_xy, weight=3, color='red').add_to(route_45_map)
route_45_map

# Include elevation data using colors with lat and long data on map and display
colors_alt = alt_color(route_45_z)
route_alt = ColorLine(route_45_xy, colors=list(range(0, len(route_45_z))),
              colormap=colors_alt, weight=3).add_to(route_45_map)

route_45_map.fit_bounds(route_45_map.get_bounds())
route_45_map