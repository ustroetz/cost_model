import ogr
import osr
ogr.UseExceptions()


def skidding(stand_wkt, landing_coords, Slope):

    # create geometry
    geom = ogr.CreateGeometryFromWkt(stand_wkt)

    landing_geom = ogr.Geometry(ogr.wkbPoint)
    landing_geom.AddPoint(*landing_coords)

    # Transform landing coordinates from WGS84 to Web Mercator
    inSR = landing_geom.GetSpatialReference()
    if inSR is None:
        sourceSR = osr.SpatialReference()
        sourceSR.ImportFromEPSG(4326)  # WGS84
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(3857)  # Web Mercator
        coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
        landing_geom.Transform(coordTrans)

    # Create centroid of harvest area
    centroid_geom = geom.Centroid()

    # Create skidding line
    skidLine = ogr.Geometry(type=ogr.wkbLineString)
    skidLine.AddPoint(centroid_geom.GetX(), centroid_geom.GetY())
    skidLine.AddPoint(landing_geom.GetX(), landing_geom.GetY())

    skidLineStand = geom.Intersection(skidLine)

    if skidLineStand.GetGeometryType() == 2:  # linestring
        lon, lat, y = skidLineStand.GetPoint(0)
        point_geom = ogr.Geometry(ogr.wkbPoint)
        point_geom.AddPoint(lon, lat)
        if point_geom.Within(geom) is False:
            landing_stand_geom = point_geom
        else:
            lon, lat, y = skidLineStand.GetPoint(1)
            point_geom = ogr.Geometry(ogr.wkbPoint)
            point_geom.AddPoint(lon, lat)
            landing_stand_geom = point_geom

        dist_landing_stand = centroid_geom.Distance(landing_stand_geom)

    elif skidLineStand.GetGeometryType() == 5:  # multilinestring
        distList = []
        for line in skidLineStand:
            lon, lat, y = line.GetPoint(0)
            point_geom = ogr.Geometry(ogr.wkbPoint)
            point_geom.AddPoint(lon, lat)
            if point_geom.Within(geom) is False:
                landing_stand_geom = point_geom
            else:
                lon, lat, y = line.GetPoint(1)
                point_geom = ogr.Geometry(ogr.wkbPoint)
                point_geom.AddPoint(lon, lat)
                landing_stand_geom = point_geom
                
            # get distance from centroid to landing at stand
            distance = centroid_geom.Distance(landing_stand_geom)
            dist_landing = (distance, landing_stand_geom)
            distList.append(dist_landing)

        dist_landing_stand, landing_stand_geom = max(distList)

    else:
        raise Exception("skidLineStand has unknown geometry type %s" % skidLineStand.GetGeometryType())

    YardDist = round((dist_landing_stand)*3.28084, 2)  # convert to feet

    # get distance from centroid to landing
    dist_landing = centroid_geom.Distance(landing_geom)  # shortest distance to road from centroid of stand

    # get Haul Distance Extension
    HaulDistExtension = round((dist_landing - dist_landing_stand)*3.28084, 2)  # convert to feet
    # Set max YardDist
    YardDistLimit = 1300.0
    if YardDist > 1300 and Slope > 40:
        YardDistLimit = 10000.0
        if YardDist > YardDistLimit:
                HaulDistExtension = (YardDist-YardDistLimit) + HaulDistExtension
                YardDist = YardDistLimit

    elif YardDist > YardDistLimit:
        HaulDistExtension = (YardDist-YardDistLimit) + HaulDistExtension
        YardDist = YardDistLimit

    # Transform from WGS84 to Web Mercator
    inSR = landing_stand_geom.GetSpatialReference()
    if inSR is None:
        sourceSR = osr.SpatialReference()
        sourceSR.ImportFromEPSG(3857)  # Web Mercator
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(4326)  # WGS84
        coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
        landing_stand_geom.Transform(coordTrans)

    # Create coordinate stand landing tuple
    landing_lat, landing_lon = landing_stand_geom.GetX(), landing_stand_geom.GetY()
    coord_landing_stand = (landing_lat, landing_lon)
    coord_landing_stand_tuple = tuple(coord_landing_stand)
    
    return YardDist, HaulDistExtension, coord_landing_stand_tuple
