## Timber Harvest Cost Model


### Overview

TODO overview of model for software developer audience

### Inputs

```
import main_model as m
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

### Assumptions

TODO