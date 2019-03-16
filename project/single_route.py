import base

def route_analysis(route_num, shapefile, rasterfile):
    """input the number of route, then output a GeoDataFrame with gradient and geometry
    information of that route, and elevation_gradient for each line segment. 
    Also will save the route as shapefile named 'route_num'."""
    route_shp = base.read_shape(shapefile, route_num)
    
    linestring_route_df = base.extract_point_df(route_shp)
    
    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, route_num, rasterfile)

    gdf_route = base.make_multi_lines( linestring_route_df, elevation_gradient) 
    
    map_display = base.route_map(gdf_route)
    
    route_plot = base.profile_plot(elevation, elevation_gradient, route_cum_distance, route_num)
    
    return map_display, route_plot

