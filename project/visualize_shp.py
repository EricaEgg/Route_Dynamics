import numpy as np
import pandas as pd
import folium
import geopandas as gpd
from folium.plugins import MarkerCluster

UW_coords = [47.6628, -122.3139]
my_map = folium.Map(location = UW_coords, zoom_start = 12) # create the map ,center is UW.

fp = '../data/Transit_Routes_for_King_County_Metro__transitroute_line.shp' 
data = gpd.read_file(fp)
gjson = data.to_json() # convert shp file to geojson.
points = folium.GeoJson(gjson)
my_map.add_child(points) # add layer into map.


fp45 = '../data/Transit_Routes_for_King_County_Metro__transitroute_line.shp'
data = gpd.read_file(fp45)
r45 = data[data['ROUTE_NUM']==45]
gjson = r45.to_json()
point45 = folium.GeoJson(gjson)
my_map.add_child(point45)
