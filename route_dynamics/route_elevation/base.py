import numpy as np
import pandas as pd
import geopandas as gpd
import branca.colormap as cm
import folium
import rasterstats
import matplotlib.pyplot as plt

from folium.features import GeoJson
from shapely.geometry import mapping
from shapely.geometry import LineString
from shapely.geometry import Polygon
# from rasterio.mask import mask
from geopy.distance import geodesic


def read_shape(shapefile, route_num):
    """
        Reads shapefile and selects desired route.

        Parameters
        ----------
        shapefile: route geospatial data (.shp file)
        route_num: route number (integer)

        Returns
        -------
        route_shp: Load shape file into GeoDataFrame
            with extra column ROUTE_NUM = (last argument)
        """

    routes_shp = gpd.read_file(shapefile)
    route_shp = routes_shp[routes_shp['ROUTE_NUM'] == route_num]
    return route_shp


def extract_point_df(route_shp):
    """
        Extracts coordinates from route GeoDataFrame for all points
        along the route.

        Parameters
        ----------
        route_shp: GeoDataFrame for the selected route;
            output of read_shape().

        Returns
        -------
        linestring_route_df: DataFrame containing the coordinates for
            every point along the route.
        """

    # list shapely geometries intrinsic to a GeoDataFrame,
    # and store values only in nd.array
    route_geometry = route_shp.geometry.values

    #HJG: I think this makes a copy? not sure why it's needed
    route_geometry = [mapping(route_geometry[0])]

    # Return route coordinates in seperate pd.DataFrame.
    # Coordinates are first row with name 'coordinates'
    coordinates_route = route_geometry[0]['coordinates']
    linestring_route = []
    for i in range(len(coordinates_route)):
        linestring_route.append(coordinates_route[i][:2])
        linestring_route_df = pd.DataFrame()
        linestring_route_df['coordinates'] = linestring_route
    return linestring_route_df


def distance_measure(route_shp):
    """
        Calculates the distance between points along the route and
        calculates the cumulative distance. ASSUMES geodesic distances
        connecting each point

        Parameters
        ----------
        route_shp: GeoDataFrame for the selected route;
        output of read_shape().

        Returns
        -------
        distance: list containing the distance between each point.
         In units = [meters].
        cum_distance: array of the total route distance at each point
        along the route (e.g. the first point will have a distance
        of 0, and the last point will equal the total route
        distance). In units = [meters]
        """

    # Convert GeoDataFrame to simple pd.DataFrame containing only
    # list of 2D coordinates along route.
    lines_gdf = extract_point_df(route_shp)

    # Calculate distance from one point to the next
    distance = []
    for idx in range(len(lines_gdf)-1):
        # x and y coordinates
        coordinate_1 = lines_gdf.loc[idx]['coordinates']
        coordinate_2 = lines_gdf.loc[idx + 1]['coordinates']
        # organize into tuples as: (Latatude, Longetude)
        swap_coord_1 = (coordinate_1[1], coordinate_1[0])
        swap_coord_2 = (coordinate_2[1], coordinate_2[0])
        # Calculate geodesic distances in meters and add to list
        distance.append(geodesic(swap_coord_1,swap_coord_2).m)

    # Calculate cumulative sum of distances along route with zero at
    # the beginning of the list for first point
    cum_distance = np.insert(np.cumsum(distance), 0, 0)

    return distance, cum_distance


def gradient(route_shp, rasterfile):
    """
        Calculates the elevation and road grade at each point along the route.

        Parameters
        ----------
        route_shp: GeoDataFrame for the selected route;
        output of read_shape().
        rasterfile: elevation data file (.tif)

        Returns
        -------
        elevation_meters: the elevation at each point along the route
        route_gradient: the road grade (e.g. slope) at each point along the route
        route_cum_distance: the total route distance at each point along the route [m]
        route_distance: the distance between each point [m]

        """

    # from the 'rasterstats' userguide:
        # "rasterstats, exists solely to extract information from
        # geospatial raster data based on vector geometries"

    # 'point_query' returns the values defined in the 'rasterfild'
    # at the points defined within the GeoDataFrame 'route_shp'
    elevation = rasterstats.point_query(route_shp, rasterfile)

    # Convert elevations to meters
    elevation_meters = np.asarray(elevation) * 0.3048

    # Calculate geodesic distances between points as well as cumulative
    # distances along route.
    route_distance, route_cum_distance = distance_measure(route_shp)

    # Calculate route gradient at each point along route
    #HJG: I am confused as to why we add zero to the beggining of the
        # list here, and also why we take the abs value. Seems like
        # the sign of the gradient would determine if we the bus is
        # going up or down a hill. I do see that we get back the right
        # length list
    route_gradient =  np.insert(
        (
            np.diff(elevation)
            /
            route_distance
            )
        ,
        0,
        0,
        )

    return elevation_meters, route_gradient, route_cum_distance, route_distance


