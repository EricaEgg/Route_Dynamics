import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


from scipy.signal import savgol_filter as sf


def create_gdf(shapefile, pt_distance):
    """
        Loads shapefile into GeoDataFrame with original point distance

        Parameters
        ----------
        shapefile: route geospatial data (.shp file)
        pt_distance: distance between points (in ft)

        Returns
        -------
        route_shp: route_df
        """

    route_df = gpd.read_file(shapefile)
    
    x = []

    for i in route_df.index:
    
        x.append(i*pt_distance)
    

    route_df['distance'] = x
    route_df = route_df.rename(columns = {'Z':'elevation'})
    route_df = route_df.rename(columns = {'SPEED_LIM':'speed_limit'})
    #route_df = route_df.drop(columns=['Id','ORIG_FID', 'SHAPE_Leng'])
    route_df = route_df[['geometry', 'distance', 'elevation', 'speed_limit']]
    
    return route_df

def metric_df(df, frequency):
    """
        Converts dataframe units to metric. Also, set how many points to evaluate. 

        Parameters
        ----------
        df: geodataframe
        frequency: how many points to keep. For example, if frequency=6, every 6th point is kept. 

        Returns
        -------
        route_shp: metric route dataframe
        """
    df = df.iloc[::frequency]
    df = df.reset_index()
    del df['index']
    df['distance'] *= 0.3048
    df['elevation'] *= 0.3048
    df['speed_limit']/= 2.237
    
    return df, df['distance'][1]

def filters(route_df):
    """
        Uses a SG filter to smooth elevation profile. 

        Parameters
        ----------
        route_df: geodataframe 

        Returns
        -------
        y_new: filtered elevation values
        """
    
    points = route_df['elevation'].values

    y_new = sf(points, 43, 3,  axis = 0) 
    
    return y_new


def grade(y_new, distance):
    """
        Calculates road grade 

        Parameters
        ----------
        route_df: geodataframe
        distance: distance between points (in meters)

        Returns
        -------
        y_new: filtered elevation values
        """
    
    grade_SG = [0]

    for i in range(1,len(y_new)):
        grade_SG.append((y_new[i]-y_new[i-1])/distance)
    
    return grade_SG


def wrapper(shapefile, pt_distance, frequency):
    """
        Wrapper function: creates initial geodataframe with distance along route and filtered elevation.  

        Parameters
        ----------
        route_df: geodataframe
        pt_distance: distance between points 
        frequency: how many points included

        Returns
        -------
        y_new: filtered elevation values
        """

    route_df = create_gdf(shapefile, pt_distance)
    
    route_df, distance = metric_df(route_df, frequency)

    route_df['elevation'] = filters(route_df)

    route_df['grade'] = grade(route_df['elevation'].values, distance)

    return route_df

