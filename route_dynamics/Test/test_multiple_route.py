import matplotlib
import matplotlib.pyplot as plt
from os import path
import sys
sys.path.append(path.abspath('..'))

import base
import multiple_route

shapefile = '../../data/six_routes.shp'
rasterfile = '../../data/seattle_dtm.tif'


def test_routes_analysis_ranking():
    """
       Test that the output is a matplotlib plot
    """
    route_list = [40, 45]
    
    temp = multiple_route.routes_analysis_ranking(route_list, shapefile, rasterfile)
    
    assert rasterfile.endswith('.tif'), 'Rasterfile should be .tif.'
    assert shapefile.endswith('.shp'), 'Shapefile should be .shp.'


    return
