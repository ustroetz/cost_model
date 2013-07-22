## Timber Harvest Cost Model


### Overview

The Timber Harvest Cost Model estimates total delivered costs (US dollar) from the stumpage to the mill gate for a timber stand.
The two main components of the model are the harvest cost (US Dollar/cubic foot) and the hauling cost (US Dollar/minute) which are estimated by the model. 
Harvest cost (US Dollar/cubic foot) is multipled by the total volume (cubic foot) of the stand. 
Hauling cost (US Dollar/minute) is multiplied by the total hauling time (minutes) from the landing to the mill gate and by the total necessary hauling trips. 
Both together result in the total delivered cost (US Dollar).

######  Costs not included
* Harvest equipment move-in costs
* Road construction costs
* Management costs
* Reforestation costs

### Installation

Requires `xlrd`, `python-gdal`, `json`, `requests`, and `numpy`

To install, simply `python setup.py install` or work directly from the root directory

## Modules

#### [Main Model] (forestcost/main_model.py)
The Main Model defines the cost function which is the primary interface; given information about stand attributes, harvest 
and routing, the cost function will estimate harvest and transportation costs. 

###### Inputs
```
from forestcost import main_model
main_model.cost_func(

    # stand info
    area,                       # Stand area (acres)
    elevation,                  # Elevation (ft)
    slope,                      # Slope (%)
    stand_wkt,                  # Well-Known Text geometry of stand polygon

    # harvest info
    RemovalsCT,                 # Chip trees removed (trees per acre)
    TreeVolCT,                  # Chip tree average volume (cubic feet)
    RemovalsSLT,                # Small log trees removed (trees per acre)
    TreeVolSLT,                 # Small log average volume (cubic feet) 
    RemovalsLLT,                # Large log trees removed (trees per acre)
    TreeVolLLT,                 # Large log average volume (cubic feet)
    HdwdFractionCT,             # Proportion of hardwood chip trees (volume of hardwood divided by total volume)
    HdwdFractionSLT,            # Proportion of hardwood small log trees (volume of hardwood divided by total volume)
    HdwdFractionLLT,            # Proportion of hardwood large log trees (volume of hardwood divided by total volume)
    PartialCut,                 # Regen/Clearcut = 0, Thin = 1

    # routing info
    landing_coords,             # coordinate of landing ((lon, lat) tuple)
    haulDist,                   # distance to mill (miles)
    haulTime,                   # transit time to mill (minutes)
    coord_mill                  # coordinate of mill ((lon, lat) tuple) 
)
```

###### Outputs

```
{
 'elevation': 505.09,                    # feet
 'harvest_cost_ft3': 0.5092,             # US dollars/cubic feet
 'harvest_system': 'GroundBasedMechWT',  # harvest method
 'haul_cost_min': 0.7604,                # US dollars/minute
 'haul_distance_extension': 1.051,       # miles from stand landing to road
 'haul_distance_ow': 31.24,              # miles
 'haul_time_ow': 56.7,                   # minutes
 'landing_coordinates': (42.7, -124.3),  # lon, lat
 'mill_coordinates': (43.11, -124.407),  # lon, lat
 'skid_distance': 825.23,                # feet
 'slope': 22.91,                         # percent
 'total_area': 8.52,                     # acres
 'total_cost': 9628.0,                   # US dollars
 'total_harvest_cost': 7990.0,           # US dollars
 'total_haul_cost': 1638.0,              # US dollars
 'total_haul_trips': 19.0,               # number of trips
 'total_volume': 15692.23                # cubic feet
}
```

###### Individual Parts

