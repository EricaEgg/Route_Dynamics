import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


from scipy.signal import savgol_filter as sf


def create_gdf(shapefile, frequency):
    """
        Loads shapefile into GeoDataFrame with original point distance

        Parameters
        ----------
        shapefile: route geospatial data (.shp file)
        frequency: distance between stops (in ft)

        Returns
        -------
        route_shp: Filtered gdf
        """

    route_df = gpd.read_file(shapefile)
    
    x = []

    for i in route_df.index:
    
        x.append(i*frequency)
    

    route_df['distance'] = x
    route_df = route_df.drop(columns=['Id','ORIG_FID', 'SHAPE_Leng'])
    
    return route_df

def metric_df(df):
    df = df.iloc[::6]
    df = df.reset_index()
    df = df[['geometry', 'distance', 'Z']]
    df = df.rename(columns = {'Z':'elevation'})
    df['distance'] *= 0.3048
    df['elevation'] *= 0.3048
    
    return df


def filters(route_df):
    
    points = route_df[('elevation')].values

    y_new = sf(points, 43, 3,  axis = 0) 
    
    return y_new


def grade(y_new):
    
    grade_SG = [0]

    for i in range(1,len(y_new)):
        grade_SG.append((y_new[i]-y_new[i-1])/10.97)
    
    return grade_SG


def wrapper(shapefile):

    route_df = create_gdf(shapefile, 6)
    
    route_df = metric_df(route_df)

    route_df['elevation'] = filters(route_df)

    route_df['grade'] = grade(route_df['elevation'].values)

    return route_df

