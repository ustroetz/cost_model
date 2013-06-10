import requests, json, ogr, osr

def skidding(lyr, FID, landing_geom, Slope):

    # get geometry
    feat = lyr.GetFeature(FID)
    geom = feat.GetGeometryRef()

    # Transform fromWGS84 to Web Mercator
    inSR = landing_geom.GetSpatialReference()
    if inSR is None:
        sourceSR = osr.SpatialReference()
        sourceSR.ImportFromEPSG(4326) # WGS84
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(3857) # WGS84
        coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
        landing_geom.Transform(coordTrans)

    # Create centroid of harvest area
    centroid_geom = geom.Centroid()
    centroidLat = centroid_geom.GetX() #Get X coordinates
    centroidLon = centroid_geom.GetY() #Get Y cooridnates

    # get distance from centroid to landing
    dist = centroid_geom.Distance(landing_geom) # shortest distance to road from centroid of stand
    YardDist = round((dist)*3.28084, 2) # convert to feet

    # Loop through stand vertexes and get max dist from centro to polygon edge
    ring = geom.GetGeometryRef(0)
    points = ring.GetPointCount()
    distList = []
    for p in xrange(points):
            lon, lat, y = ring.GetPoint(p)
            # create ogr point from strings
            polyVertex_geom = ogr.Geometry(ogr.wkbPoint)
            polyVertex_geom.AddPoint(lon, lat)
            dist = centroid_geom.Distance(polyVertex_geom)
            distList.append(dist)
    DistStand = max(distList)*3.28084 # get max of list and convert to feet

    # Set max YardDist
    HaulDistExtension = 0.0
    YardDistLimit = 3000.0
    if YardDist > 1300 and Slope > 40:
        YardDistLimit = 10000.0
        if YardDist > YardDistLimit:
                HaulDistExtension = (YardDist-YardDistLimit)
                YardDist = YardDistLimit

    elif (YardDist-DistStand) > YardDistLimit:
        HaulDistExtension = (YardDist-YardDistLimit)
        YardDist = YardDistLimit

    return YardDist, HaulDistExtension



