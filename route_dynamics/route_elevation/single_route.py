import base


def route_analysis_all(route_num, shapefile, rasterfile):
    """
       input the number of route, then output an interactive map of the
       route, elevation and road grade profiles, and metrics calculated
       for the route.

    Also will save the route as shapefile named 'route_shp'.

    Parameters
    ----------
    route_num: Desired route number (integer)
    shapefile: route geospatial data (.shp file)
    rasterfile: elevation data file (.tif)

    Returns
    -------
    map_display: interactive map for desired route
    route_plot: elevation and grade profiles for desired route
    display_metrics: results of metrics calculations
    """

    # Load shape file into GeoDataFrame
    # with extra column ROUTE_NUM = (last argument)
    route_shp = base.read_shape(shapefile, route_num)

    # Use 2D coordinates and elevation rasterfile to generate
    # elevations and elevation gradiant at each point.
    (
        elevation,
        elevation_gradient,
        route_cum_distance,
        distance
        ) = base.gradient(route_shp, rasterfile)

    # Build dataframe of 2D coordinates making up bus route
    linestring_route_df = base.extract_point_df(route_shp)

    # From dataframe containing route coordinates and list of gradients
    # at each point on route, combine into route GeoDataFrame with rows
    # corresponsing to points on route and columns;
    #   'gradient'
    #       - value of gratent per rout point
    #   'geometry'
    #       - contains shapely.Line objects conneting each point on
    # route
    gdf_route = base.make_multi_lines(linestring_route_df, elevation_gradient)

    # Use package folium to create an interactive map for the desired
    # route.
    map_display = base.route_map(gdf_route)

    route_plot = base.profile_plot(
        elevation,
        elevation_gradient,
        route_cum_distance,
        route_num,
        )

    display_metrics, _ = base.route_metrics(elevation, elevation_gradient, route_cum_distance, distance, route_num)

    return map_display, route_plot, display_metrics


def route_analysis_profile(route_num, shapefile, rasterfile):
    """
       input the number of route, then output elevation and road grade profiles.
    Also will save the route as shapefile named 'route_shp'.

    Parameters
    ----------
    route_num: desired route number (integer)
    shapefile: route geospatial data (.shp file)
    rasterfile: elevation data file (.tif)

    Returns
    -------
    route_plot: elevation and grade profiles for desired route
    """
    route_shp = base.read_shape(shapefile, route_num)

    linestring_route_df = base.extract_point_df(route_shp)

    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

    gdf_route = base.make_multi_lines( linestring_route_df, elevation_gradient)

    route_plot = base.profile_plot(elevation, elevation_gradient, route_cum_distance, route_num)

    return route_plot


def route_analysis_map(route_num, shapefile, rasterfile):
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

def route_analysis_df(route_num, shapefile, rasterfile):
    """
       input the number of route, then output a GeoDataFrame with gradient and geometry
    information of that route, and elevation_gradient for each line segment.
    Also will save the route as shapefile named 'route_shp'.

    Parameters
    ----------
    route_num: desired route number (integer)
    shapefile: route geospatial data (.shp file)
    rasterfile: elevation data file (.tif)

    Returns
    -------
    gdf_route: geodataframe with columns ['gradient', 'geometry']

    """
    route_shp = base.read_shape(shapefile, route_num)

    linestring_route_df = base.extract_point_df(route_shp)

    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

    gdf_route = base.make_multi_lines( linestring_route_df, elevation_gradient)

    return gdf_route


def route_analysis_metrics(route_num, shapefile, rasterfile):
    """
       input the number of route, then output the metrics calculated for that route.
    Also will save the route as shapefile named 'route_shp'.

    Parameters
    ----------
    route_num: Desired route number (integer)
    shapefile: route geospatial data (.shp file)
    rasterfile: elevation data file (.tif)

    Returns
    -------
    display_metrics: results of metrics calculations
    """
    route_shp = base.read_shape(shapefile, route_num)

    linestring_route_df = base.extract_point_df(route_shp)

    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

    display_metrics, _ = base.route_metrics(elevation, elevation_gradient, route_cum_distance, distance, route_num)

    return display_metrics

