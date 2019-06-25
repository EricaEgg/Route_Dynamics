import matplotlib.pyplot as plt

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

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(route_cum_distance, y, color='b', linewidth=4)
    ax.set_ylabel('Load (kW)', color='b')
    ax.tick_params('y', colors='b')
    ax.grid()

    fig.suptitle(
        'Load Profile for Route {}'.format(route_num),
        fontsize=20,
        y=0.95,
        )

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


def route_map(gdf_route):
    """
        Use package folium to create an interactive map for the desired route.
        Parameters
        ----------
        gdf_route: GeoDataFrame output from make_multi_lines()
        Returns
        -------
        route_map: interactive map that displays the desired route and road grade
        """

    UW_coords = [47.655548, -122.303200]

    # initialize figure of certain size at specific coordinates
    sized_figure = folium.Figure(height = 400)
    route_map = folium.Map(location = UW_coords, zoom_start = 12)
    min_grade = min(gdf_route['gradient'])
    max_grade = max(gdf_route['gradient'])
    route_json = gdf_route.to_json()

    # assign colormap of grade
    linear_map = cm.linear.Paired_06.scale(min_grade, max_grade )

    route_layer = folium.GeoJson(
        route_json, style_function = lambda feature: {
            'color': linear_map(feature['properties']['gradient']),
            'weight': 8
            }
        )
    route_layer.add_child
    route_map.add_child(linear_map)
    route_map.add_child(route_layer)
    route_map.add_to(sized_figure)
    return route_map

