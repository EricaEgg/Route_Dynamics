import folium
import matplotlib.pyplot as plt
from os import path
import sys
sys.path.append(path.abspath('..'))

import base
import single_route

shapefile = '../../data/six_routes.shp'
rasterfile = '../../data/sea_dtm_north.tif'


def test_route_analysis_all():
    """
    Check that the outputs are the correct type. 
    """
    route_num = 45
    
    example = single_route.route_analysis_all(route_num, shapefile, 
rasterfile)
    
    assert type(example[0]) == folium.folium.Map, 'Error in returning Folium interactive map'
    assert type(example[2]) == str, 'Wrong route metrics structure'
    
    return


def test_route_analysis_profile():
    """
       Test that the output is the correct type
    """
    route_num = 45
    
    example = single_route.route_analysis_profile(route_num, shapefile, 
rasterfile)
    
    # assert type(example) == object, 'Wrong display structure'
    
    return


def test_route_analysis_map():
    """
       Test that the output is the correct type
    """ 
    route_num = 45
    
    example = single_route.route_analysis_map(route_num, shapefile, 
rasterfile)
    
    assert type(example) == folium.folium.Map, 'Error in returning Folium interactive map'
    
    return


def test_route_analysis_df():
    """
       Test that the output is the correct length
    """
    route_num = 45
    
    example = single_route.route_analysis_df(route_num, shapefile, 
rasterfile)
    
    assert len(example) == 207, 'For route 45, there should be 207 linestring being calculated the distance'
    
    return


def test_route_analysis_metrics():
    """
       Test that the output is the correct type
    """
    route_num = 45
    
    example = single_route.route_analysis_df(route_num, shapefile, 
rasterfile)
    
    # assert type(example[0]) == str, 'Wrong route metrics structure'
    
    return
    
