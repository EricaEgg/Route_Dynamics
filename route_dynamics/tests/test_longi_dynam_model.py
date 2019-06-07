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

class SimpleRouteTrajectory(ldm.RouteTrajectory):
    """ Build a simple test route with only a few route coordinates
        one unit apart and at constanstant route grate.
        """

    def __init__(self,
        shp_coords,
        bus_speed_model='stopped_at_stops__15mph_between',
        stop_coords=None,
        elevation_gradient_const=0,
        ):
        """
            """

        # Store algorithm name for future reference.
        self.bus_speed_model = bus_speed_model

        # The package implemented 'RouteTrajectory' class runs the
        # following method 'build_route_coordinate_df' to initialize
        # a GeoDataFrame with the following columns:
        #     - 'elevation'
        #     - 'cum_distance'
        #     - 'is_bus_stop

        # Simplify the route dataframe.
        self.route_df = self._simple_build_route_coordinate_df(
            shp_coords = shp_coords,
            stop_coords = stop_coords,
            elevation_gradient_const = elevation_gradient_const,
            )

        # TEST: Mark no stops for
        route_df = self._mark_stops(None, route_df)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Everything else in should be the same as package implementation
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        # Add 'velocity' column to route_df
        # This will also involve calulating the velocity.
        self.route_df = self._add_velocities_to_df(self.route_df)

        # Add 'acceleration' column to route_df
        self.route_df = self._add_accelerations_to_df(self.route_df)

        # Add passenger mass column to route_df
        self.route_df = self._add_passenger_mass_to_df(self.route_df)

        # Add force columns to route_df:
        #     - 'grav_force' : gravitation force determined by road grade
        #     - 'roll_fric' : rolling friction
        #     - 'aero_drag' : areodynamic drag
        #     - 'inertia' : inertial force, F = ma. Changes with passenger load
        #                   on bus.
        self.route_df = self._add_forces_to_df(self.route_df)

        # Add column to route_df containing instantaneous power experted by
        # bus at each point along route.
        self.route_df = self._add_power_to_df(self.route_df)

    def _simple_build_route_coordinate_df(self,
        shp_coords=None,
        stop_coords,
        elevation_gradient_const,
        ):
        """ Builds GeoDataFrame with rows cooresponding to points on
            route with columns corresponding to elevation, elevation
            gradiant, and connecting line segments between points in
            the form of Shapely Linstring objects.

            Also adds bus stop column and assigns bus stops based on
            'stop_coords' argument

            Args:
                'stop_coords': list of coordinates of bus stops. Will
                    assign points along bus route based on these values
                    .

            """

        if shp_coords is None:
            # Use default coordinates
            coordinates = [
                (0,0),
                (0,1),
                (0,2),
                (0,3),
                ]

        elif type(shp_coords) is list:
            # Might faul if list is not 2D coordinate tuples...
            coordinates = shp_coords

        # Build preliminary coordinate DataFrame
        route_2Dcoord_df = pandas.DataFrame(
            data=coordinates,
            index=None,
            columns='coordinates',
            )

        elevation_gradient = elevation_gradient_const * np.ones(len(coordinates))

        route_df = rbs.make_multi_lines(
            route_2Dcoord_df, # Dataframe with list of tuples in 'coordinate' column
            elevation_gradient, # Simple array
            )

        route_df = self._add_elevation_to_df(elevation, route_df)

        route_df = self._add_cum_dist_to_df(route_cum_distance, route_df)

        return route_df


class TestRouteTrajectory(object):
    """ Constructs route dataframe given the arguments;

        Args:
            route points (x,y)
            elevation (z)
            velocity

        returns:
            GeoDataFrame object with columns
        """
    def test_simple_route__no_grade(self):
        """
            """
        test_instance = SimpleRouteTrajectory(
            shp_coords=None,

            bus_speed_model='stopped_at_stops__15mph_between',
            stop_coords=None,
            elevation_gradient_const=0,
            )



    def test_constant_velocity(self):
        """ Test that RouteTrajectory instance by defaults returns
            constant velocity
            """

        test_instance = ldm.RouteTrajectory(
            route_num=test_route_num,
            shp_filename=shapefile_name,
            elv_raster_filename=rasterfile_name,
            bus_speed_model='constant_15mph',
            stop_coords=None,
            )

        inst_velocities = test_instance.route_df.velocity.values

        assert inst_velocities == np.ones(len(inst_velocities))*6.7056


    def test_one(self):
        """ Test that RouteTrajectory instance returns object with
            DataFrame attribute
            """

