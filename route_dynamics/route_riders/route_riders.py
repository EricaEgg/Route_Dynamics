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
dat1 = pd.read_csv("../data/Trip183.csv") # KCM Data
dat2 = pd.read_csv("../data/Zon183Unsum.csv") # KCM Data

# Removing all unneeded columns
trip183 = dat1[['SignRt', 'InOut', 'KeyTrip', 'BusType', 'Seats', 
					 'Period', 'AnnRides']]
trip183unsum = dat2[['Route', 'Dir', 'Trip_ID', 'InOut', 'STOP_SEQ', 'STOP_ID',
                     'Period', 'AveOn', 'AveOff', 'AveLd', 'Obs']]

# Dictionary created using data from King County Metro
# Relates bus type to bus mass (many are approximations)
bus_mass = {
    11: 11000,
    26: 19051,
    32: 11793,
    36: 11793,
    37: 12247,
    43: 14913,
    45: 19051,
    46: 18835,
    60: 19051,
    62: 19051,
    68: 19051,
    70: 12927,
    72: 12927,
    73: 12927,
    80: 19051,
    81: 19051,
    82: 19051,
    90: 12927,
    91: 12927,
    92: 12927,
    95: 19051,
    96: 19051
        }

# Creating a new dictionary relating Trip_ID to buss mass
trip183 = trip183.replace({'BusType': bus_mass})
trip_mass = trip183[['BusType', 'KeyTrip']]
trip_dict = dict(zip(trip_mass.KeyTrip, trip_mass.BusType))


def route_ridership(period, route):
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

    final_df = df.sort_values(by=['Trip_ID', 'STOP_SEQ', 'STOP_ID'])
    seq_id = final_df[['STOP_SEQ', 'STOP_ID']]
    seq_id2 = seq_id.drop_duplicates(subset=['STOP_SEQ'], keep='first')
    seq_id3 = seq_id2.sort_values(by='STOP_SEQ')
    stopid_dic = dict(zip(seq_id3.STOP_SEQ, seq_id3.STOP_ID))
    riders = final_df.pivot(index='STOP_SEQ', columns='Trip_ID', values='AveLd')

    keyfind = list(riders.columns)
    mass_bus = [trip_dict[x] for x in keyfind]
    mode = mode_mass = max(set(mass_bus), key=mass_bus.count)
    rider_columns = list(riders.columns)
    kept_columns = []

    for i in range(0, len(mass_bus)):
        if mass_bus[i] == mode:
            kept_columns.append(rider_columns[i])

    riders_interm = riders[kept_columns]
    riders_kept = pd.DataFrame((riders_interm.mean(axis=1)), columns=['Mean'])
    riders_kept.Mean*=80
    riders_kept.reset_index(inplace=True)
    riders_kept.replace({"STOP_SEQ": stopid_dic}, inplace=True)
    riders_kept.columns = ['STOP_ID', 'Mean']

    return final_df, riders_kept, mode_mass



def stop_coord(num, riders_num):
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
    routes_shp = '../data/rt' + str(num) + '_pts.shp'
    stops_shp = '../data/Transit_Stops_for_King_County_Metro__transitstop_point.shp'

    route_num = num

    route = base.create_gdf(routes_shp)
    #points = base.extract_point_df(route)
    stops = gpd.read_file(stops_shp)
    stops['ROUTE_LIST'].fillna(value=str(0), inplace=True)

    stops_list = pd.DataFrame()
    for i in range(0, len(stops)):

        if str(route_num) in (stops['ROUTE_LIST'][i]):
            for x in stops['ROUTE_LIST'][i].split(' '):
                if str(route_num) == x:
                    stops_list = stops_list.append(stops.iloc[i])
                else:
                    pass
        else:
            pass

    stop_ids = stops_list['STOP_ID'].values

    geometry = stops_list.geometry.values

    xy = []
    for i in range(len(geometry)):
        dic = mapping(geometry[i])
        coords = dic['coordinates']
        xy.append(coords)
        xy_df = pd.DataFrame(columns = ['STOP_ID','coordinates'])
        xy_df['coordinates'] = xy

    xy_df['STOP_ID'] = stops_list['STOP_ID'].values

    df = riders_num
    df_ind = df.reset_index()
    df_ind.columns = ['STOP_SEQ', 'STOP_ID', 'Mean']

    df_comb = xy_df.merge(df_ind, how='right', on="STOP_ID")
    df_comb = df_comb.drop_duplicates(subset=['STOP_ID'], keep='first')
    df_comb = df_comb[['STOP_SEQ', 'STOP_ID', 'coordinates', 'Mean']]
    df_combine = df_comb.sort_values(by='STOP_SEQ')

    return xy_df, df_combine
