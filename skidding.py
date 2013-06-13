import requests, json, ogr, osr

def skidding(lyr, landing_geom, Slope):

    # get geometry
    feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()

    # Transform landing coordinates from from WGS84 to Web Mercator
    inSR = landing_geom.GetSpatialReference()
    if inSR is None:
        sourceSR = osr.SpatialReference()
        sourceSR.ImportFromEPSG(4326) # WGS84
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(3857) # Web Mercator
        coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
        landing_geom.Transform(coordTrans)

    # Create centroid of harvest area
    centroid_geom = geom.Centroid()
    centroidLat = centroid_geom.GetX() #Get X coordinates
    centroidLon = centroid_geom.GetY() #Get Y cooridnates

    # Create skidding line
    skidLine = ogr.Geometry(type=ogr.wkbLineString)
    skidLine.AddPoint(centroid_geom.GetX(), centroid_geom.GetY())
    skidLine.AddPoint(landing_geom.GetX(), landing_geom.GetY())
 
    skidLineStand = geom.Intersection(skidLine)
    for p in range(1):
        p +=1
        lon, lat, y = skidLineStand.GetPoint(p)
        point_geom = ogr.Geometry(ogr.wkbPoint)
        point_geom.AddPoint(lon, lat)
        if point_geom.Within(geom) is False:
            landing_stand_geom = point_geom


    # get distance from centroid to landing
    dist_landing = centroid_geom.Distance(landing_geom) # shortest distance to road from centroid of stand
    # get distance from centroid to landing at stand
    dist_landing_stand = centroid_geom.Distance(landing_stand_geom) 
    YardDist = round((dist_landing_stand)*3.28084, 2) # convert to feet
    # get Haul Distance Extension
    HaulDistExtension = dist_landing - dist_landing_stand

    # Set max YardDist
    YardDistLimit = 1300.0
    if YardDist > 1300 and Slope > 40:
        YardDistLimit = 10000.0
        if YardDist > YardDistLimit:
                HaulDistExtension = (YardDist-YardDistLimit)+ HaulDistExtension
                YardDist = YardDistLimit

    elif YardDist > YardDistLimit:
        HaulDistExtension = (YardDist-YardDistLimit) + HaulDistExtension
        YardDist = YardDistLimit

    # Transform fromWGS84 to Web Mercator
    inSR = landing_stand_geom.GetSpatialReference()
    if inSR is None:
        sourceSR = osr.SpatialReference()
        sourceSR.ImportFromEPSG(3857) # Web Mercator
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(4326) # WGS84
        coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
        landing_stand_geom.Transform(coordTrans)


    return YardDist, HaulDistExtension, landing_stand_geom



