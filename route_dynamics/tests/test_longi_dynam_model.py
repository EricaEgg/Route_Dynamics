""" Test for route_energy
	"""
from ..route_elevation import base as rbs
from ..route_energy import longi_dynam_model as ldm

import numpy as np
import pandas as pd

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


class IllegalArgumentErrorInTest(ValueError):
    """ """
    pass


class SimpleRouteTrajectory(ldm.RouteTrajectory):
    """ Build a simple test route with only a few route coordinates
        one unit apart and at constanstant route grate.
        """

    def __init__(self,
        shp_coords='default',
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
        self.route_df = self._add_dynamics_to_df(
            route_df=self.route_df,
            stop_coords=None,
            bus_speed_model=self.bus_speed_model,
            )

    def _simple_build_route_coordinate_df(self,
        shp_coords='default',
        stop_coords=None,
        elevation_gradient_const=0,
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

        if shp_coords is 'default':

            coordinates = [
                (0,0),
                (0,1),
                (0,2),
                (0,3),
                (0,4),
                (0,5),
                (0,6),
                ]

        elif type(shp_coords) is list:
            # Might faul if list is not 2D coordinate tuples...
            coordinates = shp_coords

        else:
            raise IllegalArgumentErrorInTest(
                "Bad input for 'shp_coords' arg of '_simple_build_route_coordi"
                "nate_df' method of class 'SimpleRouteTrajectory' in file 'tes"
                "t_longi_dynam_model'")

        # Build preliminary coordinate DataFrame
        route_2Dcoord_df = pd.DataFrame(
            data=pd.Series(coordinates),
            index=None,
            columns=['coordinates'],
            )

        elevation_gradient = elevation_gradient_const * np.ones(len(coordinates))

        route_df = rbs.make_multi_lines(
            route_2Dcoord_df, # Dataframe with list of tuples in 'coordinate' column
            elevation_gradient, # Simple array
            )

        # route_df = self._add_elevation_to_df(elevation, route_df)

        # route_df = self._add_cum_dist_to_df(route_cum_distance, route_df)

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

    test_instance__0_grade = SimpleRouteTrajectory(
        shp_coords='default',
        bus_speed_model='stopped_at_stops__15mph_between',
        stop_coords=None,
        elevation_gradient_const=0,
        )

    test_instance__1_grade = SimpleRouteTrajectory(
        shp_coords='default',
        bus_speed_model='stopped_at_stops__15mph_between',
        stop_coords=None,
        elevation_gradient_const=1,
        )

    constant_speed_instance__0_grade = SimpleRouteTrajectory(
        shp_coords='default',
        bus_speed_model='constant_15mph',
        stop_coords=None,
        elevation_gradient_const=0,
        )


    def test_simple_route__no_grade(self):
        """
            """

        test_instance = TestRouteTrajectory.test_instance__0_grade

        test_rdf = test_instance.route_df

        assert np.all(np.logical_not(test_rdf.gradient)), "gradient not all 0"

        # assert False, "{}".format(test_rdf)


    def test_energy_calc_yields_number(self):
        """Test that energy calculation performs a number"""

        test_instance = TestRouteTrajectory.test_instance__0_grade

        energy = test_instance.energy_from_route()

        assert (
            (type(energy) is float)
            or
            (type(energy) is np.float64)
            ),(
            "Energy is not a float.\n"
            "Likely due to first column of dataframe, head looks like...\n"
            "{}".format(test_instance.route_df.head())
            )


    def test_power_positive_for_flat_driving_constant_speed(self):

        inst = TestRouteTrajectory.constant_speed_instance__0_grade
        power_output_values = inst.route_df.power_output.values[1:]

        assert np.all(power_output_values>=0.0)

    def test_that_hills_are_harder_than_flat(self):

        flat_energy = (
            TestRouteTrajectory.test_instance__0_grade.energy_from_route()
            )

        hill_energy = (
            TestRouteTrajectory.test_instance__1_grade.energy_from_route()
            )

        assert flat_energy < hill_energy, (
            "The flat was harder than the hill...\n"
            "Energy output on flat route: {}\n"
            "Energy output on hill route: {}".format(flat_energy,hill_energy)
            )

    def test_that_downhills_are_easier_than_flat(self):

        flat_energy = (
            TestRouteTrajectory.test_instance__0_grade.energy_from_route()
            )

        downhill_instance = SimpleRouteTrajectory(
            shp_coords='default',
            bus_speed_model='stopped_at_stops__15mph_between',
            stop_coords=None,
            elevation_gradient_const=-1,
            )

        downhill_energy = (
            downhill_instance.energy_from_route()
            )

        assert flat_energy > downhill_energy, (
            "The flat was harder than the hill...\n"
            "Energy output on flat route: {}\n"
            "Energy output on hill route: {}".format(flat_energy,downhill_energy)
            )

    # Other test ideas,
    # - heavy bus vs light bus
    #

