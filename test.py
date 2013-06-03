import main_model as m

### Harvest Type (clear cut = 0, partial cut = 1)
PartialCut = 0

### GIS Data
stand = 'U:\\My Documents\Tool\\Data\\testarea1.shp'
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

print m.cost_model(stand, slope_raster, elevation_raster, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, millID, mill_Lat, mill_Lon, PartialCut)
