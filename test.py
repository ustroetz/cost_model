def main():
    import main_model as m
    import routing_main as r
    from pprint import pprint
    import ogr

    ### Harvest Type (clear cut = 0, partial cut = 1)
    PartialCut = 0

    ### GIS Data
    slope_raster = 'G:\\Basedata\\PNW\\terrain\\slope'
    elevation_raster = 'G:\\Basedata\\PNW\\terrain\\dem_prjr6'

    driver = ogr.GetDriverByName('ESRI Shapefile')
    property_shp = driver.Open('Data//testarea6.shp', 0)
    property_lyr = property_shp.GetLayer()	
    stand_lyr = property_shp.GetLayer()

    mill_shp = driver.Open('Data//mills.shp', 0)
    mill_lyr = mill_shp.GetLayer()


    ### Tree Data ###
    # Hardwood Fraction
    HdwdFractionCT = 0.15
    HdwdFractionSLT = 0.0
    HdwdFractionLLT = 0.0

    # Chip Trees
    RemovalsCT = 0.0
    TreeVolCT = 0.0

    # Small Log Trees
    RemovalsSLT = 15.54
    TreeVolSLT = 39.1

    # Large Log Trees
    RemovalsLLT = 12.25
    TreeVolLLT = 96.08
    
    ### Mill information
    millID = None
    mill_Lat = None
    mill_Lon = None
	
    landing_geom, haulDist, haulTime, coord_mill = r.routing(property_lyr, millID, mill_Lat, mill_Lon, mill_lyr)

    pprint (m.cost_func(slope_raster, elevation_raster, stand_lyr, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, PartialCut, landing_geom, haulDist, haulTime, coord_mill))


main()



