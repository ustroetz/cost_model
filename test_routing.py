from forestcost import routing as r


def test_routing_mill_shp():
    mill_shp = 'Data//mills.shp'

    # Landing Coordinates
    landing_coords = (-118.620, 44.911)

    haulDist, haulTime, coord_mill = r.routing(
        landing_coords,
        mill_shp=mill_shp
    )

    print "Using shapefile to find nearest mill..."
    print "Distance:", haulDist
    print "Time:", haulTime
    print "Landing coordinate:", landing_coords
    print "Mill coordinate:", coord_mill
    print


def test_routing_mill_filter():
    mill_shp = 'Data//mills.shp'
    mill_filter = "CITY = 'John Day'"

    # Landing Coordinates
    landing_coords = (-118.620, 44.911)

    haulDist, haulTime, coord_mill = r.routing(
        landing_coords,
        mill_shp=mill_shp,
        mill_filter=mill_filter,
    )

    print "Using shapefile filtered for `%s`..." % mill_filter
    print "Distance:", haulDist
    print "Time:", haulTime
    print "Landing coordinate:", landing_coords
    print "Mill coordinate:", coord_mill
    print


def test_routing_mill_coords():
    mill_coords = (-119.250013, 44.429948)

    # Landing Coordinates
    landing_coords = (-118.620, 44.911)

    haulDist, haulTime, coord_mill = r.routing(
        landing_coords,
        mill_coords=mill_coords,
    )

    print "Using specified mill coordinates"
    print "Distance:", haulDist
    print "Time:", haulTime
    print "Landing coordinate:", landing_coords
    print "Mill coordinate:", coord_mill
    print


if __name__ == "__main__":
    print
    test_routing_mill_shp()
    test_routing_mill_coords()
    test_routing_mill_filter()
