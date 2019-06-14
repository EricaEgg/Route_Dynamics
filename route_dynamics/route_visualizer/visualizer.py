import matplotlib.pyplot as plt

def profile_x(y, route_cum_distance, route_num):
    """
        Creates elevation profile.
        Parameters
        ----------
        y: Dependent variable of profile (i.e elevation, grade, load, etc)
        route_cum_distance: the total route distance at each point along
            the route [m]
        route_num: route number (integer)
        Returns
        -------
        plt: Elevation vs. distance 
        """

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(route_cum_distance, y, color='b', linewidth=4)
    ax.set_ylabel('Elevation (meter)', color='b')
    ax.tick_params('y', colors='b')
    ax.grid()

    fig.suptitle(
        'Elevation Profile for Route {}'.format(route_num),
        fontsize=20,
        y=0.95,
        )

    return fig


def profile_t(y, time, route_num):
    """
        Creates elevation profile.
        Parameters
        ----------
        y: Dependent variable of profile (i.e elevation, grade, load, etc)
        time: route time
        route_num: route number (integer)
        Returns
        -------
        plt: Elevation vs. distance 
        """

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(route_cum_distance, elevation.T, color='b', linewidth=4)
    ax.set_ylabel('Elevation (meter)', color='b')
    ax.tick_params('y', colors='b')
    ax.grid()

    fig.suptitle(
        'Elevation Profile for Route {}'.format(route_num),
        fontsize=20,
        y=0.95,
        )

    return plt


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

