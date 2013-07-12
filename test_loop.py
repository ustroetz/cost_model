from forestcost import main_model as m
from forestcost import routing as r
from pprint import pprint
import ogr


def main():
    ### Harvest Type (clear cut = 0, partial cut = 1)
    PartialCut = 0

    ### GIS Data
    slope_raster = 'G:\\Basedata\\PNW\\terrain\\slope'
    elevation_raster = 'G:\\Basedata\\PNW\\terrain\\dem_prjr6'

    driver = ogr.GetDriverByName('ESRI Shapefile')
    property_shp = driver.Open('U:\\My Documents\Tool\\Data\\testarea6.shp', 0)
    property_lyr = property_shp.GetLayer()
    stand_lyr = property_shp.GetLayer()

    ### Mill information
    mill_shp = 'U:\\My Documents\Tool\\Data\\mills.shp'

#    landing_geom, haulDist, haulTime, coord_mill = r.routing(property_lyr, mill_shp=mill_shp)

    import csv
    data = csv.reader(open('C:\\Users\\ustroetz\\Downloads\\fvsaggregate.csv', 'rb'))
    data.next()
    for row in data:
        print row[1]
    
        ### Tree Data ###
        # Hardwood Fraction
        HdwdFractionCT = 0.15
        HdwdFractionSLT = 0.0
        HdwdFractionLLT = 0.0

        # Chip Trees
        RemovalsCT = float(row[19])
        TreeVolCT = float(row[17])

        # Small Log Trees
        RemovalsSLT = float(row[29])
        TreeVolSLT = float(row[27])

        # Large Log Trees
        RemovalsLLT = float(row[43])
        TreeVolLLT = float(row[41])

        print RemovalsCT, RemovalsSLT, RemovalsLLT

#        pprint (m.cost_func(slope_raster, elevation_raster, stand_lyr, mill_lyr, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, PartialCut, landing_geom, haulDist, haulTime, coord_mill))
      

main()



