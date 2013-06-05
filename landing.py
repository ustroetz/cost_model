import requests, json, ogr, osr

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
    url = "http://router.project-osrm.org/nearest?loc=%f,%f"%(centroidLat, centroidLon)
    response = requests.get(url, headers=headers)
    binary = response.content
    data = json.loads(binary)

    # parse json string for landing coordinate
    landing_coord = data['mapped_coordinate']
    landing_lat = landing_coord[0]
    landing_lon = landing_coord[1]

    return landing_lat, landing_lon
