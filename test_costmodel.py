from forestcost import main_model as m
from forestcost import routing as r
from forestcost import landing
from forestcost import gis
from pprint import pprint
import ogr

if __name__ == '__main__':
    ### GIS Data
    slope_raster = 'testdata//slope.tif'
    elevation_raster = 'testdata//dem.tif'

    property_shp = ogr.Open('testdata//test_stand.shp')
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
    RemovalsCT = 200.0
    TreeVolCT = 5.0

    # Small Log Trees
    RemovalsSLT = 100.00
    TreeVolSLT = 70.0

    # Large Log Trees
    RemovalsLLT = 20.00
    TreeVolLLT = 100.00

    ### Mill information
    mill_shp = 'testdata//mills.shp'
    #mill_coords = (-123.5677, 41.2564)

    # Landing Coordinates
    landing_coords = landing.landing(property_lyr)
    haulDist, haulTime, coord_mill = r.routing(
        landing_coords,
        mill_shp=mill_shp
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




