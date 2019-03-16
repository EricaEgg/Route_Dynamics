import base


def route_analysis_all(route_num, shapefile, rasterfile):
    """input the number of route, then output a GeoDataFrame with gradient and geometry
    information of that route, and elevation_gradient for each line segment. 
    Also will save the route as shapefile named 'route_num'."""
    route_shp = base.read_shape(shapefile, route_num)
    
    linestring_route_df = base.extract_point_df(route_shp)
    
    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

    gdf_route = base.make_multi_lines( linestring_route_df, elevation_gradient) 
    
    map_display = base.route_map(gdf_route)
    
    route_plot = base.profile_plot(elevation, elevation_gradient, route_cum_distance, route_num)
    
    _, _, _, _, route_diff_metrics = base.route_metrics(elevation, elevation_gradient, route_cum_distance, distance, route_num)
    
    return map_display, route_plot, route_diff_metrics


def route_analysis_profile(route_num, shapefile, rasterfile):
    """input the number of route, then output a GeoDataFrame with gradient and geometry
    information of that route, and elevation_gradient for each line segment. 
    Also will save the route as shapefile named 'route_num'."""
    route_shp = base.read_shape(shapefile, route_num)
    
    linestring_route_df = base.extract_point_df(route_shp)
    
    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

    gdf_route = base.make_multi_lines( linestring_route_df, elevation_gradient) 
    
    route_plot = base.profile_plot(elevation, elevation_gradient, route_cum_distance, route_num)
    
    return route_plot


def route_analysis_map(route_num, shapefile, rasterfile):
    """input the number of route, then output a GeoDataFrame with gradient and geometry
    information of that route, and elevation_gradient for each line segment. 
    Also will save the route as shapefile named 'route_num'."""
    route_shp = base.read_shape(shapefile, route_num)
    
    linestring_route_df = base.extract_point_df(route_shp)
    
    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

    gdf_route = base.make_multi_lines( linestring_route_df, elevation_gradient) 
    
    map_display = base.route_map(gdf_route)
    
    return map_display

def route_analysis_df(route_num, shapefile, rasterfile):
    """input the number of route, then output a GeoDataFrame with gradient and geometry
    information of that route, and elevation_gradient for each line segment. 
    Also will save the route as shapefile named 'route_num'."""
    route_shp = base.read_shape(shapefile, route_num)
    
    linestring_route_df = base.extract_point_df(route_shp)
    
    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)

    gdf_route = base.make_multi_lines( linestring_route_df, elevation_gradient) 
    
    return gdf_route


def route_analysis_metrics(route_num, shapefile, rasterfile):
    """input the number of route, then output a GeoDataFrame with gradient and geometry
    information of that route, and elevation_gradient for each line segment. 
    Also will save the route as shapefile named 'route_num'."""
    route_shp = base.read_shape(shapefile, route_num)
    
    linestring_route_df = base.extract_point_df(route_shp)
    
    elevation, elevation_gradient, route_cum_distance, distance = base.gradient(route_shp, rasterfile)
    
    _, _, _, _, route_diff_metrics = base.route_metrics(elevation, elevation_gradient, route_cum_distance, distance, route_num)
    
    print(route_diff_metrics)
    
    return 

