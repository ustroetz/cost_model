import ogr

def gis(stand):

    # get area
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open(stand, 0)
    lyr = shp.GetLayer()
    feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()

    area = geom.GetArea() # get area in m2

    area = round(area*0.000247105, 4) # convert to acre and round

    return area
