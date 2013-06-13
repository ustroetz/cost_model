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
    property_shp = driver.Open('U:\\My Documents\Tool\\Data\\test_stands.shp', 0)
    property_lyr = property_shp.GetLayer()	
    stand_lyr = property_shp.GetLayer()

    mill_shp = driver.Open('U:\\My Documents\Tool\\Data\\mills.shp', 0)
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
    RemovalsSLT = 100.0
    TreeVolSLT = 50.0

    # Large Log Trees
    RemovalsLLT = 10.0
    TreeVolLLT = 80.0
    
    ### Mill information
    millID = None
    mill_Lat = None
    mill_Lon = None
	
    landing_geom, haulDist, haulTime, coord_mill = r.routing(property_lyr, millID, mill_Lat, mill_Lon, mill_lyr)

    pprint (m.cost_func(slope_raster, elevation_raster, stand_lyr, mill_lyr, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, PartialCut, landing_geom, haulDist, haulTime, coord_mill))


main()



