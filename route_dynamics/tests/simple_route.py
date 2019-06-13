""" Simper route used for tests """
from ..route_elevation import base as rbs
from ..route_energy import longi_dynam_model as ldm
from ..route_energy import knn

import numpy as np
import pandas as pd


class IllegalArgumentErrorInTest(ValueError):
    """ """
    pass


class SimpleRouteTrajectory(ldm.RouteTrajectory):
    """ Build a simple test route with only a few route coordinates
        one unit apart and at constanstant route grate.
        """

    def __init__(self,
        route_coords='default',
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
            route_coords = route_coords,
            # stop_coords = stop_coords,
            elevation_gradient_const = elevation_gradient_const,
            )

        # TEST: Mark no stops for
        self.route_df = self._add_dynamics_to_df(
            route_df=self.route_df,
            stop_coords=stop_coords,
            bus_speed_model=self.bus_speed_model,
            )

    def _simple_build_route_coordinate_df(self,
        route_coords='default',
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

        if route_coords is 'default':

            coordinates = [
                (0,0),
                (0,1),
                (0,2),
                (0,3),
                (0,4),
                (0,5),
                (0,6),
                (0,7),
                (0,8),
                (0,9)
                ]

        elif type(route_coords) is list:
            # Might faul if list is not 2D coordinate tuples...
            coordinates = route_coords

        else:
            raise IllegalArgumentErrorInTest(
                "Bad input for 'route_coords' arg of '_simple_build_route_coordi"
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

        back_diff_distance = np.ones(len(coordinates)-1)
        for i in range(len(coordinates)-1):
            back_diff_distance[i] = knn.euclidean_distance(
                coordinates[i+1],
                coordinates[i]
                )

        route_df = self._add_distance_to_df(back_diff_distance, route_df)

        # route_df = self._add_elevation_to_df(elevation, route_df)

        # route_df = self._add_cum_dist_to_df(route_cum_distance, route_df)

        return route_df