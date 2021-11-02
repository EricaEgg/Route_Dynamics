import matplotlib.pyplot as plt

import route_dynamics.route_elevation.base_df as base
def profile_x(y, route_cum_distance, route_num):
    """
        Creates load vs. distance profile.
        Parameters
        ----------
        y: Dependent variable of profile (i.e elevation, grade, load, etc)
        route_cum_distance: the total route distance at each point along
            the route [m]
        route_num: route number (integer)
        Returns
        -------
        Load vs. distance 
        """

    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    ax.plot(route_cum_distance/1000, y/1000, linewidth=4)
    ax.set_xlabel('Distance (km)', fontsize=20)
    ax.set_ylabel('Load (kW)', fontsize=20)
    ax.tick_params(labelsize=14)
    ax.grid(axis='y')

    fig.suptitle(
        'Load Profile for Route {}'.format(route_num),
        fontsize=24,
        y=1,
        )

    plt.savefig('profile_x_{}.png'.format(route_num), dpi=300)

    return 


def profile_t(y, time, route_num):
    """
        Creates load vs. time profile.
        Parameters
        ----------
        y: Dependent variable of profile (i.e elevation, grade, load, etc)
        time: route time
        route_num: route number (integer)
        Returns
        -------
        Load vs. time 
        """

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(time, y, color='b', linewidth=4)
    ax.set_ylabel('Load (kW)', color='b')
    ax.tick_params('y', colors='b')
    ax.grid()

    fig.suptitle(
        'Load Profile for Route {}'.format(route_num),
        fontsize=20,
        y=0.95,
        )

    return 

def elev(elevation, route_cum_distance, route_num):

	"""
		Created elevation vs. distance profile.

		Parameters:
		route_cum_distance: the total route distance at each point along
            the route [m]
        elevation: elevation values
        route_num: route number (integer)

    """
	fig, ax = plt.subplots(figsize=(12, 5), dpi=300)

	ax.plot(route_cum_distance/5280, elevation, linewidth=4)
	ax.set_xlabel('Distance (miles)', fontsize=20)
	ax.set_ylabel('Elevation (ft)', fontsize=20)
	ax.tick_params(labelsize=14)

	fig.suptitle(
        'Elevation Profile for Route {}'.format(route_num),
        fontsize=24,
        y=1,
        )


def x_elev(y, route_cum_distance, elevation, route_num):

    """
        Creates load vs. distance profile and elevation vs. distance profile.

        Parameters:
        -----------
        y: Dependent variable of profile (i.e elevation, grade, load, etc)
        route_cum_distance: the total route distance at each point along
            the route [m]
        route_num: route number (integer)
        Returns
        -------
        Load vs. distance with elevation overlay
    """

    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)

    ax.fill_between(route_cum_distance/1000, elevation, color='#BDBDBD')
    ax1 = ax.twinx()

    ax1.plot(route_cum_distance/1000, y/1000, linewidth=4)
    ax.set_xlabel('Distance (km)', fontsize=20)
    ax.set_ylabel('Elevation (m)', fontsize=20)
    ax1.set_ylabel('Load (kW)', fontsize=20)
    ax.tick_params(labelsize=14)
    ax.grid(axis='y')

    fig.suptitle(
        'Load Profile for Route {}'.format(route_num),
        fontsize=24,
        y=1,
        )

    plt.savefig('x_elev_{}.png'.format(route_num), dpi=300)

    return 


def diag_plot(inst, style='plot', title=None):
    """
        Creates series of plots (Power vs time, acceleration vs time, veloctiy vs time, distance vs time, 
        power vs distance, accleration vs distance, velocity vs distance, time vs distance).
        Parameters
        ----------
        inst: output from longi_dynam_model
        style: default = 'plot'
        title: default = None
        
        """
    
    widths=[1,1]
    heights=[2.5,0.75,0.75,0.75]
    
    fig, axes = plt.subplots(
        4,2,dpi=100, 
        figsize = (8,6),
        constrained_layout=True,
        gridspec_kw = dict(width_ratios=widths, height_ratios=heights),
        )
    
    if title is not None:
        fig.suptitle(title, fontsize=12)
        
    x = inst.route_df.cum_distance.values
    v = inst.route_df.velocity.values
    a = inst.route_df.acceleration.values
    t = inst.route_time
    p = inst.route_df.power_output.values
    p_raw = inst.raw_batt_power_exert

    
    axes[0,0].plot(t,p, label='battery power')
    axes[0,0].plot(t,p_raw, label='raw power')
    axes[0,0].legend()
    axes[0,0].set_xlabel('time')
    axes[0,0].set_ylabel('distance')
    
    axes[1,0].plot(t,a)
    axes[1,0].set_xlabel('time')
    axes[1,0].set_ylabel('acceleration')

    axes[2,0].plot(t,v)
    axes[2,0].set_xlabel('time')
    axes[2,0].set_ylabel('speed')

    axes[3,0].plot(t,x)
    axes[3,0].set_xlabel('time')
    axes[3,0].set_ylabel('distance')
    

    axes[0,1].plot(x,p, label='battery power')
    axes[0,1].plot(x,p_raw, label='raw power')
    axes[0,1].legend()
    axes[0,1].set_xlabel('time')
    axes[0,1].set_ylabel('distance')

    axes[1,1].plot(x,a)
    axes[1,1].set_xlabel('distance')
    axes[1,1].set_ylabel('acceleration')

    axes[2,1].plot(x,v)
    axes[2,1].set_xlabel('distance')
    axes[2,1].set_ylabel('speed')

    axes[3,1].plot(x,t)
    axes[3,1].set_ylabel('time')
    axes[3,1].set_xlabel('distance')

    
def route_map(route_num, shapefile, rasterfile):
    """
       input the number of route, then output an interactive map showing the route and road grade.
    Also will save the route as shapefile named 'route_shp'.

    Parameters
    ----------
    route_num: desired route number (integer)
    shapefile: route geospatial data (.shp file)
    rasterfile: elevation data file (.tif)

    Returns
    -------
    map_display: interactive map for desired route
    """
    route_shp = base.read_shape(shapefile, route_num)

    linestring_route_df = base.extract_point_df(route_shp)

    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

    gdf_route = base.make_multi_lines( linestring_route_df, elevation_gradient)

    map_display = base.route_map(gdf_route)

    return map_display

