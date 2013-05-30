import requests, json, ogr, osr

def skidding(stand):
    # get centroid coordinates of harvest area
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open(stand, 0)
    lyr = shp.GetLayer()
    feat = lyr.GetNextFeature()
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

    # create ogr point from strings
    landing_point = ogr.Geometry(ogr.wkbPoint)
    landing_point.AddPoint(landing_lat,landing_lon)

    # get distance from centroid to landing
    dist = centroid_geom.Distance(landing_point) # shortest distance to road from centroid of stand
    YardDist = round((dist)*3.28084, 2) # convert to feet

    # Set max YardDist
    HaulDistExtension = 0
    YardDistLimit = 3000.0
    if YardDist > YardDistLimit:
        HaulDistExtension = (YardDist-YardDistLimit)*0.000189394
        YardDist = YardDistLimit

    return YardDist, HaulDistExtension, landing_coord

