import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


from scipy.signal import savgol_filter as sf


def create_gdf(shapefile):
    """
        Loads shapefile into GeoDataFrame 

        Parameters
        ----------
        shapefile: route geospatial data (.shp file)

        Returns
        -------
        route_shp: Filtered gdf
        """

    route_df = gpd.read_file(shapefile)
    
    x = []

    for i in route_df.index:
    
        x.append(i*6) # 6 is to indicate points are 6 ft apart
    

    route_df['length'] = x
    route_df = route_df.drop(columns=['Id','ORIG_FID', 'SHAPE_Leng'])
    
    return route_df


def filters(route_df):
    
    points = route_df[('Z')].values

    y_new = sf(points, 439, 3,  axis = 0) 
    
    return y_new


def grade(rt_df, y_new):
    
    grade_SG = [0]

    for i in range(1,len(y_new)):
        grade_SG.append((y_new[i]-y_new[i-1])/6)
    
    return grade_SG


def wrapper(shapefile):

	route_df = create_gdf(shapefile)

	route_df['Z'] = filters(route_df)

	route_df['grade'] = grade(route_df, route_df['Z'])

	return route_df

