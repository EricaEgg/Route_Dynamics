from ..route_elevation import base_df as re_base
from . import knn
from . import accel as ca

import numpy as np
import geopandas as gpd

def add_dynamics_to_df(route_df,
    stop_coords, 
    a_prof,
    a_neg,
    v_lim
    ):

    # Try to determine bus stops from list of coordinates
    route_df = add_stops_to_df(stop_coords, route_df)


    # Add 'acceleration' column to route_df
    route_df = add_accelerations_to_df(
        route_df,
        a_prof,
        a_neg,
        v_lim
        )

    route_df = add_velocities_to_df(
        route_df,
        a_prof,
        a_neg,
        v_lim
        )

    route_df = add_delta_times_to_df(route_df, 'model', a_prof, a_neg, v_lim)

    # Add passenger mass column to route_df
    route_df = add_mass_to_df(route_df)

    # Add force columns to route_df:
    #     - 'grav_force' : gravitation force determined by road grade
    #     - 'roll_fric' : rolling friction
    #     - 'aero_drag' : areodynamic drag
    #     - 'inertia' : inertial force, F = ma. Changes with passenger load
    #                   on bus.
    route_df = add_forces_to_df(route_df)

    # Add column to route_df containing instantaneous power experted by
    # bus at each point along route.
    route_df = add_power_to_df(route_df)

    return route_df

def build_route_coordinate_df(shp_filename
    ):

    # Build the df of 2D route coordinates and
    route_df = re_base.create_gdf(shp_filename, 6)

    return route_df

def add_stops_to_df(stop_coords, route_df):
    """ Find rows in route_df matching the stop_coordinates and
        mark as bus stop under new column.
        """

        # Calculate indicies of 'stop_coords' that match bus_stops
    stop_nn_indicies, stop_coord_nn = knn.find_knn(
        1,
        route_df.geometry.values,
        stop_coords
        )
    # the 'jth' element of stop_nn_indicies also selects the

    route_df = route_df.assign(
        is_bus_stop = ([False] * len(route_df.index))
        )

    for i in stop_nn_indicies.ravel():
        route_df.at[i, 'is_bus_stop'] = True


    return route_df

def add_velocities_to_df(route_df, a_prof, a_neg, v_lim):
        

    (accelerations,
    const_a_velocities,
    x_ls,
    x_ns,
    route_time
    ) = ca.accel_dynamics(
    route_df,
    a_prof,
    a_neg,
    v_lim
    )

    rdf = route_df.assign(
        velocity=const_a_velocities
        )

    return rdf

def add_delta_times_to_df(route_df, alg, a_prof, a_neg, v_lim):
    """ Add delta_times for finite_difference calculation of acceleration """

    (accelerations,
    const_a_velocities,
    x_ls,
    x_ns,
    route_time
    ) = ca.accel_dynamics(
    route_df,
    a_prof,
    a_neg,
    v_lim
    )


    if alg == 'finite_diff':
        delta_times = calculate_delta_times_on_linestring_distance(
            route_df)
    elif alg == 'model':
        delta_times = np.append(
            0,
            np.diff(route_time)
            )

    rdf = route_df.assign(
        delta_time=delta_times
        )

    return rdf

def calculate_delta_times_on_linestring_distance(route_df,
    alg='finite_diff',
    ):

    back_diff_delta_x = np.full(len(route_df), 1.8288)

    try:
        velocities = route_df.velocity.values
    except AttributeError:
        print("Does 'route_df' have 'velocity' column? ")

    if alg == 'finite_diff':
        # Calcule average velocities along segment but backward difference
        segment_avg_velocities = (
            velocities
            +
            np.append(0,velocities[:-1])
            )/2

        delta_times = back_diff_delta_x * segment_avg_velocities

    else:
        raise IllegalArgumentError("time calculation only equiped to "
            "implement finite difference.")


    time_on_route = np.append(
        0,
        np.cumsum(delta_times[1:])
        )

    return delta_times

def add_accelerations_to_df(route_df, a_prof, a_neg, v_lim):
    """ For now just adds a acceleration velocity as a placeholder.
        """
    # print(route_df.head())
    accelerations = calculate_acceleration(route_df, a_prof, a_neg, v_lim)

    #Assign acceleration values to new row in route DataFrame.
    rdf = route_df.assign(
        acceleration=accelerations
        )

    return rdf

def calculate_acceleration(route_df,
	a_prof,
    a_neg,
    v_lim
    ):
    
    (
        accelerations,
        const_a_velocities,
        x_ls,
        x_ns,
        route_time
        ) = ca.accel_dynamics(
        route_df,
        a_prof,
        a_neg,
        v_lim
        )

    return accelerations

