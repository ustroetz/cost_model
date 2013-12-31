import math
import skidding
import hauling
import harvesting


# func for every stand per property
def cost_func(Area, Elevation, Slope, stand_wkt, RemovalsCT, TreeVolCT,
              RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT,
              HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT,
              PartialCut, landing_coords, haulDist, haulTime, coord_mill, NoHelicopter = False, NoHaulProportion = 1):

    #############################################
    # Skid Distance, Haul Distance Extension    #
    #############################################
    SkidDist, HaulDistExtension, coord_landing_stand = skidding.skidding(stand_wkt, landing_coords, Slope)
    HaulDistExtension = round(HaulDistExtension*0.000189394, 3)  # convert to miles 

    #############################################
    # Harvest Cost                              #
    #############################################
    harvest_result = harvesting.harvestcost(PartialCut, Slope, SkidDist, Elevation, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, NoHelicopter,NoHaulProportion)
    harvestCost, HarvestSystem = harvest_result  # returns harvest cost per CCF and Harvesting System

    totalVolumePerAcre = TreeVolSLT*RemovalsSLT+RemovalsLLT*TreeVolLLT+RemovalsCT*TreeVolCT
    totalVolume = Area*totalVolumePerAcre  # total removal volume in ft3
    totalHarvestCost = round(harvestCost*totalVolume)  # total harvest costs for stand

    #############################################
    # Hauling Cost                              #
    #############################################
    haulTimeRT = 0.0
    haulCost = 0.0
    truckVol = 0.0
    trips = 0.0
    totalHaulCost = 0.0

    if haulDist > 0.00001:
        haulDist = haulDist + HaulDistExtension  # in miles
        haulDist = round(haulDist, 2)
        if HaulDistExtension > 0:
            haulTimeRT = haulTime*2.0+HaulDistExtension*2.0/(30*60.0)  # round trip time plus travel time on extension
        else:
            haulTimeRT = haulTime*2.0  # round trip time
        haulCost = hauling.haulcost(haulDist, haulTimeRT)  # returns haul cost per minute

        # stinger-steer log truck avg volume per load (7 CCF small timber to 10 CCF large timber)
        if totalVolumePerAcre > 0.0:
            percentageCT = (TreeVolCT*RemovalsCT)/totalVolumePerAcre 
            percentageSLT = (TreeVolSLT*RemovalsSLT)/totalVolumePerAcre
            percentageLLT = (TreeVolLLT*RemovalsLLT)/totalVolumePerAcre 
            truckVol = percentageCT*700+percentageSLT*850+percentageLLT*1000
            trips = math.ceil(total50Volume/truckVol)  # necessary total trips to mill
            totalHaulCost = round(haulTimeRT*haulCost*trips*NoHaulProportion)  # total costs for all trips

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
        'landing_coordinates': coord_landing_stand,
        'total_cost': totalCost
    }

    return results
