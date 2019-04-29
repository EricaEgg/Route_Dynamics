""" Implementation of the Longitudinal Dynamics Model for work done by
    the bus engine along route.

    From:
        Asamer J, Graser A, Heilmann B, Ruthmair M. Sensitivity
        analysis for energy demand estimation of electric vehicles.
        Transportation Research Part D: Transport and Environment.
        2016 Jul 1;46:182-99.

    """

from ..route_elevation import single_route as rsr
from ..route_elevation import base as rbs

import numpy as np
import geopandas as gpd


# Thinking this is not the best implementation since I don't actually
# know how to make objects print like pandas DataFrames.
class RouteTrajectory(object)
    """ Takes 2d route coordinates extracted from shapefile and
        combines the information with elevation to create a route
        trajectory dataframe.
        """

    def __init__(self, xy_route_coords, route_elevation):
        """ Build DataFrame with bus trajectory and shapely connections
            for plotting.
            """
            # route_df = gpd.dataframe()


    def calculate_forces(self):
        """ Calculate forces on bus relevant to the Longitudinate
            dynamics model.
            """


    def calculate_energy_demand(self):


    def calculate_power(self)