* Skid Distance and Haul Distance Extension  
Skidding distance (feet), hauling distance extension (meter), and the landing coordiantes ((lon, lat (tuple)) are returned from [skidding](https://github.com/ustroetz/cost_model/blob/master/README.md#skidding). The hauling distance extension is converted from meters to miles.

* Harvest Cost  
Harvest cost (US dollars/cubic feet) and the name of the selected harvest system is returned from [harvesting](https://github.com/ustroetz/cost_model/blob/master/README.md#harvesting).
`totalHarvestCost = harvestCost*totalVolume # US dollar`

* Hauling Cost  
Haul cost (US dollars/minute) is returned from [hauling](https://github.com/ustroetz/cost_model/blob/master/README.md#hauling).  
`haulDist = haulDist + HaulDistExtension    # miles`  
`haulTimeRoundTrip = haulTime*2.0+HaulDistExtension*2.0/(30*60.0)   # minutes`  
&nbsp;&nbsp;&nbsp;&nbsp;30 mph on hauling distance extension
`truckVol = percentageChipTrees*700+percentageSmallLogTrees*850+percentageLargeLogTrees*1000    # cubic feet`  
&nbsp;&nbsp;&nbsp;&nbsp;standard stinger-steer log truck: 700 cubic feet small timber to 1000 cubic feet large timber
`trips = totalVolume/truckVol   # adjusted upward`  
`totalHaulCost = haulTimeRoundTrip*haulCost*trips   # US dollar`

* Total Costs  
`totalCost = totalHaulCost + totalHarvestCost   # US dollar`

#### [Harvesting] (forestcost/harvesting.py)
Harvesting calculates the costs for four harvesting systems and returns the price (US dollar/cubic feet) and name of the least expensive one. 
If no harvesting system is suitable due to limitations of the systems `Price = NaN` and `HarvestingSystem = 'NoSystem'` is returned.

Harvesting is based on the Fuel Reduction Cost Simulator [(FRCS-West)] (http://www.fs.fed.us/pnw/data/frcs/frcs.shtml) from the USDA.

Machine costs and labor costs are stored in [harvest_cost.xls] (forestcost/harvest_cost.xls).

###### Inputs
```
from forestcost import harvesting
harvesting.harvestcost(

    RemovalsCT,                 # Chip trees removed (trees per acre)
    TreeVolCT,                  # Chip tree average volume (cubic feet)
    RemovalsSLT,                # Small log trees removed (trees per acre)
    TreeVolSLT,                 # Small log average volume (cubic feet) 
    RemovalsLLT,                # Large log trees removed (trees per acre)
    TreeVolLLT,                 # Large log average volume (cubic feet)
    HdwdFractionCT,             # Proportion of hardwood chip trees (volume of hardwood divided by total volume)
    HdwdFractionSLT,            # Proportion of hardwood small log trees (volume of hardwood divided by total volume)
    HdwdFractionLLT,            # Proportion of hardwood large log trees (volume of hardwood divided by total volume)
    PartialCut,                 # Regen/Clearcut = 0, Thin = 1
)
```

###### Outputs 
```
    Price,                      # US dollars/cubic feet
    HarvestingSystem,           # name of harvest method
```    

###### Harvest methods, individual costs, and limitations:

* Ground-Based Manual Whole Tree =  trees are felled with chainsaws but are not limbed or bucked. Rubber-tired skidders (choker and grapple) collect and transport whole trees. Trees are chipped or processed mechanically with stroke or single-grip processors and loaded onto trucks.
`GroundBasedManualWT = CostManFLBLLT2 + CostManFellST2 + CostSkidUB + CostProcess + CostChipWT + CostLoad`

 System limits: `Slope<40 and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<500 and TreeVolALT<500 and TreeVol<500`


* Ground-Based Mech Whole Tree = trees are felled and bunched; drive-to-tree machines are assumed for flat ground, whereas swingboom and self-leveling versions are included for steeper terrain. Rubber-tired grapple skidders transport bunches to the landing. Trees are chipped or processed mechanically with stroke or single-grip processors and loaded onto trucks.
`GroundBasedMechWT = CostFellBunch+CostManFLBLLT+CostSkidBun+CostProcess+CostChipWT+CostLoad`

 System limits: `Slope<40  and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<250 and TreeVolALT<250 and TreeVol<250`


* Cable Manual Whole Tree = trees are felled with chainsaws, but are not limbed or bucked. (Trees too large to be yarded in one piece or too large to be mechanically processed at the landing are limbed and bucked in the woods.) Cable yarders transport the trees to the landing for chipping or mechanical processing and loading onto trucks.
`CableManualWT = CostManFLBLLT2 + CostManFellST2 + CostYardUB + CostProcess + CostChipWT + CostLoad`

 System limits: `SkidDist<1300 and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<500 and TreeVolALT<500 and TreeVol<500`


* Helicopter Manual Whole Tree = trees are felled with chainsaws, and are limbed, and bucked at the stump. The helicopters then transport the logs out of the stand. Logs to be hauled in log form are loaded onto trucks, and those to be chipped are processed through a disk chipper and blown into chip vans.
`HelicopterManualWT = CostManFLB + CostHeliYardML +  CostChipWT + CostHeliLoadML`

 System limits: `TreeVolCT<80 and TreeVolALT<250 and SkidDist<10000 and TreeVol<250 and TreeVolLLT<150`

#### [Hauling] (forestcost/hauling.py)
Hauling returns the cost (US dollar/min) to operate a standard stinger-steer log truck (18 tires). 

Harvesting is based on the [Log Truck Haul Cost] (http://www.fs.usda.gov/detail/r6/landmanagement/resourcemanagement/?cid=fsbdev2_027048) from the USDA.

Machine costs and labor costs are stored in [haul_cost.xls] (forestcost/haul_cost.xls).

###### Inputs
```
from forestcost import hauling
hauling.haulcost(

    TravelDistanceOneWay,       # One way distance from landing to the mill (miles)
    TimeRoundTrip,              # Round trip time from landing to the mill and back (minutes)
)
```

###### Outputs 
```
    AverageCPmin                # Average owning, operating, and labor cost for log truck (US dollars/ minutes)
```    


#### [Skidding] (forestcost/skidding.py)
Skidding returns the skidding distance from the centroid of the stand to the stand landing, the coordinates of the stand landing, and the distance from the stand landing to the road landing.

1. A straight line from the centroid of the stand to the road landing is created.
2. Where the line intersects with the stand is the stand landing.
3. Distance from the centroid to the stand landing is the skidding distance and distance from the stand landing to the road landing is the haul distance extension and considered as road.
4. Skidding distance limit is 1,300 feet (additional skidding distance is added to haul distance extension). If skidding distance > 1,300 and slope > 40 than the limit is 10,000 feet (helicopter logging).
  
<p align="center">
  <img src="http://s10.postimg.org/6dwy8f0h5/Capture.png" />
</p>

###### Inputs
```
from forestcost import skidding
skidding.skidding(

    stand_wkt,                  # Well-Known Text geometry of stand polygon
    landing_coords,             # coordinate of road landing from landing.py 
    Slope                       # Slope (%)
)
```

###### Outputs 
```
    YardDist,                   # Skidding distance (feet)
    HaulDistExtension,          # Haul distance extension (feet)
    coord_landing_stand_tuple   # coordinate of stand landing ((lon, lat) tuple)
```  


#### [GIS] (forestcost/gis.py)
The area function returns the total area (acers) of the stand.

###### Inputs
```
from forestcost import gis
gis.area(

    lyr                         # OGR layer of stand
)
```

###### Outputs 
```
    area                        # area of stand (acres)
```    
The zonal statistics function returns the mean values of the slope and elevation raster within the zones of the stand. 
###### Inputs
```
from forestcost import gis
gis.zonal_stats(

    input_value_raster,         # Value raster of slope/elevation
    lyr                         # OGR layer of stand
)
```

###### Outputs 
```
    mean                        # Mean values of the slope/elevation raster within the zones of the stand
```    

#### [Landing] (forestcost/landing.py) (feeds into Main Model)
Landing returns the road landing coordinates on the closest road to the property (stand landing coordinates are determined with [skidding.py](https://github.com/ustroetz/cost_model/blob/master/README.md#skidding)).
    
1. Centroids of all stands are created
2. Centroid of all centroids is created (center of property)
3. OpenStreetMap with [OSRM Routing API] (https://github.com/DennisOSRM/Project-OSRM/wiki) is used to find the nearest point on a street which is the road landing. Only roads of OpenStreetMap are considered as roads.

###### Inputs
```
from forestcost import landing
landing.landing(

    lyr                          # OGR layer of property
)
```

###### Outputs 
```
    landing_coords               # coordinate of road landing ((lon, lat) tuple)
```     

#### [Routing] (forestcost/routing.py) (feeds into Main Model)
Routing returns the one-way distance and time from the road landing to the mill and the coordinates of the selected mill.  
OpenStreetMap with [OSRM Routing API] (https://github.com/DennisOSRM/Project-OSRM/wiki) is used to determine the distance and time.  
  
Routing either automatically determines the closest mill by creating exponential expanding bounding boxes around the landing until at least three mills are found. 
If three mills are found the routes for each one are determined and the shortest one is selected.

###### Inputs
```
from forestcost import routing

mill_shp = 'Data//mills.shp'        # shapefile containing mill points
landing_coords = (-118.620, 44.911) # coordinates of road landing ((lon, lat) tuple)

routing.routing(
    landing_coords,
    mill_shp=mill_shp
)
```
Or the exact mill location can be specified.

```
mill_coords = (-119.250, 44.429)    # coordinates of selected mill ((lon, lat) tuple)
landing_coords = (-118.620, 44.911) # coordinates of road landing ((lon, lat) tuple)

routing.routing(
    landing_coords,
    mill_coords=mill_coords,
)
```

Additionally the mill shapefile can be filtered using OGR SQL queries

```
mill_shp = 'Data//mills.shp'        # shapefile containing mill points
landing_coords = (-118.620, 44.911) # coordinates of road landing ((lon, lat) tuple)
mill_filter = "CITY = 'John Day'"   # filter using OGR SQL query

routing.routing(
    landing_coords,
    mill_shp=mill_shp,
    mill_filter=mill_filter,
)
```
###### Outputs
```
total_distance,                     # one-way distance from road landing to mill (miles)
total_time,                         # one-way time from road landing to mill (minutes)
coord_mill_tuple                    # coordinates of selected mill ((lon, lat) tuple)
```

