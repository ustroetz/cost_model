def main():
    import main_model as m
    import routing_main as r
    import landing
    from pprint import pprint
    import ogr
    import gis

    ### GIS Data
    slope_raster = '/usr/local/apps/land_owner_tools/lot/fixtures/downloads/terrain/slope.tif'
    elevation_raster = '/usr/local/apps/land_owner_tools/lot/fixtures/downloads/terrain/dem.tif'

    driver = ogr.GetDriverByName('ESRI Shapefile')
    property_shp = driver.Open('Data//test_stands.shp', 0)
    property_lyr = property_shp.GetLayer()
    stand_lyr = property_shp.GetLayer()
    feat = stand_lyr.GetFeature(0)
    geom = feat.GetGeometryRef()

    stand_wkt = geom.ExportToWkt()
    area = gis.area(stand_lyr)
    elevation = gis.zonal_stats(elevation_raster, stand_lyr)
    slope = gis.zonal_stats(slope_raster, stand_lyr)

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

    ### Mill information
    # Can use mill_lyr alone, mill_lyr AND millID, OR mill_Lat and mill_Lon
    # mill_shp = driver.Open('Data//ODF_mills.shp', 0)
    # mill_lyr = mill_shp.GetLayer()
    mill_lyr = None
    millID = None
    mill_Lat = 41.2564
    mill_Lon = -123.5677

    # Landing Coordinates 
    landing_coords = landing.landing(property_lyr)

    haulDist, haulTime, coord_mill = r.routing(
        landing_coords,
        millID,
        mill_Lat,
        mill_Lon,
        mill_lyr
    )

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
        landing_coords,
        haulDist,
        haulTime,
        coord_mill
    )

    pprint(cost)

main()
