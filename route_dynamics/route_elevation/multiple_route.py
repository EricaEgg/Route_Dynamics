import pandas as pd

from . import base


def routes_analysis_ranking(route_list, shapefile, rasterfile):
    """
    Computes the four chosen metrics values for each bus routes in route_list and display them on a bar plot for
    ease of comparison

    Parameters
    ----------
    route_list: A list of bus routes to be compared (Integers)
    shapefile: route geospatial data (.shp file)
    rasterfile: elevation data file (.tif)

    Returns
    -------
    bar plot: showing results comparison between bus routes according to the four metrics chosen
    """
    num_route = len(route_list)
    metrics_1 = [0] * num_route
    metrics_2 = [0] * num_route
    metrics_3 = [0] * num_route
    metrics_4 = [0] * num_route
    for idx, route_num in enumerate(route_list):
        route_shp = base.read_shape(shapefile, route_num)

        elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

        _ , metrics = base.route_metrics(elevation, elevation_gradient, route_cum_distance, distance, route_num)

        metrics_1[idx], metrics_2[idx], metrics_3[idx], metrics_4[idx] = metrics

    data = pd.DataFrame({'Bus Num': route_list, 'M1': metrics_1, 'M2': metrics_2, 'M3': metrics_3, 'M4': metrics_4})
    ax = data.plot.bar('Bus Num', figsize= [14, 5], fontsize= 20)
    ax.set_ylabel('Metrics', size= 20)
    ax.set_xlabel('Bus Number', size= 20)

    return ax
