import base
import single_route
import multiple_route


def test_routes_analysis_ranking():
    """
       Test that the output is a matplotlib plot
    """
    route_list = [40, 45]
    shapefile = 'six_routes.shp'
    rasterfile = 'seattle_dtm.tif'
    
    temp = multiple_route.routes_analysis_ranking(route_list, shapefile, rasterfile)
    
    assert type(temp) == matplotlib.axes._subplots.AxesSubplot

    return
