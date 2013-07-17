## Timber Harvest Cost Model


### Overview

TODO overview of model for software developer audience

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

### Routing 
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

### Assumptions

#### Harvesting Systems

* Ground-Based Mech WT
CostFellBunch
CostManFLBLLT
CostSkidBun
CostProcess
CostChipWT
CostLoad

* Cable Manual WT
CostManFLBLLT2
CostManFellST2
CostProcess
CostChipWT
CostYardUB
CostLoad

* Helicopter Manual WT
CostHeliYardML
CostHeliLoadML
CostManFLBAc 
CostChipWTAc

# Ground-Based Manual WT
CostManFLBLLT2
CostManFellST2
CostSkidUB
CostProcess
CostChipWT
CostLoad


