import routing as r


def routing(landing_coords, millID, mill_Lat, mill_Lon, mill_lyr):

    #############################################
    # Mill Coordinates, Haul Distance & Time    #
    #############################################
    haulDist, haulTime, coord_mill = r.routing(landing_coords, millID, mill_Lat, mill_Lon, mill_lyr)  # returns one way haul distance in miles and time in minutes
    if haulDist > 0:
        haulTime = round(haulTime, 2)
    else:
        haulTime = 0.0

    return haulDist, haulTime, coord_mill
