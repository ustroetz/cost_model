# unit test suite for forestcost
# run 'py.test test_main_model.py'

from forestcost import landing
from forestcost import routing
from forestcost import main_model
from forestcost import skidding
from forestcost import harvesting
from forestcost import hauling
import ogr

driver = ogr.GetDriverByName('ESRI Shapefile')

def test_landing():
        # test landing: landing_coords

        # Input
        property_shp = driver.Open('testdata//test_stand.shp', 0)
        property_lyr = property_shp.GetLayer()

        # Expected Output
        landing_coords = (-124.04858, 43.12776)

        assert(landing.landing(property_lyr)) == landing_coords


def test_routing():
        # test routing: haulDist, haulTime, coord_mill

        # Input
        landing_coords = (-124.04858, 43.12776)
        mill_shp = 'testdata//mills.shp'    

        # Expected Output
        haulDist = 8.674960531 
        haulTime = 32.92 
        coord_mill = (-124.161246, 43.106512)
        
        assert(routing.routing(landing_coords, mill_shp=mill_shp)) == (haulDist, haulTime, coord_mill)


def test_skidding():
        # test skidding: SkidDist, HauldistExtension, coord_landing_stand"

        # Input
        stand_wkt = u'POLYGON ((-13809080.891332019 5330620.9753014417,-13808943.708174769 5331066.8205624959,-13808393.373740762 5330897.4868904939,-13808530.556898013 5330451.6416294342,-13809080.891332019 5330620.9753014417))'
        landing_coords = (-124.04858, 43.12776) 
        Slope = 21.74728843

        # Expected Output
        SkidDist = 999.69
        HaulDistExtension = 1420.39
        coord_landing_stand = (-124.04706351844823, 43.125146208049415)
		
        assert(skidding.skidding(stand_wkt, landing_coords, Slope)) == (SkidDist, HaulDistExtension, coord_landing_stand)
		
		
def test_harvesting_GroundBasedMechWT():
        # test harvesting: harvestCost, HarvestSystem
        
        # Input
        PartialCut = 0 
        Slope = 30
        SkidDist = 1200
        Elevation = 100
        RemovalsCT = 200.0 
        TreeVolCT = 5.0 
        RemovalsSLT = 100.0 
        TreeVolSLT = 70.0 
        RemovalsLLT = 20.0 
        TreeVolLLT = 200.0 
        HdwdFractionCT = 0.15 
        HdwdFractionSLT = 0.0 
        HdwdFractionLLT = 0.0
        
        # Expected Output
        harvestCost = 0.4423
        HarvestSystem = 'GroundBasedMechWT'
        
        assert(harvesting.harvestcost(
                PartialCut, Slope, SkidDist, Elevation,
                RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT,
                HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT))== (harvestCost, HarvestSystem)


def test_harvesting_GroundBasedMechWT():
        # test harvesting: harvestCost, HarvestSystem
        
        # Input
        PartialCut = 1 
        Slope = 30
        SkidDist = 100
        Elevation = 100
        RemovalsCT = 200.0 
        TreeVolCT = 5.0 
        RemovalsSLT = 100.0 
        TreeVolSLT = 70.0 
        RemovalsLLT = 20.0 
        TreeVolLLT = 200.0 
        HdwdFractionCT = 0.15 
        HdwdFractionSLT = 0.0 
        HdwdFractionLLT = 0.0
        
        # Expected Output
        harvestCost = 0.3038
        HarvestSystem = 'GroundBasedMechWT'
        
        assert(harvesting.harvestcost(
                PartialCut, Slope, SkidDist, Elevation,
                RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT,
                HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT))== (harvestCost, HarvestSystem)

				
def test_harvesting_GroundBasedManualWT():
        # test harvesting: harvestCost, HarvestSystem
        
        # Input
        PartialCut = 0 
        Slope = 30
        SkidDist = 1200
        Elevation = 100
        RemovalsCT = 200.0 
        TreeVolCT = 5.0 
        RemovalsSLT = 100.0 
        TreeVolSLT = 70.0 
        RemovalsLLT = 20.0 
        TreeVolLLT = 300.0 
        HdwdFractionCT = 0.15 
        HdwdFractionSLT = 0.0 
        HdwdFractionLLT = 0.0
        
        # Expected Output
        harvestCost = 0.5358
        HarvestSystem = 'GroundBasedManualWT'
        
        assert(harvesting.harvestcost(
                PartialCut, Slope, SkidDist, Elevation,
                RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT,
                HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT))== (harvestCost, HarvestSystem)

				
