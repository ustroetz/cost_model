## Timber Harvest Cost Model


### Overview

TODO overview of model for software developer audience

######  Costs not included
* Harvest equipment move-in costs
* Road construction costs
* Management costs
* Reforestation costs

### Installation

Requires `xlrd`, `python-gdal`, `json`, `requests`, and `numpy`. 

To install, simply `python setup.py install` or work directly from the root directory

### Inputs

The primary interface is the cost function; given information about stand attributes, harvest 
and mills, the cost function will estimate harvest and transportation costs. 
```
from forestcost import main_model
m.cost_func(

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

### Outputs

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
## Modules
#### [Harvesting] (forestcost/harvesting.py)
Harvesting calculates the costs for four harvesting systems and returns the `Price` (US dollar/cubic feet) and `HarvestingSystem` (name) for the least expensive one. 
If no harvesting system is suitable due to limitations of the systems `Price = NaN` and `HarvestingSystem = 'NoSystem'` is returned.

Harvesting is based on the Fuel Reduction Cost Simulator [(FRCS-West)] (http://www.fs.fed.us/pnw/data/frcs/frcs.shtml) from the USDA.

Machine costs and labor costs are stored in [harvest_cost.xls] (forestcost/harvest_cost.xls).

###### Inputs
```
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
```

###### Outputs 
```
    Price,                      # US dollars/cubic feet
    HarvestingSystem,           # name of harvest method
```    

###### Harvest methods, individual costs, and limitations:

* Ground-Based Manual Whole Tree =  trees are felled with chainsaws but not limbed or bucked. Rubber-tired skidders (choker and grapple) collect and transport whole trees. Trees are chipped or processed mechanically with stroke or single-grip processors and loaded onto trucks.
`GroundBasedManualWT = CostManFLBLLT2 + CostManFellST2 + CostSkidUB + CostProcess + CostChipWT + CostLoad`

 System limits: `Slope<40 and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<500 and TreeVolALT<500 and TreeVol<500`


* Ground-Based Mech Whole Tree = trees are felled and bunched; drive-to-tree machines are assumed for flat ground, whereas swingboom and self-leveling versions are included for steeper terrain. Rubber-tired grapple skidders transport bunches to the landing. Trees are chipped or processed mechanically with stroke or single-grip processors and loaded onto trucks.
`GroundBasedMechWT = CostFellBunch+CostManFLBLLT+CostSkidBun+CostProcess+CostChipWT+CostLoad`

 System limits: `Slope<40  and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<250 and TreeVolALT<250 and TreeVol<250`


* Cable Manual Whole Tree = trees are felled with chainsaws, but not limbed or bucked. (Trees too large to be yarded in one piece or too large to be mechanically processed at the landing are limbed and bucked in the woods.) Cable yarders transport the trees to the landing for chipping or mechanical processing and loading onto trucks.
`CableManualWT = CostManFLBLLT2 + CostManFellST2 + CostYardUB + CostProcess + CostChipWT + CostLoad`

 System limits: `SkidDist<1300 and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<500 and TreeVolALT<500 and TreeVol<500`


* Helicopter Manual Whole Tree = trees are felled with chainsaws, limbed, and bucked at the stump. The helicopters then transport the logs out of the stand. Logs to be hauled in log form are loaded onto trucks, and those to be chipped are processed through a disk chipper and blown into chip vans.
`HelicopterManualWT = CostManFLB + CostHeliYardML +  CostChipWT + CostHeliLoadML`

 System limits: `TreeVolCT<80 and TreeVolALT<250 and SkidDist<10000 and TreeVol<250 and TreeVolLLT<150`

#### [Hauling] (forestcost/hauling.py)
Hauling calculates and returns the price `AverageCPmin` (US dollar/min) to operate a standard stinger-steer log truck (18 tires). 

Harvesting is based on the [Log Truck Haul Cost] (http://www.fs.usda.gov/detail/r6/landmanagement/resourcemanagement/?cid=fsbdev2_027048) from the USDA.

Machine costs and labor costs are stored in [haul_cost.xls] (forestcost/haul_cost.xls).

###### Inputs
```
    TravelDistanceOneWay,       # One way distance from landing to the mill (miles)
    TimeRoundTrip,              # Round trip time from landing to the mill and back (minutes)
```

###### Outputs 
```
    AverageCPmin                # Average owning, operating, and labor cost for log truck (US dollars/ minutes)
```    

#### [GIS] (forestcost/gis.py)
GIS includes the functions `area` and `zonal_stats`.

##### Area
`area` returns the total area (acers) of the stand.

###### Inputs
```
    lyr                         # OGR layer of stand
```

###### Outputs 
```
    area                        # area of stand (acres)
```    
##### Zonal statistics
`zonal_stats` returns the mean values of the slope and elevation raster within the zones of the stand. 
###### Inputs
```
    input_value_raster,         # Value raster of slope/elevation
    lyr                         # OGR layer of stand
```

###### Outputs 
```
    mean                        # Mean values of the slope/elevation raster within the zones of the stand
```    

#### [Landing] (forestcost/landing.py)
TODO

#### [Skidding] (forestcost/skidding.py)
TODO

#### [Routing] (forestcost/routing.py)
The routing information can be determined by selecting the closest mill from a
shapefile

```
from forestcost import routing

mill_shp = 'Data//mills.shp'
landing_coords = (-118.620, 44.911)

haul_distance, haul_time, coord_mill = r.routing(
    landing_coords,
    mill_shp=mill_shp
)
```

or by specifying the exact location of the mill

```
mill_coords = (-119.250013, 44.429948)
landing_coords = (-118.620, 44.911)

haul_distance, haul_time, coord_mill = r.routing(
    landing_coords,
    mill_coords=mill_coords,
)
```

additionally you can filter the mill shapefile using OGR SQL queries

```
mill_filter = "CITY = 'John Day'"

haul_distance, haul_time, coord_mill = r.routing(
    landing_coords,
    mill_shp=mill_shp,
    mill_filter=mill_filter,
)
```

#### [Main Model] (forestcost/main_model.py)
TODO

## License
TODO

