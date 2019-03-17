import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from folium.features import GeoJson
import rasterio as rio
import rasterstats 
from shapely.geometry import Polygon, mapping, LineString
from geopy.distance import geodesic
import branca.colormap as cm

# reading shape files and mapping the route 
def read_shape(shapefile, route):
    fp = shapefile
    dat = gpd.read_file(fp)
    da = dat[dat['ROUTE_NUM'] == route]
    
    # da.to_file("da.shp")
    # points = folium.GeoJson(da.to_json())
    # map = folium.Map(location = [47.6, -122.3], zoom_start = 12).add_child(points)
    
    return(da)
    
# reading raster files and extract elevation 
def extract_elev(shapefile, route, rasterfile):
    da = read_shape(shapefile, route)
    raw_elev = pd.DataFrame(rasterstats.gen_point_query(da, rasterfile))
    elev = [x for x in raw_elev.iloc[0,:] if x is not None] 
    elev_meter = np.array(elev) * 0.3048
    
    return(elev_meter)


# extracting points from linestring 
def extract_point(shapefile, route):
    da = read_shape(shapefile, route)
    geoms = [mapping(da.geometry.values[0])]
    ge = np.array(geoms[0]['coordinates'])[:,[0,1]]

    coord = []
    for i in range(len(ge)):
            coord.append([ge[i][1], ge[i][0]])

    return(coord)


# map points 
def map_point(shapefile, route):
    coord = extract_point(shapefile, route)
    loca = pd.DataFrame(np.array(coord)).values.tolist()

    map = folium.Map(location=[47.6, -122.3], zoom_start=12)
    for point in range(0, len(loca)):
        folium.Marker(loca[point]).add_to(map)
    
    return(map)


# distance measure 
def dist_measure(shapefile, route):
    coord = extract_point(shapefile, route)
    dis = []
    for i in range(len(coord)-1):
        dis.append(geodesic(coord[i],coord[i+1]).m)

    dist = np.insert(np.cumsum(dis), 0, 0)
    
    return(dis, dist)

def gradient(shapefile, route, rasterfile):
    dis, dist = dist_measure(shapefile, route)
    elev = extract_elev(shapefile, route, rasterfile)
    stress = np.insert(abs(np.diff(elev)/ dis), 0, 0)
    
    return(dis, dist, elev, stress)


def make_multi_lines(shapefile, route, rasterfile):
    coord = extract_point(shapefile, route)
    dis, dist, elev, stress = gradient(shapefile, route, rasterfile)
    coord = np.column_stack((np.array(coord)[:,1], np.array(coord)[:,0]))
    line = [0]*(len(coord))
    for i in range(len(coord) - 1):
        first = coord[i]
        second = coord[i + 1]
        line[i+1] = LineString([first, second])
        
    line = gpd.GeoDataFrame(pd.DataFrame({'gradient': stress, 'geometry': line}).drop([0]))
    return line


def route_map(shapefile, route, rasterfile):
    line = make_multi_lines(shapefile, route, rasterfile)
    UW_coords = [47.6, -122.3]
    figure_size = folium.Figure(height = 400)
    route_map = folium.Map(location = UW_coords, zoom_start = 12)
    
    min_grade = min(line['gradient'])
    max_grade = max(line['gradient'])
    linear_map = cm.linear.RdYlBu_04.scale(min_grade, max_grade )
        
    route_layer = folium.GeoJson(line.to_json(), style_function = lambda feature: {
        'color': linear_map(feature['properties']['gradient']),
        'weight': 8})
    
    route_map.add_child(linear_map)
    route_map.add_child(route_layer)
    route_map.add_to(figure_size)
    
    return (route_map)


# route plots 
def profile_plot(shapefile, route, rasterfile):
    
    dis, dist, elev, stress = gradient(shapefile, route, rasterfile)
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(15, 8))
    
    ax[0].plot(dist, elev, label= 'elevation', color='b', linewidth=4)
    ax[0].set_ylabel('Elevation (meter)', color='b')
    ax[0].tick_params('y', colors='b')
    ax[0].legend()
    ax[0].grid()
    
    # ax[1] = ax.twinx()
    ax[1].plot(dist, stress, label= 'stress index', color='r')
    ax[1].set_xlabel('Plain distance (meter)')
    ax[1].set_ylabel('Stress index', color='r')
    ax[1].tick_params('y', colors='r')
    ax[1].legend()
    ax[1].grid()
    
    return

# Medium fuction for the 4 metrics
def ss(shapefile, route, rasterfile):
    '''
    Function: This function measures the metrics of stress in 4 different ways.
    
    Input
        shapefile: shapefile of bus routes
        route: bus number
        rasterfile: rasterfile of Lidar elevation 
        
    Output
        4 values of metrics 
    '''
    dis, dist, elev, stress = gradient(shapefile, route, rasterfile)
    s1 = 100* sum(stress)/ max(dist) 
    s2 = sum(abs(np.diff(elev)))/ max(dist)
    s3 = 100* sum(np.insert(np.diff(elev)/ dis, 0, 0)[np.insert(np.diff(elev)/ dis, 0, 0) > 0])/ max(dist)
    s4 = - 100* sum(np.insert(np.diff(elev)/ dis, 0, 0)[np.insert(np.diff(elev)/ dis, 0, 0) < 0])/ max(dist)
    
    return(s1, s2, s3, s4)

# Bar chart and table 
def stress_cal(shapefile, num_list, rasterfile):
    '''
    Function: This function shows 4 metrics of stress measure in table and bar chart.
    
    Input
        shapefile: shapefile of bus routes
        num_list: a list of bus numbers 
        rasterfile: rasterfile of Lidar elevation 
        
    Output
        Barchart and table of 4 metrics for stress measure
    '''
  
    num = len(num_list)
    s1 = [0]*num
    s2 = [0]*num
    s3 = [0]*num
    s4 = [0]*num
    for i in range(num):
        s1[i], s2[i], s3[i], s4[i] = ss(shapefile, num_list[i], rasterfile)
        print('\n')

    data = pd.DataFrame({'Bus Num': num_list, 'M1': s1, 'M2': s2, 'M3': s3, 'M4': s4})
    ax = data.plot.bar('Bus Num', figsize= [14, 5], fontsize= 20)
    ax.set_ylabel('Metrics', size= 20)
    ax.set_xlabel('Bus Number', size= 20)
    
    return(data)