def test_harvesting_CableManualWT():
        # test harvesting: harvestCost, HarvestSystem
        
        # Input
        PartialCut = 0 
        Slope = 60
        SkidDist = 1200
        Elevation = 100
        RemovalsCT = 200.0 
        TreeVolCT = 5.0 
        RemovalsSLT = 100.0 
        TreeVolSLT = 70.0 
        RemovalsLLT = 20.0 
        TreeVolLLT = 200.0 
        HdwdFractionCT = 0.15 
        HdwdFractionSLT = 0.0 
        HdwdFractionLLT = 0.0
        
        # Expected Output
        harvestCost = 0.7595
        HarvestSystem = 'CableManualWT'
        
        assert(harvesting.harvestcost(
                PartialCut, Slope, SkidDist, Elevation,
                RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT,
                HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT))== (harvestCost, HarvestSystem)


def test_harvesting_CableManualWT_PartialCut():
        # test harvesting: harvestCost, HarvestSystem
        
        # Input
        PartialCut = 1 
        Slope = 60
        SkidDist = 1200
        Elevation = 100
        RemovalsCT = 200.0 
        TreeVolCT = 5.0 
        RemovalsSLT = 100.0 
        TreeVolSLT = 70.0 
        RemovalsLLT = 20.0 
        TreeVolLLT = 200.0 
        HdwdFractionCT = 0.15 
        HdwdFractionSLT = 0.0 
        HdwdFractionLLT = 0.0
        
        # Expected Output
        harvestCost = 0.5467
        HarvestSystem = 'CableManualWT'
        
        assert(harvesting.harvestcost(
                PartialCut, Slope, SkidDist, Elevation,
                RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT,
                HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT))== (harvestCost, HarvestSystem)

				
def test_harvesting_HelicopterManualWT():
        # test harvesting: harvestCost, HarvestSystem
        
        # Input
        PartialCut = 0 
        Slope = 60
        SkidDist = 2000
        Elevation = 100
        RemovalsCT = 200.0 
        TreeVolCT = 5.0 
        RemovalsSLT = 100.0 
        TreeVolSLT = 70.0 
        RemovalsLLT = 20.0 
        TreeVolLLT = 100.0 
        HdwdFractionCT = 0.15 
        HdwdFractionSLT = 0.0 
        HdwdFractionLLT = 0.0
        
        # Expected Output
        harvestCost = 1.2036
        HarvestSystem = 'HelicopterManualWT'
        
        assert(harvesting.harvestcost(
                PartialCut, Slope, SkidDist, Elevation,
                RemovalsCT, TreeVolCT, RemovalsSLT, TreeVolSLT, RemovalsLLT, TreeVolLLT,
                HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT))== (harvestCost, HarvestSystem)
	

def test_hauling():
        # test hauling: haulCost

        # Input
        haulDist = 8.94 
        haulTimeRT = 65.8402988889

        # Expected Output
        haulCost = 0.604

        assert(hauling.haulcost(haulDist, haulTimeRT)) == haulCost


def test_cost_func():
        # test cost_func: cost

        # Input
        # stand info
        area = 66.3709
        elevation = 141.034205761
        slope = 21.74728843 
        stand_wkt = u'POLYGON ((-13809080.891332019 5330620.9753014417,-13808943.708174769 5331066.8205624959,-13808393.373740762 5330897.4868904939,-13808530.556898013 5330451.6416294342,-13809080.891332019 5330620.9753014417))'
        # harvest info
        RemovalsCT = 200.0 
        TreeVolCT = 5.0 
        RemovalsSLT = 100.0 
        TreeVolSLT = 70.0 
        RemovalsLLT = 20.0 
        TreeVolLLT = 200.0 
        HdwdFractionCT = 0.15 
        HdwdFractionSLT = 0.0 
        HdwdFractionLLT = 0.0
        PartialCut = 0 
        # routing info
        landing_coords = (-124.04858, 43.12776) 
        haulDist = 8.674960531
        haulTime = 32.92 
        coord_mill = (-124.161246, 43.106512)

        # Expected Output
        cost = {'slope': 21.75, 'skid_distance': 999.69, 'mill_coordinates': (-124.161246, 43.106512), 'elevation': 141.03, 'total_harvest_cost': 314598.0, 'haul_distance_ow': 8.94, 'total_cost': 350309.0, 'haul_cost_min': 0.604, 'total_area': 66.37, 'harvest_cost_ft3': 0.395, 'haul_distance_extension': 0.269, 'total_haul_trips': 898.0, 'haul_time_ow': 32.92, 'total_haul_cost': 35711.0, 'harvest_system': 'GroundBasedMechWT', 'landing_coordinates': (-124.04706351844823, 43.125146208049415), 'total_volume': 796450.8}
        assert(main_model.cost_func(
                # stand info
                area,
                elevation,
                slope,
                stand_wkt,
                # harvest info
                RemovalsCT,
                TreeVolCT,
                RemovalsSLT,
                TreeVolSLT,
                RemovalsLLT,
                TreeVolLLT,
                HdwdFractionCT,
                HdwdFractionSLT,
                HdwdFractionLLT,
                PartialCut,
                # routing info
                landing_coords,
                haulDist,
                haulTime,
                coord_mill
                )) == cost
