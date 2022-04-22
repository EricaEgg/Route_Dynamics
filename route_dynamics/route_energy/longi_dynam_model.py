from ..route_elevation import base_df as re_base
from . import knn
from . import accel as ca

import numpy as np
import geopandas as gpd

class IllegalArgumentError(ValueError):
    """ """
    pass

class RouteTrajectory():
    """ Takes 2d route coordinates extracted from shapefile and
        combines the information with elevation to create a route
        trajectory dataframe.
        """

    def __init__(self,
        route_num,
        shp_filename,
        a_prof,
        stop_coords=None,
        signal_coords=None,
        mass_array=None,
        unloaded_bus_mass=12927,
        charging_power_max=None,
        a_pos=0.4,
        a_neg=-1.5
        ):

        self._initialize_instance_args(
            route_num,
            shp_filename,
            a_prof,
            stop_coords,
            signal_coords,
            mass_array,
            unloaded_bus_mass,
            charging_power_max,
            a_pos,
            a_neg
            )

        # Build Route DataFrame, starting with columns:
        #     - 'Z' (elevation)
        #     - 'geometry' (coordinates)
        #     - 'length' (cumulative distance)
        #     - 'grade' 
        #     - 'is_bus_stop'
        self.route_df = self.build_route_coordinate_df(
            shp_filename = shp_filename
            )

        self.route_df = self._add_dynamics_to_df(
            route_df=self.route_df,
            a_prof=a_prof,
            stop_coords=stop_coords,
            signal_coords=signal_coords
            )


    def _initialize_instance_args(self,
        route_num,
        shp_filename,
        a_prof,
        stop_coords,
        signal_coords,
        mass_array,
        unloaded_bus_mass,
        charging_power_max,
        a_pos,
        a_neg
        ):

        # default speed limit and acceleration constant
        self.a_neg = a_neg
        self.a_pos = a_pos
        self.a_prof = a_prof


        self.stop_coords = stop_coords
        self.signal_coords=signal_coords

        # Mass stuff
        self.mass_array = mass_array
        self.unloaded_bus_mass = unloaded_bus_mass

        # # Boolean check for instance argument 'mass_array'
        # self.mass_arg_is_list = (
        #     type(self.mass_array) is list
        #     or
        #     type(self.mass_array) is np.ndarray
        #     )
        # ####

        # Store chargeing ability as instance attribute
        self.charging_power_max = charging_power_max


    def _add_dynamics_to_df(self,
        route_df,
        a_prof,
        stop_coords,
        signal_coords
        ):

        # Try to determine bus stops from list of coordinates
        route_df = self._add_stops_to_df(stop_coords, signal_coords, route_df)


        # Add 'acceleration' column to route_df
        route_df = self._add_accelerations_to_df(
            route_df,
            a_prof
            )

        route_df = self._add_velocities_to_df(route_df)

        route_df = self._add_delta_times_to_df(route_df)

        # Add passenger mass column to route_df
        route_df = self._add_mass_to_df(route_df)

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
        shp_filename
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
        route_df = re_base.wrapper(shp_filename, 6, 6)

        return route_df


    def _add_stops_to_df(self, stop_coords, signal_coords, route_df):
        """ Find rows in route_df matching the stop_coordinates and
            mark as bus stop under new column.
            """

        self.stop_nn_indicies, self.stop_coord_nn = knn.find_knn(
        1,
        route_df.geometry.values,
        stop_coords
        )


        signal_nn_indicies, singal_coord_nn = knn.find_knn(
        1,
        route_df.geometry.values,
        signal_coords)

        route_df = route_df.assign(
        is_bus_stop = ([False] * len(route_df.index))
        )

        route_df = route_df.assign(
        is_signal = ([False] * len(route_df.index))
        )

        route_df = route_df.assign(
        is_stop = ([False] * len(route_df.index))
        )

        for i in self.stop_nn_indicies.ravel()[::3]:
            route_df.at[i, 'is_bus_stop'] = True
            route_df.at[i, 'is_stop'] = True
            
        for i in signal_nn_indicies.ravel()[::3]:
            route_df.at[i, 'is_stop'] = True
            route_df.at[i, 'is_signal'] = True

        # route_df.at[0, 'is_bus_stop'] = True
        # route_df.at[-1, 'is_bus_stop'] = True

        return route_df


    def _add_velocities_to_df(self, route_df):
        

        bus_speed_array = self.const_a_velocities

        route_df = route_df.assign(
            velocity=bus_speed_array
            )

        return route_df


    def _add_delta_times_to_df(self, route_df):
        """ Add delta_times for finite_difference calculation of acceleration """

        

        route_df = route_df.assign(delta_times = self.delta_times)
        route_df = route_df.assign(total_time = self.route_time)

        # if alg is 'finite_diff':
        #     delta_times = self._calculate_delta_times_on_linestring_distance(
        #         route_df)
        # elif alg is 'model':
        #     delta_times = np.append(
        #         0,
        #         np.diff(self.route_time)
        #         )

        # route_df = route_df.assign(
        #     delta_time=delta_times
        #     )

        return route_df


    # def _calculate_delta_times_on_linestring_distance(self,
    #     route_df,
    #     alg='finite_diff',
    #     ):

    #     back_diff_delta_x = np.full(len(route_df), 1.8288)

    #     try:
    #         velocities = route_df.velocity.values
    #     except AttributeError:
    #         print("Does 'route_df' have 'velocity' column? ")

    #     if alg is 'finite_diff':
    #         # Calcule average velocities along segment but backward difference
    #         segment_avg_velocities = (
    #             velocities
    #             +
    #             np.append(0,velocities[:-1])
    #             )/2

    #         self.delta_times = back_diff_delta_x * segment_avg_velocities

    #     else:
    #         raise IllegalArgumentError("time calculation only equiped to "
    #             "implement finite difference.")


    #     self.time_on_route = np.append(
    #         0,
    #         np.cumsum(self.delta_times[1:])
    #         )

    #     return self.delta_times


    def _add_accelerations_to_df(self, route_df, a_prof):
        """ For now just adds a acceleration velocity as a placeholder.
            """
        # print(route_df.head())
        accelerations = self._calculate_acceleration(route_df, a_prof)

        #Assign acceleration values to new row in route DataFrame.
        route_df = route_df.assign(
            acceleration=accelerations
            )

        return route_df


    def _calculate_acceleration(self,
        route_df,
        a_prof,
        a_pos=None,
        a_neg=None
        
        ):

        if a_neg is None: a_neg=self.a_neg
        if a_pos is None: a_pos=self.a_pos

        (
            accelerations,
            self.const_a_velocities,
            self.x_ls,
            self.x_ns,
            self.route_time,
            self.delta_times
            ) = ca.accel_dynamics(
            route_df,
            a_prof,
            a_pos,
            a_neg
            )

        return accelerations


    def _add_mass_to_df(self,
        route_df,
        ):
        """ Compute number of passengers along the route.

            Eventually this will use Ryan's ridership module, which
            determines the ridership at each bus stop.
            """
        # if self.mass_arg_is_list:

        #     lengths_equiv = len(self.mass_array)==len(
        #         self.stop_coords)
            # Does mass array check out for calculation?
            # mass_array_correct_length = (
            #     lengths_equiv and self.mass_arg_is_list
            #     )

        full_mass_column = self.calculate_mass()

        # full_mass_column = np.zeros(len(self.route_df.index))

        # else: # Add default mass to every row
        #     full_mass_column = self.unloaded_bus_mass*np.ones(
        #         len(route_df.index))


        route_df = route_df.assign(
            mass = full_mass_column
            )

        return route_df


    def calculate_mass(self
        ):
        """ Take mass array that is length of bus stop array and store
            as df column with interpolated values in between stops
            (value from last stop). If no mass array was input as class
            arg, then default bus mass is stored in every df row.
            """


        # if alg=='list_per_stop' and len_check:

        # if not hasattr(self, 'stop_nn_indicies'):
        #     raise AttributeError('Cant calculate from list')


        # Initialize array of Nan's for mass column of route_df
        full_mass_column = np.zeros(len(self.route_df.index))
        full_mass_column[:] = np.nan

        order = np.sort(self.stop_nn_indicies.ravel())


        for i in range(len(self.mass_array)):  
            full_mass_column[order[i]] = self.mass_array[i]
        
        
        # Set initial and value to unloaded bus mass.
        full_mass_column[0] = self.unloaded_bus_mass
        full_mass_column[-1] = self.unloaded_bus_mass

        # Iterate through the half constructed rdf mass column
        # ('full_mass_column') and fill in sapce between stops with previous value
        # for i in range(len(full_mass_column)-1):
        #     j = 1
        #     try:
        #         while np.isnan(full_mass_column[i+j]):
        #             full_mass_column[i+j] = full_mass_column[i]
        #             # print(full_mass_column[i+j] )
        #             j+=1
        #     except: IndexError

        for i in range(len(full_mass_column)-1):
            if np.isnan(full_mass_column[i]):
                full_mass_column[i] = full_mass_column[i-1]
            else:
                continue 

        # if np.any(full_mass_column < self.unloaded_bus_mass):
        #     raise IllegalArgumentError("Class arg 'unloaded_bus_mass' "
        #         "is heavier than values in arg 'mass_array'")

        # elif alg=='list_per_stop' and (
        #     self.mass_arg_is_list and not len_check
        #     ):
        #     raise IllegalArgumentError(
        #         "'stop_coords' and 'mass_array' must be same length"
        #         )

        # else:
        #     raise IllegalArgumentError(
        #         "Algorithm for mass calculation must be 'list_per_stop'"
        #         )


        return full_mass_column


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


    def calculate_forces(self, route_df):
        """ Requires GeoDataFrame input with mass column """  

        vels = route_df.velocity.values
        acce = route_df.acceleration.values
        grad = route_df.grade.values
        grad_angle = np.arctan(grad)


        # Physical parameters
        gravi_accel = 9.81
        air_density = 1.225 # air density in kg/m3; consant for now,
            # eventaully input from weather API
        v_wind = 0.0 # wind speed in km per hour; figure out component,
            # and also will come from weather API
        fric_coeff = 0.01

        # List of Bus Parameters for 40 foot bus
        # if self.mass_array is None:
        #     loaded_bus_mass = self.unloaded_bus_mass # Mass of bus in kg
        # else:
        loaded_bus_mass = route_df.mass.values

        width = 2.6 # in m
        height = 3.3 # in m
        bus_front_area = width * height
        drag_coeff = 0.34 # drag coefficient estimate from paper (???)
        rw = 0.28575 # radius of wheel in m


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


    def _calculate_batt_power_exert(self, route_df):

        f_resist = (
            route_df.grav_force.values
            +
            route_df.roll_fric.values
            +
            route_df.aero_drag.values
            )

        f_traction = route_df.inertia.values - f_resist

        velocity = route_df.velocity.values

        # calculate raw power before capping charging ability of bus
        batt_power_exert = f_traction * velocity
        self.raw_batt_power_exert = np.copy(batt_power_exert)

        for i in range(len(batt_power_exert)):
            if batt_power_exert[i] < -self.charging_power_max:
                batt_power_exert[i] = -self.charging_power_max

            elif batt_power_exert[i] > self.charging_power_max:
                batt_power_exert[i] = self.charging_power_max

        return batt_power_exert


    def _add_power_to_df(self, route_df):

        batt_power_exert = self._calculate_batt_power_exert(route_df)


        new_df = route_df.assign(
            power_output = batt_power_exert
            )

        return new_df


    def energy_from_route(self, route_df):

        route_df = self.route_df

        delta_t = route_df.delta_times.values[1:]

        power = route_df.power_output.values[1:]

        energy = np.sum(power/1000 * delta_t/3600)

        return energy
