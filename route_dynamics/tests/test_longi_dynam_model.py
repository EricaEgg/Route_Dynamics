""" Test for route_energy
	"""
from ..route_elevation import base as rbs
from ..route_energy import longi_dynam_model as ldm

import numpy as np

shapefile = '../data/six_routes.shp'
rasterfile = '../data/seattle_dtm.tif'

test_route_num = 45
route_list = [48, 50, 75, 7, 45, 40]

route_shp = rbs.read_shape(shapefile, test_route_num)

# Use 2D coordinates and elevation rasterfile to generate
# elevations and elevation gradiant at each point.
(
    elevation,
    elevation_gradient,
    route_cum_distance,
    distance
    ) = rbs.gradient(route_shp, rasterfile)

# Build dataframe of 2D coordinates making up bus route
test_route_coord_df = rbs.extract_point_df(route_shp)


class TestRouteTrajectory(object):
    """ Constructs route dataframe given the arguments;

        Args:
            route points (x,y)
            elevation (z)
            velocity

        returns:
            GeoDataFrame object with columns
        """
    def test_one(self):
        """ Test that """

        constant_velocity = np.ones(test_elevations)

        test_instance = ldm.RouteDataFrame(
            test_route_coords,
            test_elevations,
            constant_velocity)

