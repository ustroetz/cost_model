import math, ogr, gis, skidding, routing, hauling, harvesting, landing

# func for every stand per property
def stand_func(haul_mc_wb, harvest_mc_wb, slope_raster, elevation_raster, property_lyr, FID, landing_geom, PartialCut, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, haulDist, haulTime):
    
    #############################################
    # Area, Slope, Elevation                    #
    #############################################

    Area = gis.area(property_lyr, FID)
    Elevation = 500.0
    Slope = 30.0
#   Elevation = gis.zonal_stats(elevation_raster, property_lyr, FID)
#   Slope = gis.zonal_stats(slope_raster, property_lyr, FID)
	


    #############################################
    # Skid Distance, Haul Distance Extension    #
    #############################################

    SkidDist, HaulDistExtension = skidding.skidding(property_lyr, FID, landing_geom)
    HaulDistExtension = round(HaulDistExtension*0.000189394, 3) # convert to miles

    #############################################
    # Harvest Cost                              #
    #############################################
    
    harvest_result = harvesting.harvestcost(harvest_mc_wb, PartialCut, Slope, SkidDist, Elevation, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT)  # returns harvest cost per CCF and Harvesting System
    harvestCost, HarvestSystem = harvest_result
    
    totalVolume = Area*(TreeVolSLT*RemovalsSLT+RemovalsLLT*TreeVolLLT+RemovalsCT*TreeVolCT)/100 # total removal volume in ft3
    totalHarvestCost = round(harvestCost*totalVolume) # total harvest costs for stand


    #############################################
    # Hauling Cost                              #
    #############################################

    if haulDist > 0:
        haulDist = haulDist + HaulDistExtension # in miles
        haulDist = round(haulDist, 2)
        if HaulDistExtension > 0:
            haulTimeRT = haulTime*2.0+65.0+HaulDistExtension*2.0/(30*60.0) # round trip time plus standing time plus travel time on extension
        else:        
            haulTimeRT = haulTime*2.0+65.0 # round trip time plus standing time 
        haulCost = hauling.haulcost(haul_mc_wb, haulDist, haulTimeRT)  # returns haul cost per minute
        truckVol = 8.0 # CCF per truck load
        trips = math.ceil(totalVolume/100.0/truckVol) # necessary total trips to mill
        totalHaulCost = round(haulTimeRT*haulCost*trips) # total costs for all trips
    else:
        haulTimeRT = 0.0
        haulCost = 0.0
        truckVol = 0.0
        trips = 0.0
        totalHaulCost = 0.0


    #############################################
    # Total Costs                               #
    #############################################

    totalCost = totalHaulCost+totalHarvestCost

    results = {'total_area':(round(Area,2)),'slope':(round(Slope,2)),'elevation':(round(Elevation,2)),'total_volume':(round(totalVolume,2)),
               'skid_distance':SkidDist, 'harvest_system':(HarvestSystem),'harvest_cost_ft3':harvestCost,'total_harvest_cost':totalHarvestCost,
               'haul_distance_extension':HaulDistExtension, 'haul_distance_ow':haulDist, 'haul_time_ow':haulTime, 'total_haul_trips':trips,' haul_cost_min':haulCost,'total_haul_cost':totalHaulCost,
               'total_cost':totalCost}
    
    return results




# function for total property
def cost_func(haul_mc_wb, harvest_mc_wb, slope_raster, elevation_raster, property_lyr, mill_lyr, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, millID = None, mill_Lat = None, mill_Lon = None, PartialCut = 0):

    results = {}
    
    #############################################
    # Landing Coordinates                       #
    #############################################
    landing_geom = landing.landing(property_lyr)
    landing_lon = landing_geom.GetX()
    landing_lat = landing_geom.GetY()
    results['landing_coordinates'] = str(landing_lat)+','+str(landing_lon)


    #############################################
    # Mill Coordinates, Haul Distance & Time    #
    #############################################
    
    haulDist, haulTime, coord_mill = routing.routing(landing_geom, millID, mill_Lat, mill_Lon, mill_lyr)  # returns one way haul distance in miles and time in minutes
    if haulDist > 0:
        haulTime = round(haulTime, 2)
    else:
        haulTime = 0.0

    results['mill_coordinates'] = str(coord_mill)

    
    #############################################
    # Stand Loop                                #
    #############################################
    
    numFeatures = property_lyr.GetFeatureCount()
    FID = 0
    while FID < numFeatures:
        for key, val in stand_func(haul_mc_wb, harvest_mc_wb, slope_raster, elevation_raster, property_lyr, FID, landing_geom, PartialCut, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, haulDist, haulTime).items():
            results.setdefault(key, []).append(val)
        FID += 1


    #############################################    
    return results

