import requests, json, ogr, osr
import os
#ogr.UseExceptions()

#############################################
# Landing Coordinates                       #
#############################################

def landing(lyr):
    numFeatures = lyr.GetFeatureCount()
    FID = 0
    centroidLonList = []
    centroidLatList = []

    # get centroids of stands
    while FID < numFeatures:
        feat = lyr.GetFeature(FID)
        geom = feat.GetGeometryRef()

        # Transform from Web Mercator to WGS84
        sourceSR = lyr.GetSpatialRef()
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(4326) # WGS84
        coordTrans = osr.CoordinateTransformation(sourceSR,targetSR)
        geom.Transform(coordTrans)

        # Create centroid of harvest area
        centroid_geom = geom.Centroid()
        centroidLon = centroid_geom.GetX() #Get X coordinates
        centroidLat = centroid_geom.GetY() #Get Y cooridnates
        centroidLonList.append(centroidLon)
        centroidLatList.append(centroidLat)
        FID += 1

    # calcualte centroid of all stands
    centroidLon = sum(centroidLonList)/numFeatures
    centroidLat = sum(centroidLatList)/numFeatures

    # get nearest point on road from centroid as json string
    headers = {'User-Agent': 'Forestry Scenario Planner'}
    url = "http://router.project-osrm.org/nearest?loc=%f,%f" % (centroidLat, centroidLon)
    key = "%s_%s-None.cache" % (centroidLat, centroidLon)
    if os.path.exists(key):
        # READING FROM CACHE
        with open(key, 'r') as cache:
            data = json.loads(cache.read())
    else:
        response = requests.get(url, headers=headers)
        binary = response.content
        data = json.loads(binary)
        # WRITING TO CACHE
        with open(key, 'w') as cache:
            cache.write(json.dumps(data))

    # parse json string for landing coordinate
    landing_lat, landing_lon = data['mapped_coordinate']

    # create ogr geom point from strings
    landing_geom = ogr.Geometry(ogr.wkbPoint)
    landing_geom.AddPoint(landing_lon, landing_lat)

    return landing_geom
