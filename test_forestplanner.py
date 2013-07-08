def main():
    import main_model as m
    import routing_main as r
    import ogr
    from pprint import pprint

    driver = ogr.GetDriverByName('ESRI Shapefile')
    property_shp = driver.Open('Data//test_stands.shp', 0)
    property_lyr = property_shp.GetLayer()
    stand_lyr = property_shp.GetLayer()
    feat = stand_lyr.GetNextFeature()

    ### Mill information
    # Can use mill_lyr alone, mill_lyr AND millID, OR mill_Lat and mill_Lon
    # mill_shp = driver.Open('Data//ODF_mills.shp', 0)
    # mill_lyr = mill_shp.GetLayer()
    mill_lyr = None
    millID = None
    mill_Lat = 41.2564
    mill_Lon = -123.5677

    landing_geom, haulDist, haulTime, coord_mill = r.routing(
        property_lyr,
        millID,
        mill_Lat,
        mill_Lon,
        mill_lyr
    )

    while feat:
        ### GIS Data
        geom = feat.GetGeometryRef()
        stand_wkt = geom.ExportToWkt()
        area = 15.5  # gis.area(stand_lyr)
        elevation = 600  # gis.zonal_stats(elevation_raster, stand_lyr)
        slope = 14.33  # gis.zonal_stats(slope_raster, stand_lyr)

        ### Tree Data ###
        # Harvest Type (clear cut = 0, partial cut = 1)
        PartialCut = 0
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

        cost = m.cost_func(
            # stand info
            area,
            elevation,
            slope,
            stand_wkt,
            # harvest info
            RemovalsCT,
            TreeVolCT,
            RemovalsSLT,
            TreeVolSLT,
            RemovalsLLT,
            TreeVolLLT,
            HdwdFractionCT,
            HdwdFractionSLT,
            HdwdFractionLLT,
            PartialCut,
            # routing info
            landing_geom,
            haulDist,
            haulTime,
            coord_mill
        )

        print cost['total_cost']
        #pprint(cost)
        feat = stand_lyr.GetNextFeature()

main()
