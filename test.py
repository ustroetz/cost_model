import main_model as m
from pprint import pprint
import ogr, trtr

### Harvest Type (clear cut = 0, partial cut = 1)
PartialCut = 0

### GIS Data
property_shp = 'U:\\My Documents\Tool\\Data\\testarea2.shp'
slope_raster = 'G:\\Basedata\\PNW\\terrain\\slope'
elevation_raster = 'G:\\Basedata\\PNW\\terrain\\dem_prjr6'

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
millID = 75
mill_Lat = None
mill_Lon = None

### Loop through stands
driver = ogr.GetDriverByName('ESRI Shapefile')
shp = driver.Open(property_shp, 0)
lyr = shp.GetLayer()
numFeatures = lyr.GetFeatureCount()
FID = 0
while FID < numFeatures:
    pprint (m.cost_model(slope_raster, elevation_raster, lyr, FID, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, millID, mill_Lat, mill_Lon, PartialCut))
    FID += 1
    print FID
