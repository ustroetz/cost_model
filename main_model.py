import math, ogr, gis, skidding, routing, hauling, harvesting

def cost_model():
    #############################################
    # Input                                     #
    #############################################

    PartialCut = 0

    ### GIS Data ###
    stand = 'U:\\My Documents\Tool\\Data\\testarea1.shp'
    Area = gis.gis(stand)
    Elevation = 1000.0
    Slope = 20.0


    ### Tree Data ###
    # Chip Trees
    RemovalsCT = 0.0
    TreeVolCT = 0.0

    # Small Log Trees
    RemovalsSLT = 100.0
    TreeVolSLT = 50.0

    # Large Log Trees
    RemovalsLLT = 10.0
    TreeVolLLT = 80.0

    totalVolume = Area*(TreeVolSLT*RemovalsSLT+RemovalsLLT*TreeVolLLT+RemovalsCT*TreeVolCT)/100 # total removal volume in ft3




    #############################################
    # Skidding Distance & Landing Coordinates   #
    #############################################

    skid_results = skidding.skidding(stand) # returns YardDist in feet and Landing Coordinates

    coord_landing_lat = skid_results[1][0]
    coord_landing_lon = skid_results[1][1]
    SkidDist = skid_results[0]



    #############################################
    # Harvest Costs                             #
    #############################################
    harvest_result = harvesting.harvestcost(PartialCut, Slope, SkidDist, Elevation, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT)  # returns harvest cost per CCF and Harvesting System
    harvestCost, HarvestSystem = harvest_result

    totalHarvestCost = round(harvestCost*totalVolume) # total harvest costs for stand




    #############################################
    # Routing Distance & Time                   #
    #############################################

    routing_result = routing.routing(coord_landing_lat, coord_landing_lon)  # returns one way haul distance in miles and time in minutes
    haulDist, haulTime = routing_result
    haulDist = round(haulDist, 2)
    haulTime = round(haulTime, 2)




    ############################################
    # Haul Cost                                #
    ############################################

    haulTimeRT = haulTime*2.0+65.0 # round trip time plus standing time

    haulCost = hauling.haulcost(haulDist, haulTimeRT)  # returns haul cost per minute

    truckVol = 8.0 # CCF per truck load
    trips = math.ceil(totalVolume/100/truckVol) # necessary total trips to mill
    totalHaulCost = round(haulTimeRT*haulCost*trips) # total costs for all trips




    ############################################
    # SUMMARY                                  #
    ############################################

    totalCost = totalHaulCost+totalHarvestCost

    results = {'total_area':(round(Area,2)),'total_volume':(round(totalVolume,2)),
           'skid_distance':SkidDist, 'harvest_system':(HarvestSystem),'harvest_cost_ft3':harvestCost,'total_harvest_cost':totalHarvestCost,
           'haul_distance_ow':haulDist, 'haul_time_ow':haulTime, 'total_haul_trips':trips,' haul_cost_min':haulCost,'total_haul_cost':totalHaulCost,
           'total_cost':totalCost}
    
    return results

    print "######################################"
    print "Stand Characteristics"
    print "Total Area: " + str(round(Area,2)) + " ac\nTotal Volume: " + str(round(totalVolume,2)) + " ft3\n\n\n"


    print "######################################"
    print "Harvest"
    print "Skid Distance: " + str(SkidDist) + " ft \nHarvest System: " + str(HarvestSystem) + \
    "\nHarvest Cost: " + str(harvestCost) + " $/ft3\nTotal Harvest Cost: " + str(totalHarvestCost) + " $\n\n\n"

    print "######################################"
    print "Transportation"
    print "One-way Haul Distance: " + str (haulDist) + " mi\nOne-way Haul Time: " + str(haulTime) + " min\nTotal haul trips: " + str(trips) + \
    "\nHaul Cost per minute: " + str(haulCost) + " $ \nTotal Haul Cost: " + str(totalHaulCost) + " $\n\n\n"

    print "######################################"
    print "Total Cost to harvest stand: " + str(totalCost) + " $\n\n\n"
