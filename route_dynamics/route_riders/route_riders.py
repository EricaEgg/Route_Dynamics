import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dat1 = pd.read_csv('Trip183.csv')
dat2 = pd.read_csv('Zon183Unsum.csv')
trip183 = dat1[['SignRt', 'InOut', 'KeyTrip', 'BusType', 'Seats',
                'Period', 'AnnRides']]
trip183unsum = dat2[['Route', 'Dir', 'Trip_ID', 'InOut', 'STOP_SEQ', 'Period',
                     'AveOn', 'AveOff', 'AveLd', 'Obs']]

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

trip183 = trip183.replace({'BusType': bus_mass})
trip_mass = trip183[['BusType', 'KeyTrip']]
trip_mass.head()
trip_dict = dict(zip(trip_mass.KeyTrip, trip_mass.BusType))


def route_ridership(period, direction, route):
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
    df = df.drop(df[(df.InOut != direction)].index)
    df = df.drop(df[(df.Route != route)].index)

    final_df = df.sort_values(by=['Trip_ID', 'STOP_SEQ'])
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

    return final_df, riders_kept, mode_mass
