import base
import single_route


def test_route_analysis_all():
    """
    Check that the outputs are the correct type. 
    """
    
    shapefile = 'six_routes.shp'
    rasterfile = 'seattle_dtm.tif
    route_num = 45
    
    example = single_route.route_analysis_all(route_num, shapefile, 
rasterfile)
    
    assert type(example[0]) == folium.folium.Map
    assert type(example[1]) == module
    assert type(example[2]) == str
    
    return


def test_route_analysis_profile():
    """
       Test that the output is the correct type
    """
    shapefile = 'six_routes.shp'
    rasterfile = 'seattle_dtm.tif
    route_num = 45
    
    example = single_route.route_analysis_profile(route_num, shapefile, 
rasterfile)
    
    assert type(example) == module
    
    return


def test_route_analysis_map():
    """
       Test that the output is the correct type
    """ 
    shapefile = 'six_routes.shp'
    rasterfile = 'seattle_dtm.tif
    route_num = 45
    
    example = single_route.route_analysis_map(route_num, shapefile, 
rasterfile)
    
    assert type(example) == folium.folium.Map
    
    return


def test_route_analysis_df():
    """
       Test that the output is the correct length
    """
    shapefile = 'six_routes.shp'
    rasterfile = 'seattle_dtm.tif'
    route_num = 45
    
    example = single_route.route_analysis_df(route_num, shapefile, 
rasterfile)
    
    assert len(example) == 207
    
    return


def test_route_analysis_metrics():
    """
       Test that the output is the correct type
    """
    shapefile = 'six_routes.shp'
    rasterfile = 'seattle_dtm.tif'
    route_num = 45
    
    example = single_route.route_analysis_df(route_num, shapefile, 
rasterfile)
    
    assert type(example) == str
    
    return
    
