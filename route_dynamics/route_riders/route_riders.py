import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import os
from os import path
import sys
from shapely.geometry import mapping

#sys.path.append(path.abspath('..'))
import route_dynamics.route_elevation.base_df as base
dat1 = pd.read_csv("../data/Trip183.csv", usecols = ['SignRt', 'InOut', 'KeyTrip', 'BusType', 'Seats', 
                     'Period', 'AnnRides']) # KCM Data
dat2 = pd.read_csv("../data/Zon183Unsum.csv", usecols = ['Route', 'Dir', 'Trip_ID', 'InOut', 'STOP_SEQ', 'STOP_ID',
                     'Period', 'AveOn', 'AveOff', 'AveLd', 'Obs']) # KCM Data

# Removing all unneeded columns
trip183 = dat1
trip183unsum = dat2


def route_ridership(period, route, empty_bus):
    """
    Calculates ridership mass from King County Metro ridership statistics. An
    average ridership is used and is specific to a specific route, direction,
    and segment during the day. Not date specific.

    Inputs:
    period - A block of time, options are 'AM', 'MID', 'PM', 'XEV', 'XNT'
    direction - Inbound 'I' or Outbound 'O'
    route - King County Metro Route Number

    Outputs:
    final_df - A pandas DataFrame with all raw ridership data
    riders_kept - A DataFrame with the average ridership in kilograms as it
        changes between stops with the most common bus type for the specified
        parameters
    mode_mass - Mass of the most frequently used bus type for the given
        parameters with no riders

    """

    df = trip183unsum
    df = df.drop(df[(df.Period != period)].index)
    #df = df.drop(df[(df.InOut != direction)].index)
    df = df.drop(df[(df.Route != route)].index)

    final_df = df.sort_values(by=['InOut','Trip_ID', 'STOP_SEQ', 'STOP_ID'])
    final_df = final_df[['InOut','STOP_SEQ', 'STOP_ID', 'AveLd']]
    final_df = final_df.drop_duplicates(subset=['InOut','STOP_SEQ'], keep='first')
    final_df = final_df.sort_values(by=['InOut','STOP_SEQ'])
    final_df = final_df.reset_index()

    final_df['Pass_Mass'] = final_df['AveLd']*80
    final_df['Total_Mass'] = final_df['Pass_Mass'] + empty_bus

    coord_list = stop_coord(route)

    filler = np.zeros(len(final_df))
    final_df = final_df.assign(geometry = filler)

    for i in range(len(final_df)):
        stopid = final_df['STOP_ID'].iloc[i]
        copy = coord_list.loc[coord_list['STOP_ID'] == stopid].geometry.values
        final_df['geometry'].iloc[i] = copy

    return final_df


def stop_coord(num):
    """
    Uses riders_kept data frame from route ridership to incorporate the
    link between stop coordinates and stop IDs.

    Inputs:
    num - Route Number
    riders_num - Data Frame of riders organized by stop sequence and mass_bus
        (use riders_kept output from route_riders)

    Outputs:
    xy_df - Data Frame of bus stop coordinates for route
    df_combine - Final Data Frame with STOP_ID, stop coordinates, and
        ridership mass, organized by STOP_SEQ

    """
    routes_shp = '../data/rt' + str(num) + '_pts2.shp'
    stops_shp = '../data/Transit_Stops_for_King_County_Metro__transitstop_point.shp'

    route_num = num

    stops = gpd.read_file(stops_shp)
    stops['ROUTE_LIST'].fillna(value=str(0), inplace=True)

    stops_list = pd.DataFrame(columns=stops.columns)
    for i in range(0, len(stops)):

        if str(route_num) in (stops['ROUTE_LIST'][i]):
            for x in stops['ROUTE_LIST'][i].split(' '):
                if str(route_num) == x:
                    row = pd.DataFrame(stops.iloc[i])
                    stops_list = pd.concat([stops_list,row.transpose()])
                else:
                    pass
        else:
            pass

    coord_list_full = stops_list.drop_duplicates('STOP_ID')
    coord_list = coord_list_full[['STOP_ID', 'geometry']]
    coord_list = coord_list.reset_index(drop=True)

    return coord_list