import main_model as m
PartialCut = 0

### GIS Data ###
stand = 'U:\\My Documents\Tool\\Data\\testarea4.shp'
slope_raster = 'G:\\Basedata\\PNW\\terrain\\slope'
elevation_raster = 'G:\\Basedata\\PNW\\terrain\\dem_prjr6'


### Tree Data ###
# Chip Trees
RemovalsCT = 0.0
TreeVolCT = 0.0

# Small Log Trees
RemovalsSLT = 100.0
TreeVolSLT = 50.0

# Large Log Trees
RemovalsLLT = 10.0
TreeVolLLT = 80.0

print m.cost_model(stand, slope_raster, elevation_raster, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, PartialCut)
