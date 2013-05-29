# determines the distance and time from the landing to the mill

import requests, json, ogr

def routing(landing_lat, landing_lon, min_dbh = 0.0, max_dbh = 999.0):
    
    # create landing cpoint
    landing_point = '%f,%f' %(landing_lat,landing_lon)

    # query mill layer based on trees
    min_dbh = 0.0
    max_dbh = 999
    driver = ogr.GetDriverByName('ESRI Shapefile')
    millshp = driver.Open('U:\My Documents\Tool\Data\mills.shp', 0)
    milllyr = millshp.GetLayer()
    milllyr.SetAttributeFilter("min_dbh >= %s and max_dbh <= %s" % (str(min_dbh), str(max_dbh)))

    # set spatial filter around landing to include only close by mills
    offset = 0.05
    while True:
        offset += 0.05

        dfMinX = landing_lon - offset
        dfMaxX = landing_lon + offset
        dfMinY = landing_lat - offset
        dfMaxY = landing_lat + offset

        milllyr.SetSpatialFilterRect(dfMinX, dfMinY, dfMaxX, dfMaxY)
        millfeat = milllyr.GetNextFeature()

        if millfeat:
            break

    distDict = {}
    timeDict = {}

    while millfeat:
        # get mill coordinates
        mill_geom = millfeat.GetGeometryRef()
        mill_Lon = mill_geom.GetX()
        mill_Lat = mill_geom.GetY()
        mill_point = '%f,%f' %(mill_Lat, mill_Lon)

        # get routing json string from landing to mill
        headers = {'User-Agent': 'Forestry Scenario Planner'}
        url = 'http://router.project-osrm.org/viaroute?loc=' + landing_point + '&loc=' + mill_point
        response = requests.get(url, headers=headers)
        binary = response.content
        data = json.loads(binary)

        # parse json string for distance
        total_summary = data['route_summary']
        total_distance = total_summary['total_distance'] # in meters
        total_time = total_summary['total_time']# in sec

        distDict[mill_point] = total_distance
        timeDict[mill_point] = total_time
        
        millfeat.Destroy()
        millfeat = milllyr.GetNextFeature()

    # Remove items from Dictionary where distance is 0, mill not on road    
    distDict = {key: value for key, value in distDict.items()
                if value > 0}

    # get distance and time to closest mill
    coord_mill = min(distDict, key=distDict.get)
    total_distance = distDict[coord_mill]*0.000621371 # convert to miles
    total_time = timeDict[coord_mill]/60.0 # convert to min

    return total_distance, total_time


