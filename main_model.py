import math
import skidding
import routing
import hauling
import harvesting
import landing


# func for every stand per property
def cost_func(Area, Elevation, Slope, stand_wkt, RemovalsCT, TreeVolCT,
              RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT,
              HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT,
              PartialCut, landing_coords, haulDist, haulTime, coord_mill):

    #############################################
    # Skid Distance, Haul Distance Extension    #
    #############################################

    SkidDist, HaulDistExtension, landing_stand_geom = skidding.skidding(stand_wkt, landing_coords, Slope)
    HaulDistExtension = round(HaulDistExtension*0.000189394, 3)  # convert to miles
    landing_lat, landing_lon = landing_stand_geom.GetX(), landing_stand_geom.GetY()

    #############################################
    # Harvest Cost                              #
    #############################################
    harvest_result = harvesting.harvestcost(PartialCut, Slope, SkidDist, Elevation, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT)
    harvestCost, HarvestSystem = harvest_result  # returns harvest cost per CCF and Harvesting System

    totalVolume = Area*(TreeVolSLT*RemovalsSLT+RemovalsLLT*TreeVolLLT+RemovalsCT*TreeVolCT)/100.0  # total removal volume in ft3
    totalHarvestCost = round(harvestCost*totalVolume)  # total harvest costs for stand

    #############################################
    # Hauling Cost                              #
    #############################################
    if haulDist > 0:
        haulDist = haulDist + HaulDistExtension  # in miles
        haulDist = round(haulDist, 2)
        if HaulDistExtension > 0:
            haulTimeRT = haulTime*2.0+HaulDistExtension*2.0/(30*60.0)  # round trip time plus travel time on extension
        else:
            haulTimeRT = haulTime*2.0  # round trip time
        haulCost = hauling.haulcost(haulDist, haulTimeRT)  # returns haul cost per minute
        truckVol = 8.0  # CCF per truck load
        trips = math.ceil(totalVolume/100.0/truckVol)  # necessary total trips to mill
        totalHaulCost = round(haulTimeRT*haulCost*trips)  # total costs for all trips
    else:
        haulTimeRT = 0.0
        haulCost = 0.0
        truckVol = 0.0
        trips = 0.0
        totalHaulCost = 0.0

    #############################################
    # Total Costs                               #
    #############################################
    totalCost = totalHaulCost + totalHarvestCost

    results = {
        'total_area': (round(Area, 2)),
        'slope': (round(Slope, 2)),
        'elevation': (round(Elevation, 2)),
        'total_volume': (round(totalVolume, 2)),
        'skid_distance': SkidDist,
        'harvest_system': (HarvestSystem),
        'harvest_cost_ft3': harvestCost,
        'total_harvest_cost': totalHarvestCost,
        'haul_distance_extension': HaulDistExtension,
        'haul_distance_ow': haulDist,
        'haul_time_ow': haulTime,
        'total_haul_trips': trips,
        'haul_cost_min': haulCost,
        'total_haul_cost': totalHaulCost,
        'mill_coordinates': coord_mill,
        'landing_coordinates': (landing_lon, landing_lat),
        'total_cost': totalCost
    }

    return results
