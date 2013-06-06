import math, ogr, gis, skidding, routing, hauling, harvesting, landing

def loop_func(slope_raster, elevation_raster, lyr, FID, landing_lat, landing_lon, PartialCut, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, haulDist, haulTime):
    
    #############################################
    # Area, Slope, Elevation                    #
    #############################################

    Area = gis.area(lyr, FID)
    Elevation = gis.zonal_stats(elevation_raster, lyr, FID)
    Slope = gis.zonal_stats(slope_raster, lyr, FID)


    #############################################
    # Skid Distance, Haul Distance Extension    #
    #############################################

    SkidDist, HaulDistExtension = skidding.skidding(lyr, FID, landing_lat, landing_lon)


    #############################################
    # Harvest Cost                              #
    #############################################
    
    harvest_result = harvesting.harvestcost(PartialCut, Slope, SkidDist, Elevation, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT)  # returns harvest cost per CCF and Harvesting System
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
        haulCost = hauling.haulcost(haulDist, haulTimeRT)  # returns haul cost per minute
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



def final(slope_raster, elevation_raster, lyr, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, millID = None, mill_Lat = None, mill_Lon = None, PartialCut = 0):

    #############################################
    # Landing Coordinates                       #
    #############################################
    landing_lat, landing_lon = landing.landing(lyr)


    #############################################
    # Mill Coordinates, Haul Distance & Time    #
    #############################################
    
    haulDist, haulTime, coord_mill = routing.routing(landing_lat, landing_lon, millID, mill_Lat, mill_Lon)  # returns one way haul distance in miles and time in minutes
    if haulDist > 0:
        haulTime = round(haulTime, 2)
    else:
        haulTime = 0.0

    
    #############################################
    # Stand Loop   #
    #############################################
    
    numFeatures = lyr.GetFeatureCount()
    results = {}
    FID = 0
    while FID < numFeatures:
        for key, val in loop_func(slope_raster, elevation_raster, lyr, FID, landing_lat, landing_lon, PartialCut, RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT, HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT, haulDist, haulTime).items():
            results.setdefault(key, []).append(val)
        FID += 1
    results['mill_coordinates'] = str(coord_mill)
    results['landing_coordinates'] = str(landing_lat)+','+str(landing_lon)
    return results

