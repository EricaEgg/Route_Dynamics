""" Test for route_energy
	"""
from ..route_elevation import base as rbs
from ..route_energy import longi_dynam_model as ldm
import simple_route as sro

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


class TestRouteTrajectory(object):
    """ Constructs route dataframe given the arguments;

        Args:
            route points (x,y)
            elevation (z)
            velocity

        returns:
            GeoDataFrame object with columns
        """

    test_instance__0_grade = sro.SimpleRouteTrajectory(
        route_coords='default',
        bus_speed_model='stopped_at_stops__15mph_between',
        stop_coords=None,
        elevation_gradient_const=0,
        )

    test_instance__1_grade = sro.SimpleRouteTrajectory(
        route_coords='default',
        bus_speed_model='stopped_at_stops__15mph_between',
        stop_coords=None,
        elevation_gradient_const=1,
        )

    constant_speed_instance__0_grade = sro.SimpleRouteTrajectory(
        route_coords='default',
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

        downhill_instance = sro.SimpleRouteTrajectory(
            route_coords='default',
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

    def test_single_stop_manual(self):

        stop_coord = [(0.542, 6.05),]

        instance = sro.SimpleRouteTrajectory(
            route_coords='default',
            bus_speed_model='stopped_at_stops__15mph_between',
            stop_coords=stop_coord,
            elevation_gradient_const=0,
            )

        assert instance.route_df.iloc[6].is_bus_stop, (
            "{} not marked by stop coord {}".format(
                instance.route_df.iloc[6].coordinates,
                stop_coord
                )
            )


    def test_single_stop_manual(self):

        stop_coord = [
            (0.542, 6.05), # Should mark (0,6)
            (3.542, 1.98), # Should mark (0,2)
            ]

        instance = sro.SimpleRouteTrajectory(
            route_coords='default',
            bus_speed_model='stopped_at_stops__15mph_between',
            stop_coords=stop_coord,
            elevation_gradient_const=0,
            )

        assert (
            instance.route_df.iloc[6].is_bus_stop
            and
            instance.route_df.iloc[2].is_bus_stop
            ), (
            "{} not marked by stop coord {}"
            "\n"
            "{} not marked by stop coord {}".format(
                instance.route_df.iloc[6].coordinates,
                stop_coord[0],
                instance.route_df.iloc[2].coordinates,
                stop_coord[1]
                )
            )





    # Other test ideas,
    # - heavy bus vs light bus
    #

