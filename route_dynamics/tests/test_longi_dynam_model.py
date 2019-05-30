""" Test for route_energy
	"""
from ..route_elevation import base as rbs
from ..route_energy import longi_dynam_model as ldm

import numpy as np

# Load files for tests.
shapefile_name = '../data/six_routes.shp'
rasterfile_name = '../data/seattle_dtm.tif'

test_route_num = 45
route_list = [48, 50, 75, 7, 45, 40]

# route_shp = rbs.read_shape(shapefile_name, test_route_num)

# # Use 2D coordinates and elevation rasterfile_name to generate
# # elevations and elevation gradiant at each point.
# (
#     elevation,
#     elevation_gradient,
#     route_cum_distance,
#     distance
#     ) = rbs.gradient(route_shp, rasterfile_name)

# # Build dataframe of 2D coordinates making up bus route
# test_route_coord_df = rbs.extract_point_df(route_shp)


class TestRouteTrajectory(object):
    """ Constructs route dataframe given the arguments;

        Args:
            route points (x,y)
            elevation (z)
            velocity

        returns:
            GeoDataFrame object with columns
        """
    def test_constant_velocity(self):
        """ Test that RouteTrajectory instance by defaults returns
            constant velocity
            """

        test_instance = ldm.RouteTrajectory(
            route_num=test_route_num,
            shp_filename=shapefile_name,
            elv_raster_filename=rasterfile_name,
            # bus_speed_model_name='test' by default
            # stop_coords=None by default
            )

        inst_velocities = test_instance.route_df.velocity.values

        assert inst_velocities == np.ones(len(inst_velocities))*6.7056


    def test_one(self):
        """ Test that RouteTrajectory instance returns object with
            DataFrame attribute
            """

