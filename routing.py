# determines the distance and time from the landing to the mill

import requests, json, ogr

def routing(landing_lat, landing_lon, millID , mill_Lat , mill_Lon):

    # create landing coordinates
    coord_landing = '%f,%f' %(landing_lat,landing_lon)

    # query mill layer based on trees
    min_dbh = 0.0
    max_dbh = 999.0
    driver = ogr.GetDriverByName('ESRI Shapefile')
    millshp = driver.Open('U:\My Documents\Tool\Data\mills.shp', 0)
    milllyr = millshp.GetLayer()
    milllyr.SetAttributeFilter("min_dbh >= %s and max_dbh <= %s" % (str(min_dbh), str(max_dbh)))
	
    def get_point():
            # get mill coordinates
            mill_geom = millfeat.GetGeometryRef()
            mill_Lon = mill_geom.GetX()
            mill_Lat = mill_geom.GetY()
            coord_mill = '%f,%f' %(mill_Lat, mill_Lon)
            return coord_mill
            
    def routing(coord_landing, coord_mill):
        # get routing json string from landing to mill
        headers = {'User-Agent': 'Forestry Scenario Planner'}
        url = 'http://router.project-osrm.org/viaroute?loc=' + coord_landing + '&loc=' + coord_mill
        response = requests.get(url, headers=headers)
        binary = response.content
        data = json.loads(binary)

        # parse json string for distance
        total_summary = data['route_summary']
        total_distance = total_summary['total_distance'] # in meters
        total_time = total_summary['total_time']# in sec
        return total_distance, total_time

    # determine mill and run routing 
    if millID is not None:
        milllyr.SetAttributeFilter("ObjectID = %s" % (str(millID)))
        millfeat = milllyr.GetNextFeature()
        coord_mill = get_point()
        total_distance, total_time = routing(coord_landing, coord_mill)
        total_distance = total_distance*0.000621371 # convert to miles
        total_time = total_time/60.0 # convert to min 
    elif mill_Lat is not None:
        coord_mill = '%f,%f' %(mill_Lat, mill_Lon)
        total_distance, total_time = routing(coord_landing, coord_mill)
        total_distance = total_distance*0.000621371 # convert to miles
        total_time = total_time/60.0 # convert to min
    else:
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
            coord_mill = get_point()

            total_distance, total_time = routing(coord_landing, coord_mill)

            distDict[coord_mill] = total_distance
            timeDict[coord_mill] = total_time
            
            millfeat.Destroy()
            millfeat = milllyr.GetNextFeature()

        # Remove items from Dictionary where distance is 0, mill not on road    
        distDict = {key: value for key, value in distDict.items()
                    if value > 0}

        # get distance and time to closest mill
        coord_mill = min(distDict, key=distDict.get)
        total_distance = distDict[coord_mill]*0.000621371 # convert to miles
        total_time = timeDict[coord_mill]/60.0 # convert to min

    return total_distance, total_time, coord_mill


