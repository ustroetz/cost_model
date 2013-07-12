# determines the distance and time from the landing to the mill
import requests
import json
import ogr
import os
import tempfile


def routing(landing_coords, millID, mill_Lat, mill_Lon, mill_lyr):

    # create landing coordinates
    # TODO unnecessary to create geom and string, use tuple for point
    landing_geom = ogr.Geometry(ogr.wkbPoint)
    landing_geom.AddPoint(*landing_coords)
    landing_lon = landing_geom.GetX()
    landing_lat = landing_geom.GetY()
    coord_landing = '%f,%f' % (landing_lat, landing_lon)

    def get_point():
        # get mill coordinates
        # TODO unnecessary to use geom and string, instead use tuple for point
        mill_geom = millfeat.GetGeometryRef()
        mill_Lon = mill_geom.GetX()
        mill_Lat = mill_geom.GetY()
        coord_mill = '%f,%f' % (mill_Lat, mill_Lon)
        return coord_mill

    def routing(coord_landing, coord_mill):
        # get routing json string from landing to mill
        headers = {'User-Agent': 'Forestry Scenario Planner'}
        url = 'http://router.project-osrm.org/viaroute?loc=' + coord_landing + '&loc=' + coord_mill
        tmp = tempfile.gettempdir()
        key = os.path.join(tmp, "%s-%s.cache" % tuple([x.replace(",", "_") for x in [coord_landing, coord_mill]]))
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

        # parse json string for distance
        total_summary = data['route_summary']
        total_distance = total_summary['total_distance'] # in meters
        total_time = total_summary['total_time']# in sec
        return total_distance, total_time

    # determine mill and run routing 
    if millID is not None:
        mill_lyr.SetAttributeFilter("ObjectID = %s" % (str(millID)))
        millfeat = mill_lyr.GetNextFeature()
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
        # query mill layer based on trees
        min_dbh = 0.0
        max_dbh = 999.0
        mill_lyr.SetAttributeFilter("min_dbh >= %s and max_dbh <= %s" % (str(min_dbh), str(max_dbh)))

        # set spatial filter around landing to include only close by mills
        offset = 0.05
        while True:
            offset += 0.05

            dfMinX = landing_lon - offset
            dfMaxX = landing_lon + offset
            dfMinY = landing_lat - offset
            dfMaxY = landing_lat + offset

            mill_lyr.SetSpatialFilterRect(dfMinX, dfMinY, dfMaxX, dfMaxY)
            millfeat = mill_lyr.GetNextFeature()

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
            millfeat = mill_lyr.GetNextFeature()

        # Remove items from Dictionary where distance is 0, mill not on road    
        distDict = {key: value for key, value in distDict.items()
                    if value > 0}

        # get distance and time to closest mill
        coord_mill = min(distDict, key=distDict.get)
        total_distance = distDict[coord_mill]*0.000621371 # convert to miles
        total_time = timeDict[coord_mill]/60.0 # convert to min

    coord_mill_tuple = tuple([float(x) for x in coord_mill.split(",")])
    return total_distance, total_time, coord_mill_tuple