def add_mass_to_df(route_df,
    ):
    """ Compute number of passengers along the route.

        Eventually this will use Ryan's ridership module, which
        determines the ridership at each bus stop.
        """
    if mass_arg_is_list:

        lengths_equiv = len(mass_array)==len(
            stop_coords)
        # Does mass array check out for calculation?
        mass_array_correct_length = (
            lengths_equiv and mass_arg_is_list
            )

        full_mass_column = calculate_mass(
            alg='list_per_stop',
            len_check=mass_array_correct_length
            )

    else: # Add default mass to every row
        full_mass_column = unloaded_bus_mass*np.ones(
            len(route_df.index))


    route_df = route_df.assign(
        mass = full_mass_column
        )

    return route_df

def calculate_mass(alg='list_per_stop',
    len_check=None,
    ):
    """ Take mass array that is length of bus stop array and store
        as df column with interpolated values in between stops
        (value from last stop). If no mass array was input as class
        arg, then default bus mass is stored in every df row.
        """


    if alg=='list_per_stop' and len_check:


        # Initialize array of Nan's for mass column of rdf
        full_mass_column = np.zeros(len(route_df.index))
        full_mass_column[:] = np.nan

        # Iterate through the length of the given mass_array
        # (already determined equal length to 'stop_coords').
        for i in range(len(mass_array)):
            # Set values of mass at bus_stops
            full_mass_column[
                stop_nn_indicies[i]
                ] = mass_array[i]

        # Set initial and value to unloaded bus mass.
        full_mass_column[0] = unloaded_bus_mass
        full_mass_column[-1] = unloaded_bus_mass

        # Iterate through the half constructed rdf mass column
        # ('full_mass_column') and fill in sapce between stops with previous value
        for i in range(len(full_mass_column)-1):
            j = 1
            try:
                while np.isnan(full_mass_column[i+j]):
                    full_mass_column[i+j] = full_mass_column[i]
                    # print(full_mass_column[i+j] )
                    j+=1
            except: IndexError

        if np.any(full_mass_column < unloaded_bus_mass):
            raise IllegalArgumentError("Class arg 'unloaded_bus_mass' "
                "is heavier than values in arg 'mass_array'")

    elif alg=='list_per_stop' and (
        mass_arg_is_list and not len_check
        ):
        raise IllegalArgumentError(
            "'stop_coords' and 'mass_array' must be same length"
            )

    else:
        raise IllegalArgumentError(
            "Algorithm for mass calculation must be 'list_per_stop'"
            )


    return full_mass_column

def add_forces_to_df(route_df):
    """ Calculate forces on bus relevant to the Longitudinate
        dynamics model.
        """

    (
        grav_force,
        roll_fric,
        aero_drag,
        inertia
        ) = calculate_forces(route_df)

    route_df = route_df.assign(
        grav_force = grav_force,
        roll_fric = roll_fric,
        aero_drag = aero_drag,
        inertia = inertia,
        )

    return route_df

def calculate_forces(rdf):
    """ Requires GeoDataFrame input with mass column """  

    vels = rdf.velocity.values
    acce = rdf.acceleration.values
    grad = rt_df.grade.values
    grad_angle = np.arctan(grad)


    # Physical parameters
    gravi_accel = 9.81
    air_density = 1.225 # air density in kg/m3; consant for now,
        # eventaully input from weather API
    v_wind = 0.0 # wind speed in km per hour; figure out component,
        # and also will come from weather API
    fric_coeff = 0.01

    # List of Bus Parameters for 40 foot bus
    if mass_array is None:
        loaded_bus_mass = unloaded_bus_mass # Mass of bus in kg
    else:
        loaded_bus_mass = rdf.mass.values

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

def calculate_batt_power_exert(rdf):

    f_resist = (
        rdf.grav_force.values
        +
        rdf.roll_fric.values
        +
        rdf.aero_drag.values
        )

    f_traction = rdf.inertia.values - f_resist

    velocity = rdf.velocity.values

    # calculate raw power before capping charging ability of bus
    batt_power_exert = f_traction * velocity
    raw_batt_power_exert = np.copy(batt_power_exert)

    for i in range(len(batt_power_exert)):
        if batt_power_exert[i] < -charging_power_max:
            batt_power_exert[i] = -charging_power_max

    return batt_power_exert

def add_power_to_df(rdf):

    batt_power_exert = calculate_batt_power_exert(rdf)

    new_df = rdf.assign(
        power_output = batt_power_exert
        )

    return new_df


def energy_from_route(route_df):

    rdf = route_df

    delta_t = rdf.delta_time.values[1:]

    power = rdf.power_output.values[1:]

    energy = np.sum(power * delta_t)

    return energy

def dynamics(route_num,
    shp_filename,
    stop_coords=None,
    mass_array=None,
    unloaded_bus_mass=12927,
    charging_power_max=0., # should be kW
    a_neg=-0.4,
    v_lim=15.0,
    a_prof='../data/acceleration.csv'
    ):

    route_df = build_route_coordinate_df(
        shp_filename = shp_filename
        )

    route_df = add_dynamics_to_df(
        route_df=route_df,
        stop_coords=stop_coords,
        a_prof=a_prof,
        a_neg=a_neg,
        v_lim=v_lim
        )

    return route_df 