def _make_lines(gdf, idx, geometry = 'geometry'):
    """
        Creates a line between each point; iterative function for
        make_multi_lines(), so it is not called directly.

        Parameters
        ----------
        gdf: DataFrame of coordinates; output of extract_pts_df()
        gradient: the road grade (e.g. slope) at each point along the route; output of gradient()
        idx: index
        geometry: DEFAULT = 'geometry'

        Returns
        -------
        df_line: DataFrame containing the line segments
        """

    coordinate_1 = gdf.loc[idx]['coordinates']
    coordinate_2 = gdf.loc[idx + 1]['coordinates']
    # Create shapely.Line object connection coordinates
    line = LineString([coordinate_1, coordinate_2])
    # # Organize gradient input argument with shapely.Line for insertion
    # # into output DataFrame.
    # data = {'gradient': gradient,
    #         'geometry':[line]}
    # df_line = pd.DataFrame(data, columns = ['gradient', 'geometry'])

    return line


def make_multi_lines(linestring_route_df, elevation_gradient):
    """
        Creates a GeoDataFrame containing the road grade and linestring
        for each point along the route.

        Parameters
        ----------
        linestring_route_df: DataFrame of coordinates; output of extract_pts_df()
        elevation_gradient: the road grade (e.g. slope) at each point along the route; output of gradient()

        Returns
        -------
        gdf_route: GeoDataFrame with columns ['gradient', 'geometry']
        """

    num_pt_connections = len(linestring_route_df) - 1

    # Initialize output column to contain Lines
    lin_col = []
    # Add None as first element corresponding to first route point of
    # zero gradient.
    lin_col.append(None)

    # Loop through row indicies of 'linestring_route_df' input to
    # generate Shapely Lines.
    for idx in range(num_pt_connections):
        df_line = _make_lines(
            linestring_route_df,
            idx
            # elevation_gradient[idx],
            )
        lin_col.append(df_line)



    route_df = linestring_route_df.assign(
        gradient=elevation_gradient,
        geometry=lin_col
        )

    gdf_route = gpd.GeoDataFrame(route_df)
    return gdf_route

    # # Initialize output DataFrame
    # df_route = pd.DataFrame(columns = ['gradient', 'geometry'])

    # # Loop through row indicies of 'linestring_route_df' input.
    # for idx in range(len(linestring_route_df) - 1):
    #     df_linestring = make_lines(linestring_route_df, elevation_gradient[idx], idx)
    #     df_route = pd.concat([df_route, df_linestring])
    # gdf_route = gpd.GeoDataFrame(df_route)
    # return gdf_route


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


def profile_plot(elevation, elevation_gradient, route_cum_distance, route_num):
    """
        Creates two plots. First shows elevation vs. distance. Second
        shows absolute grade vs. distance.

        Parameters
        ----------
        elevation: the elevation at each point along the route
        elevation_gradient: the road grade at each point along the route
        route_cum_distance: the total route distance at each point along
            the route [m]
        route_num: route number (integer)

        Returns
        -------
        plt: Elevation vs. distance and absolute grade vs. distance plots
        """

    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(15, 8))
    ax[0].plot(route_cum_distance, elevation.T, color='b', linewidth=4)
    ax[0].set_ylabel('Elevation (meter)', color='b')
    ax[0].tick_params('y', colors='b')
    ax[0].grid()

    ax[1].plot(route_cum_distance, elevation_gradient, color='r')
    ax[1].set_xlabel('Plain distance (meter)')
    ax[1].set_ylabel('Gradient', color='r')
    ax[1].tick_params('y', colors='r')
    ax[1].grid()

    fig.suptitle(
        'Elevation and Gradient Plot for Route {}'.format(route_num),
        fontsize=20,
        y=0.95,
        )

    return plt

def route_metrics(
    elevation,
    elevation_gradient,
    route_cum_distance,
    distance,
    route_num,
    ):
    """
        Estimates route difficulty based on four test metrics.

        Parameters
        ----------
        elevation: the elevation at each point along the route
        elevation_gradient: the road grade at each point along the route
        route_cum_distance: the total route distance at each point along
            the route [m]
        distance: the distance between each point [m]
        route_num: route number (integer)

        Returns
        -------
        display_metrics: string of metrics results
        metric_values: results of metrics calculations
        """

    metrics_1 = 100 * sum(elevation_gradient)/ max(route_cum_distance)
    metrics_2 = sum(
        abs(
            np.diff(elevation[0])
            )
        )/ max(route_cum_distance)
    metrics_3 = 100 * (
        sum(
            np.insert(
                np.diff(elevation)/ distance, 0, 0
                )[np.insert(np.diff(elevation)/ distance, 0, 0) > 0]
            )
        /
        max(route_cum_distance)
        )
    metrics_4 = -100 * (
        sum(
            np.insert(
                np.diff(elevation)/ distance, 0, 0
                )[np.insert(np.diff(elevation)/ distance, 0, 0) < 0]
            )
        /
        max(route_cum_distance)
        )
    metrics_values = (metrics_1, metrics_2, metrics_3, metrics_4)

    display_metrics = (
        ' Route Evaluation Metrics for Bus {} \n Normalized Gradient = {:.4f} '
        +
        '\n Differentiated Gradient = {:.4f} \n Positive Gradient = {:.4f} '
        +
        '\n Negative Gradient = {:.4f}'
        ).format(route_num, metrics_1, metrics_2, metrics_3, metrics_4)

    return display_metrics, metrics_values












