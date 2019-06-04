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


class PlottingTools(object):
    """ Place holder for now, but eventually this will wrap up the
        plotting tools written by last quarter's RouteDynamics team.
        """

    def __init__(self):
        pass


# Thinking this is not the best implementation since I don't actually
# know how to make objects print like pandas DataFrames.
class RouteTrajectory(PlottingTools):
    """ Takes 2d route coordinates extracted from shapefile and
        combines the information with elevation to create a route
        trajectory dataframe.

        """

    def __init__(self,
        route_num,
        shp_filename,
        elv_raster_filename,
        bus_speed_model_name='test',
        stop_coords=None,
        ):
        """ Build DataFrame with bus trajectory and shapely connections
            for plotting. This object is mostly a wrapper object to
            build and return the Route DataFrame, but will later
            contain plotting methods as well.


            Args:

                route_num: needs to be one that Erica made work.

                bus_speed_model_name:
                    Right now the argument 'bus_speed_model_name' is
                    set to 'test' by default, which causes the speed to
                    be set at a constant velocity of 6.7056 [m/s],
                    which is equal to 15 mph. Later this will accept
                    arguments like 'parabolic_between_stops' or maybe
                    even something smarter that includes trtaffic.

            Methods:

                ...

            """

        # Assign attributes from __init__ args
        self.route_num = route_num
        self.route_shp_filename = route_shp_filename
        self.elv_filename = elv_filename
        self.stop_coords = stop_coords

        # Build Route DataFrame, starting with columns:
        #     - 'elevation'
        #     - 'cum_distance'
        #     - 'is_bus_stop
        self.route_df = self.build_route_coordinate_df(
            route_num = self.route_num,
            route_shp_filename = self.route_shp_filename,
            elv_filename = self.elv_filename,
            stop_coords = self.stop_coords,
            )

        # Add 'velocity' column to route_df
        # This will also involve calulating the velocity.
        self.route_df = self._add_velocities_to_df(self.route_df)

        # Add 'acceleration' column to route_df
        self.route_df = self._add_accelerations_to_df(self.route_df)

        # Add force columns to route_df:
        #     - 'grav_force'
        #     - 'roll_fric'
        #     - 'aero_drag'
        #     - 'inertia'
        self.route_df = self._add_forces_to_df(self.route_df)

        # Add '' column to route_df
        self.route_df = self._add_power_to_df(self.route_df)


    def build_route_coordinate_df(self,
        route_num,
        route_shp_filename,
        elv_filename,
        stop_coords,
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

        # Build the df of 2D route coordinates and
        route_shp = rbs.read_shape(route_shp_filename, route_num)

        route_2Dcoord_df = rbs.extract_point_df(route_shp)

        (
            elevation,
            elevation_gradient,
            route_cum_distance,
            distance
            ) = rbs.gradient(route_shp, elv_filename)

        route_df = rbs.make_multi_lines(
            route_2Dcoord_df,
            elevation_gradient
            )

        route_df = self._add_elevation_to_df(elevation, route_df)

        route_df = self._add_cum_dist_to_df(route_cum_distance, route_df)

        # Try to determine bus stops from list of coordinates
        route_df = self._mark_stops(stop_coords, route_df)

        return route_df


    def _mark_stops(self, stop_coords, route_df):
        """ Find rows in route_df matching the stop_coordinates and
            mark as bus stop under new column.
            """

        # By default, 'stop_coords' is set to 'None', if this is true,
        # then 10 bus stops will be assigned randomly
        if stop_coords is None:
            # Randomly select certain route coordinates to be marked as
            # a stop with 5% probability.
            # Fix seed for reproducability
            np.random.seed(5615423)
            # Return binary array with value 'True' 5% of time
            is_stop_binary_array = (
                np.random.random(len(route_df.index)) < .05
                )

            rdf = route_df.assign(
                is_bus_stop = ([False] * len(route_df.index))
                )

        else: # UNDER CONSTRUCTION
            # Add new column to 'route_df' filled with 0 (or anything that
            # evaluates to binary 'False').
            rdf = route_df.assign(
                is_bus_stop = ([False] * len(route_df.index))
                )
            # Look through coordinate column in 'route_df' and if matches
            # element in 'stop_coordinates' change value in 'stops' column
            # to 'True'.

            # Raise 'AssersionError' if bus stop coordinate not found in
            # 'route_df'.

            # return modified 'route_df'
            assert (True == False), ("Have not implemented stops yet")

        return rdf


    def _add_elevation_to_df(self, elevation, route_df):

        rdf = route_df.assign(
            elevation=elevation
            )

        return rdf


    def _add_cum_dist_to_df(self, cum_distance, route_df):

        rdf = route_df.assign(
            cum_distance=cum_distance
            )

        return rdf


    def _add_velocities_to_df(self, route_df):
        """ For now just adds a constant velocity as a placeholder.
            """

        # 'test' algorithm set by default for now.
        if self.bus_speed_model_name == 'test':
            # Assign constant velocity of 6.7056 m/s (= 15 mph)
            constant_bus_speed_array = 6.7056 * np.ones(len(route_df))

        elif self.bus_speed_model_name == 'test_stops':
            # Really I want something here to use the stop array to calcularte bus speed.
            # Step !: Calculate distance to next stop, which should determine the strajectory (speed at point)
                # can use difference of 'cum_dist's
            # 2) Assign trajectory as function of distance
            # 3) plug in each route point between stops intor trajectory function.

        rdf = route_df.assign(
            velocity=constant_bus_speed_array
            )

        return rdf


    def _add_accelerations_to_df(self, route_df):
        """ For now just adds a acceleration velocity as a placeholder.
            """
        velocity_array = route_df.velocity.values

        delta_distance_array = self.distance_array_from_linestrings(route_df)

        accelerations = np.diff(velocity_array) / delta_distance_array

        rdf = route_df.assign(
            acceleration=accelerations
            )

        return rdf


    def _add_forces_to_df(self, route_df):
        """ Calculate forces on bus relevant to the Longitudinate
            dynamics model.
            """

        (
            grav_force,
            roll_fric,
            aero_drag,
            inertia
            ) = self.calculate_forces(route_df)

        route_df = route_df.assign(
            grav_force = grav_force,
            roll_fric = roll_fric,
            aero_drag = aero_drag,
            inertia = inertia,
            )

        return route_df


    def calculate_forces(self, rdf):


        vels = rdf.velocity.values
        acce = rdf.acceleration.values
        grad = rdf.gradient.values
        grad_angle = np.arctan(grad)

        # Physical parameters
        gravi_accel = 9.81
        air_density = 1.225 # air density in kg/m3; consant for now, eventaully input from weather API
        v_wind = 0.0 #wind speed in km per hour; figure out component, and also will come from weather API
        fric_coeff = 0.01

        # List of Bus Parameters for 40 foot bus
        mass = 12927 # Mass of bus in kg
        width = 2.6 # in m
        height = 3.3 # in m
        bus_front_area = width * height
        drag_coeff = 0.34 # drag coefficient estimate from paper (???)
        rw = 0.28575 # radius of wheel in m

        # Calculate the gravitational force
        grav_force = mass * gravi_accel * np.sin(grad_angle)

        # Calculate the rolling friction
        roll_fric = fric_coeff * mass * gravi_accel * np.cos(grad_angle)

        # Calculate the aerodynamic drag
        aero_drag = (
            drag_coeff
            *
            bus_front_area
            *
            (air_density/2)
            *
            (vels-v_wind)
            )

    #     # Calculate the inertial force
        inertia = mass * acce

        return (grav_force, roll_fric, aero_drag, inertia)


    def _calculate_batt_power_exert(self, rdf):

        f_resist = (
            rdf.grav_force.values
            +
            rdf.roll_fric.values
            +
            rdf.aero_drag.values
            )

        f_traction = rdf.inertia.values - f_resist
        velocity = rdf.velocity.values

        batt_power_exert = f_traction * velocity

        return batt_power_exert


    def _add_power_to_df(self, rdf):

        batt_power_exert = self._calculate_batt_power_exert(rdf)

        new_df = rdf.assign(
            battery_power_exerted = batt_power_exert
            )

        return new_df


    def _calculate_energy_demand(self, power, delta_x, veloc):

        delta_t = delta_x / veloc

        energy = np.sum(power * delta_t)

        return energy


    def energy_from_route(self):

        rdf = self.route_df

        power = rdf.battery_power_exerted.values

        # Calculate lengths of route segments
        delta_x = distance_array_from_linestrings(rdf)

        return self._calculate_energy_demand(power, delta_x, velocity)


    def distance_array_from_linestrings(self, rdf):
        # Calculate lengths of route segments
        delta_x = []
        for line in rdf.geometry.values:
            if hasattr(line, 'length'):
                delta_x.append(line.length)
            else:
                delta_x.append(0)

        return delta_x


