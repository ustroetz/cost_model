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
    HdwdFractionCT,             # Proportion of hardwood chip trees 
    HdwdFractionSLT,            # Proportion of hardwood small log trees
    HdwdFractionLLT,            # Proportion of hardwood large log trees
    PartialCut,                 # Regen/Clearcut = 0, Thin = 1

    # routing info
    landing_coords,             # coordinate of landing ((lon, lat) tuple)
    haulDist,                   # distance to mill (miles)
    haulTime,                   # transit time to mill (hours?)
    coord_mill                  # coordinate of mill ((lon, lat) tuple) 
)
```

### Outputs

```
{
 'elevation': 505.09,
 'harvest_cost_ft3': 0.5092,
 'harvest_system': 'GroundBasedMechWT',
 'haul_cost_min': 0.7604,
 'haul_distance_extension': 1.051,
 'haul_distance_ow': 31.24,
 'haul_time_ow': 56.7,
 'landing_coordinates': (42.791597377229024, -124.34608736173503),
 'mill_coordinates': (43.119, -124.4075),
 'skid_distance': 825.23,
 'slope': 22.91,
 'total_area': 8.52,
 'total_cost': 9628.0,
 'total_harvest_cost': 7990.0,
 'total_haul_cost': 1638.0,
 'total_haul_trips': 19.0,
 'total_volume': 15692.23
}
```

### Assumptions

TODO