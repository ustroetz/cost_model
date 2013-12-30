# determines the distance and time from the landing to the mill
import requests
import json
from osgeo import ogr
import os
import tempfile


def routing(landing_coords, mill_coords=None, mill_shp=None, mill_filter=None):

    if not (mill_coords or mill_shp):
        raise Exception("Either mill_coords or mill_shp is required")

    # create landing coordinate string
    coord_landing = '%f,%f' % (landing_coords[1], landing_coords[0])

    if mill_shp:
        driver = ogr.GetDriverByName('ESRI Shapefile')
        mill_ds = driver.Open(mill_shp, 0)
        mill_lyr = mill_ds.GetLayer()
    else:
        mill_lyr = None

    def get_point():
        # get mill coordinates
        # TODO unnecessary to use geom and string, instead use tuple for point
        mill_geom = millfeat.GetGeometryRef()
        mill_Lon = mill_geom.GetX()
        mill_Lat = mill_geom.GetY()
        coord_mill = '%f,%f' % (mill_Lat, mill_Lon)
        return coord_mill

    def routing_request(coord_landing, coord_mill):
        try:
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
            total_distance = total_summary['total_distance']  # in meters
            total_time = total_summary['total_time']  # in sec
        except:
            print "ERROR: Routing request failed. Haul cost will be $0"
            total_distance = 0.00001 # can not be exactly zero because of distdict min
            total_time = 0.00001
            
        return total_distance, total_time

    # determine mill and run routing
    if mill_coords:
        coord_mill = '%f,%f' % (mill_coords[1], mill_coords[0])
        total_distance, total_time = routing_request(coord_landing, coord_mill)
        total_distance = total_distance*0.000621371  # convert to miles
        total_time = total_time/60.0  # convert to min
    elif mill_lyr:
        need_bbox_expansion = True
        if mill_filter:
            mill_lyr.SetAttributeFilter(mill_filter)
            fcount = mill_lyr.GetFeatureCount()
            if fcount == 0:
                raise Exception("No features matching attribute filter `%s`" % mill_filter)
            elif fcount < 5:
                # only a few, no need to do a spatial filter as well
                need_bbox_expansion = False

        # set spatial filter around landing to include only close by mills
        offset = 0.02
        fcount = 0
        while fcount < 3 and need_bbox_expansion:  # require at least X mills in the bbox
            offset *= 2  # exponentially grow the bbox

            dfMinX = landing_coords[0] - offset
            dfMaxX = landing_coords[0] + offset
            dfMinY = landing_coords[1] - offset
            dfMaxY = landing_coords[1] + offset

            mill_lyr.SetSpatialFilterRect(dfMinX, dfMinY, dfMaxX, dfMaxY)
            fcount = mill_lyr.GetFeatureCount()

        distDict = {}
        timeDict = {}

        millfeat = mill_lyr.GetNextFeature()
        while millfeat:
            coord_mill = get_point()

            total_distance, total_time = routing_request(coord_landing, coord_mill)

            distDict[coord_mill] = total_distance
            timeDict[coord_mill] = total_time

            millfeat.Destroy()
            millfeat = mill_lyr.GetNextFeature()

        # Remove items from Dictionary where distance is 0, mill not on road
        distDict = {key: value for key, value in distDict.items()
                    if value > 0}

        # get distance and time to closest mill
        coord_mill = min(distDict, key=distDict.get)
        total_distance = distDict[coord_mill]*0.000621371  # convert to miles
        total_time = timeDict[coord_mill]/60.0  # convert to min

    coord_mill_tuple = tuple([float(x) for x in reversed(coord_mill.split(","))])

    if total_time > 0:
        total_time = round(total_time, 2)
    else:
        total_time = 0.0

    try:
        mill_ds.Destroy()  # clean up after ogr
    except UnboundLocalError:
        pass

    return total_distance, total_time, coord_mill_tuple
