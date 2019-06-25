import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import route_dynamics.route_elevation.base as base
import geopandas as gpd
from shapely.geometry import mapping
import sys
from os import path


#sys.path.append(path.abspath('..'))

import route_elevation.base as base
from route_riders import route_riders as ride

period = 'AM'
direction = 'I'
route_num = 45


def test_route_ridership(period, direction, route):

    temp_df, temp_riders, temp_mass = ride.route_riders(period, direction, route_num)

    #assert

    return


def stop_coord(num, riders_num):



    return
