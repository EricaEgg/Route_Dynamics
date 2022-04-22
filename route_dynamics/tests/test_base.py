""" These tests pass locally, but require the ~1Gb file 'seattle.tif'
    which I have not figured out how to crop to just route 45. They
    are commented out for travisCI.
"""
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString
from os import path
import sys
sys.path.append(path.abspath('..'))

from ..route_elevation import base

sys.path.append(path.abspath(path.join('..','..')))
shapefile = 'data/six_routes.shp'
rasterfile = 'data/seattle_dtm.tif'
route_num = 45
routes_shp= gpd.read_file(shapefile)
route_shp = routes_shp[routes_shp['ROUTE_NUM'] == route_num]


def test_read_shape():
    """
        Test if shapefile is for route number 45

        Parameters
        ----------
        shapefile: The path of a shapefile(.shp)

    """
    assert shapefile.endswith('.shp'), 'Input should be shapefile.'
    assert base.read_shape(shapefile,45)['ROUTE_NUM'].values[0] == 45, 'ROUTE_NUM is wrong!'
    return


def test_extract_point_df():
    """Test if the shape of dataframe is correct."""
    df45 = base.read_shape(shapefile, route_num)
    shape = base.extract_point_df(df45).shape
    assert shape == (208,1), " Shape of df(route 45) coordinates should be (208,1)"
    return


def test_distance_measure():
    """Test if the number of points in distance is correct"""
    distance, cum_distance = base.distance_measure(route_shp)
    assert len(distance) == 207 and len(distance) == len(cum_distance) - 1, 'For route 45, there should be 207 linestring being calculated the distance, and distance = cum_distance -1'
    return


# def test_gradient():
#     """Test if the elevation data convert to meter metric and gradient data have the right length."""
#     elevation_meters, route_gradient, route_cum_distance, route_distance = base.gradient(route_shp, rasterfile)
#     assert elevation_meters.max() < 104, 'elevation should convert to meter metric.'
#     assert len(route_gradient) == 208, 'length of gradient values should be 208.'
#     return


# def test_make_lines():
#     """Test if it can make a line with right length."""
#     coordinate_1 = [3,0]
#     coordinate_2 = [0,4]
#     line = LineString([coordinate_1, coordinate_2])
#     assert line.length == 5, 'calculation of linestring distance is wrong.'
#     return


# def test_make_multi_lines():
#     """Test if all gradient data are float64 type."""
#     linestring_route_df = base.extract_point_df(route_shp)
#     _, elevation_gradient, _, _ = base.gradient(route_shp,rasterfile)
#     gdf_route = base.make_multi_lines(linestring_route_df, elevation_gradient)
#     assert gdf_route['gradient'].dtype == 'float64', 'Gradient columns should only contain number with float64 dtype.'
#     return


# def test_route_map():
#     """Test if geodataframe contain null values."""
#     linestring_route_df = base.extract_point_df(route_shp)
#     _, elevation_gradient, _, _ = base.gradient(route_shp,rasterfile)
#     gdf_route = base.make_multi_lines(linestring_route_df, elevation_gradient)
#     if gdf_route.isnull().values.all():
#         raise ValueError('GeoDataFrame has some null value, check the sources.')
#     else:
#         pass
#     return


# def test_profile_plot():
#     """Test if input data contain nan values."""
#     _, route_gradient, route_cum_distance, _ = base.gradient(route_shp, rasterfile)
#     if np.isnan(route_cum_distance).any() or np.isnan(route_gradient).any() or np.isnan(route_cum_distance).any():
#         raise ValueError('Check the source. Array should not contain nan value.')
#     else:
#         pass
#     return


# def test_route_metrics():
#     """Test values of metrics are whether valid."""
#     elevation_meters, route_gradient, route_cum_distance, route_distance = base.gradient(route_shp, rasterfile)
#     _, metrics = base.route_metrics(elevation_meters, route_gradient, route_cum_distance, route_distance,45)
#     for idx in range(len(metrics)):
#         assert metrics[idx] >= 0, 'Values of ranking should greater than 0.'
#     return
