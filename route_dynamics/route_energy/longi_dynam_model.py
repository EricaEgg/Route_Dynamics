""" Implementation of the Longitudinal Dynamics Model for work done by
    the bus engine along route.

    From:
        Asamer J, Graser A, Heilmann B, Ruthmair M. Sensitivity
        analysis for energy demand estimation of electric vehicles.
        Transportation Research Part D: Transport and Environment.
        2016 Jul 1;46:182-99.

    """

# from ..route_elevation import single_route as rsr
from ..route_elevation import base as re_base

import numpy as np
import geopandas as gpd


class IllegalArgumentError(ValueError):
    """ """
    pass


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
        bus_speed_model='stopped_at_stops__15mph_between',
        stop_coords=None,
        ):
        """ Build DataFrame with bus trajectory and shapely connections
            for plotting. This object is mostly a wrapper object to
            build and return the Route DataFrame, but will later
            contain plotting methods as well.


            Args:

                route_num: needs to be one that Erica made work.

                bus_speed_model:
                    Right now the argument 'bus_speed_model' is
                    set to 'test' by default, which causes the speed to
                    be set at a constant velocity of 6.7056 [m/s],
                    which is equal to 15 mph. Later this will accept
                    arguments like 'parabolic_between_stops' or maybe
                    even something smarter that includes trtaffic.

            Methods:

                ...

            """

        # Store algorithm name for future reference.
        self.bus_speed_model = bus_speed_model

        # Build Route DataFrame, starting with columns:
        #     - 'elevation'
        #     - 'cum_distance'
        #     - 'is_bus_stop
        self.route_df = self.build_route_coordinate_df(
            route_num = route_num,
            shp_filename = shp_filename,
            elv_raster_filename = elv_raster_filename,
            )

        self.route_df = self._add_dynamics_to_df(
            route_df=route_df,
            stop_coords=stop_coords,
            bus_speed_model=self.bus_speed_model,
            )


    def _add_dynamics_to_df(self,
        route_df,
        stop_coords,
        bus_speed_model,
        ):

        # Try to determine bus stops from list of coordinates
        route_df = self._add_stops_to_df(stop_coords, route_df)

        # Add 'velocity' column to route_df
        # This will also involve calulating the velocity.
        route_df = self._add_velocities_to_df(
            route_df,
            bus_speed_model=bus_speed_model,
            )

        route_df = self._add_delta_times_to_df(route_df)

        # Add 'acceleration' column to route_df
        route_df = self._add_accelerations_to_df(route_df)

        # Add passenger mass column to route_df
        route_df = self._add_passenger_mass_to_df(route_df)

        # Add force columns to route_df:
        #     - 'grav_force' : gravitation force determined by road grade
        #     - 'roll_fric' : rolling friction
        #     - 'aero_drag' : areodynamic drag
        #     - 'inertia' : inertial force, F = ma. Changes with passenger load
        #                   on bus.
        route_df = self._add_forces_to_df(route_df)

        # Add column to route_df containing instantaneous power experted by
        # bus at each point along route.
        route_df = self._add_power_to_df(route_df)

        return route_df


    def build_route_coordinate_df(self,
        route_num,
        shp_filename,
        elv_raster_filename,
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
        route_shp = re_base.read_shape(shp_filename, route_num)

        route_2Dcoord_df = re_base.extract_point_df(route_shp)

        (
            elevation,
            elevation_gradient,
            route_cum_distance,
            distance
            ) = re_base.gradient(route_shp, elv_raster_filename)

        route_df = re_base.make_multi_lines(
            route_2Dcoord_df,
            elevation_gradient
            )

        route_df = self._add_elevation_to_df(elevation, route_df)

        route_df = self._add_cum_dist_to_df(route_cum_distance, route_df)

        return route_df


    def _add_stops_to_df(self, stop_coords, route_df):
        """ Find rows in route_df matching the stop_coordinates and
            mark as bus stop under new column.
            """

        # By default, 'stop_coords' is set to 'None', if this is true,
        # then 10 bus stops will be assigned randomly
        if stop_coords is 'random':
            # Randomly select certain route coordinates to be marked as
            # a stop with 5% probability.
            # Fix seed for reproducability
            np.random.seed(5615423)
            # Return binary array with value 'True' 5% of time
            is_stop__truth_array = (
                np.random.random(len(route_df.index)) < .05
                )

            rdf = route_df.assign(
                is_bus_stop = is_stop__truth_array
                )

        elif stop_coords is None:
            # Mark no stops
            rdf = route_df.assign(
                is_bus_stop = ([False] * len(route_df.index))
                )

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


    def _add_velocities_to_df(self, route_df, bus_speed_model):
        """ For now just adds a constant velocity as a placeholder.
            """

        lazy_choise_for_speed = 6.7056  # 6.7056 m/s (= 15 mph)

        # 'test' algorithm set by default for now.
        if bus_speed_model == 'constant_15mph':
            # Assign constant velocity
            bus_speed_array = (
                lazy_choise_for_speed * np.ones(len(route_df.index))
                )

        elif bus_speed_model == 'stopped_at_stops__15mph_between':
            # Really I want something here to use the stop array to calcularte bus speed.
            # Step !: Calculate distance to next stop, which should determine the strajectory (speed at point)
                # can use difference of 'cum_dist's
            # 2) Assign trajectory as function of distance
            # 3) plug in each route point between stops intor trajectory function.
            # ... This is all UNDER CONSTRUCTION ...

            # Right now, this will just make stop points have zero velocity.
            zero_if_stop__one_if_not = (
                np.logical_not(route_df.is_bus_stop.values)*1
                )

            # Mark endpoints of route as well
            zero_if_stop_start_end__one_if_not = zero_if_stop__one_if_not
            zero_if_stop_start_end__one_if_not[0] = 0
            zero_if_stop_start_end__one_if_not[-1] = 0

            # if not stop, set velocity to 15 mph
            bus_speed_array = zero_if_stop__one_if_not * lazy_choise_for_speed


        rdf = route_df.assign(
            velocity=bus_speed_array
            )

        return rdf


    def _add_delta_times_to_df(self, route_df):
        """ Add delta_times for finite_difference calculation of acceleration """

        delta_times = self._calculate_delta_times_on_linestring_distance(route_df)

        rdf = route_df.assign(
            delta_time=delta_times
            )

        return rdf


    def _calculate_delta_times_on_linestring_distance(self, route_df):

        back_diff_delta_x = self.distance_array_from_linestrings(route_df)

        try:
            velocities = route_df.velocity.values
        except AttributeError:
            print("Does 'route_df' have 'velocity' column? ")

        # Calcule average velocities along segment but backward difference
        segment_avg_velocities = (
            velocities
            +
            np.append(0,velocities[:-1])
            )/2

        delta_times = back_diff_delta_x * segment_avg_velocities

        return delta_times


    def _add_accelerations_to_df(self, route_df, alg='finite_diff'):
        """ For now just adds a acceleration velocity as a placeholder.
            """

        accelerations = self._calculate_acceleration(route_df, alg)

        #Assign acceleration values to new row in route DataFrame.
        rdf = route_df.assign(
            acceleration=accelerations
            )

        return rdf


    def _calculate_acceleration(self, route_df, alg='finite_diff'):
        # Calculate acceleration
        if alg=='finite_diff':
            # Use finite difference of velocities to calculate accelerations
            velocity_array = route_df.velocity.values

            delta_distance_array = self.distance_array_from_linestrings(route_df)

            # assert (np.shape(np.diff(velocity_array))==np.shape(delta_distance_array)), (
            #     "np.shape(np.diff(velocity_array) = {}\n"
            #     "np.shape(delta_distance_array) = {}\n".format(
            #         np.shape(np.diff(velocity_array)),
            #         np.shape(delta_distance_array)
            #         )
            #     )

            # Calculate acceleraetion by central difference

            zero_in_a_list = np.array([0])

            back_diff_velocity_array = np.append(
                zero_in_a_list,
                np.diff(velocity_array)
                )

            # Assign backward diff velocities as instance attribute
            self.delta_v = back_diff_velocity_array

            # forward_diff_velocity_array = np.append(
            #     np.diff(velocity_array),
            #     zero_in_a_list
            #     )

            # central_diff_velocity_array = (
            #     back_diff_velocity_array
            #     +
            #     forward_diff_velocity_array
            #     )/2.

            # But average acceleration cooresponding to the linestring
            # distance will be the backward difference in velovity...
            # divided by time and not distance...

            dt = route_df.delta_time.values

            accelerations = back_diff_velocity_array / dt


        else:
            raise IllegalArgumentError((
                "'alg' keywarg must be implemented algorithm. "
                "Currently supported are; \n"
                "    - 'finite_diff' : calculates finite difference in"
                " velocities and distances and takes the ratio.\n"
                "and nothing else... maybe one day it will have an analytic"
                " option."
                ))

        return accelerations


    def _add_passenger_mass_to_df(self,
        route_df,
        route_number=None,
        in_or_out=None,
        segment=None,
        ):
        """ Compute number of passengers along the route.

            Eventually this will use Ryan's ridership module, which
            determines the ridership at each bus stop.
            """

        passenger_mass_per_stop = self.calculate_passenger_mass(
            route_number,
            in_or_out,
            segment,
            )

        # Placeholder for now.
        route_df = route_df.assign(
            passenger_mass = np.zeros(len(route_df.index))
            )

        return route_df


    def calculate_passenger_mass(self, route_number, in_or_out, segment):
        """ Load Ryan's module """
        return None


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
        """ Requires GeoDataFrame input with mass column """

        vels = rdf.velocity.values
        acce = rdf.acceleration.values
        grad = rdf.gradient.values
        grad_angle = np.arctan(grad)
        passenger_mass = rdf.passenger_mass.values

        # Physical parameters
        gravi_accel = 9.81
        air_density = 1.225 # air density in kg/m3; consant for now,
            # eventaully input from weather API
        v_wind = 0.0 # wind speed in km per hour; figure out component,
            # and also will come from weather API
        fric_coeff = 0.01

        # List of Bus Parameters for 40 foot bus
        bus_mass = 12927 # Mass of bus in kg
        width = 2.6 # in m
        height = 3.3 # in m
        bus_front_area = width * height
        drag_coeff = 0.34 # drag coefficient estimate from paper (???)
        rw = 0.28575 # radius of wheel in m

        # Total bus mass along route is equal to the bus mass plus
        # passenger load
        loaded_bus_mass = passenger_mass + bus_mass

        # Calculate the gravitational force
        grav_force = -(
            loaded_bus_mass * gravi_accel * np.sin(grad_angle)
            )

        # Calculate the rolling friction
        roll_fric = -(
            fric_coeff * loaded_bus_mass * gravi_accel * np.cos(grad_angle)
            )

        # Calculate the aerodynamic drag
        aero_drag = -(
            drag_coeff
            *
            bus_front_area
            *
            (air_density/2)
            *
            (vels-v_wind)
            )

        # Calculate the inertial force
        inertia = loaded_bus_mass * acce

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
            power_output = batt_power_exert
            )

        return new_df


    def energy_from_route(self):

        rdf = self.route_df

        delta_t = rdf.delta_time.values[1:]

        power = rdf.power_output.values[1:]

        energy = np.sum(power * delta_t)

        return energy


    def distance_array_from_linestrings(self, rdf):
        # Calculate lengths of route segments
        delta_x = []
        for line in rdf.geometry.values:
            if hasattr(line, 'length'):
                delta_x.append(line.length)
            else:
                delta_x.append(0)

        return delta_x


