import os
import sys
from django.core.management import setup_environ
thisdir = os.path.dirname(os.path.abspath(__file__))
appdir = os.path.realpath(os.path.join(thisdir, '..', 'land_owner_tools', 'lot'))
sys.path.append(appdir)
import settings
setup_environ(settings)
from collections import defaultdict

# import sys
# from IPython.core import ultratb
# sys.excepthook = ultratb.FormattedTB(mode='Verbose',
#      color_scheme='Linux', call_pdb=1)

##############################
import main_model as m
import routing_main as r
import landing
from pprint import pprint
from trees.models import Scenario
from django.db import connection


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        if None not in row  # remove any nulls; incomplete data can't be used
    ]


def main():

    scenario = Scenario.objects.get(id=122)

    sql = """SELECT
                ss.id AS sstand_id, a.cond, a.rx, a.year, a.offset, ss.acres AS acres,
                a.total_stand_carbon AS total_carbon,
                a.agl AS agl_carbon,
                a.removed_merch_bdft / 1000.0 AS harvested_timber, -- convert to mbf
                a.after_merch_bdft / 1000.0 AS standing_timber, -- convert to mbf
                ST_AsText(ss.geometry_final) AS stand_wkt,
                a.LG_CF             AS LG_CF,
                a.LG_HW             AS LG_HW,
                a.LG_TPA            AS LG_TPA,
                a.SM_CF             AS SM_CF,
                a.SM_HW             AS SM_HW,
                a.SM_TPA            AS SM_TPA,
                a.CH_CF             AS CH_CF,
                a.CH_HW             AS CH_HW,
                a.CH_TPA            AS CH_TPA,
                stand.elevation  AS elev,
                stand.slope      AS slope,
                a.CUT_TYPE       AS CUT_TYPE
            FROM
                trees_fvsaggregate a
            JOIN
                trees_scenariostand ss
              ON  a.cond = ss.cond_id
              AND a.rx = ss.rx_internal_num
              AND a.offset = ss.offset
            JOIN trees_stand stand
              ON ss.stand_id = stand.id
            -- WHERE a.site = 2 -- TODO if we introduce multiple site classes, we need to fix
            WHERE   var = '%s' -- get from current property
            AND   ss.scenario_id = %d -- get from current scenario
            ORDER BY a.year, ss.id;""" % (scenario.input_property.variant.code, scenario.id)

    cursor = connection.cursor()
    cursor.execute(sql)
    data = dictfetchall(cursor)

    ### Mill information
    # Can use mill_lyr alone, mill_lyr AND millID, OR mill_Lat and mill_Lon
    # TODO get mill layer
    # mill_shp = driver.Open('Data//ODF_mills.shp', 0)
    # mill_lyr = mill_shp.GetLayer()
    mill_lyr = None
    millID = None
    mill_Lat = 43.1190
    mill_Lon = -124.4075

    # Landing Coordinates
    # landing_coords = (-124.35033096, 42.980014393)
    center = scenario.input_property.geometry_final.point_on_surface
    centroid_coords = center.transform(4326, clone=True).tuple
    landing_coords = landing.landing(centroid_coords=centroid_coords)

    haulDist, haulTime, coord_mill = r.routing(
        landing_coords,
        millID,
        mill_Lat,
        mill_Lon,
        mill_lyr
    )

    annual_haul_cost = defaultdict(float)
    annual_harvest_cost = defaultdict(float)
    used_records = 0
    skip_noharvest = 0
    skip_error = 0

    for row in data:
        ### GIS Data
        stand_wkt = row['stand_wkt']
        area = row['acres']
        year = int(row['year'])

        # NOTE: elevation and slope come directly from stand 
        # if we use spatial contrainsts to chop scenariostands,
        # will need to recalc zonal stats
        elevation = row['elev']
        slope = row['slope']

        ### Tree Data ###
        # Cut type code indicating type of harvest implemented.
        # 0 = no harvest, 1 = pre-commercial thin,
        # 2 = commercial thin, 3 = regeneration harvest
        try:
            cut_type = int(row['cut_type'])
        except:
            # no harvest so don't attempt to calculate
            annual_haul_cost[year] += 0
            annual_harvest_cost[year] += 0
            skip_noharvest += 1
            continue

        # PartialCut(clear cut = 0, partial cut = 1)
        if cut_type == 3:
            PartialCut = 0
        elif cut_type in [1, 2]:
            PartialCut = 1
        else:
            # no harvest so don't attempt to calculate
            annual_haul_cost[year] += 0
            annual_harvest_cost[year] += 0
            skip_noharvest += 1
            continue

        # Hardwood Fraction
        # Chip Trees
        RemovalsCT = row['ch_tpa']
        TreeVolCT = row['ch_cf']
        HdwdFractionCT = row['ch_hw']

        # Small Log Trees
        RemovalsSLT = row['sm_tpa']
        TreeVolSLT = row['sm_cf']
        HdwdFractionSLT = row['sm_hw']

        # Large Log Trees
        RemovalsLLT = row['lg_tpa']
        TreeVolLLT = row['lg_cf']
        HdwdFractionLLT = row['lg_hw']

        cost_args = (
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
        )

        try:
            result = m.cost_func(*cost_args)
            # if math.isnan(result['total_cost']):
            #     ???
            annual_haul_cost[year] += result['total_haul_cost']
            annual_harvest_cost[year] += result['total_harvest_cost']
            used_records += 1
        except (ZeroDivisionError, ValueError):
            annual_haul_cost[year] += 0
            annual_harvest_cost[year] += 0
            skip_error += 1

            # import traceback
            # print cost_args
            # print traceback.format_exc()

    print "--------"
    print "Year, HarvestCost, TransportationCost"
    for year in sorted(dict(annual_harvest_cost).keys()):
        print ", ".join(str(x) for x in [year, annual_harvest_cost[year], annual_haul_cost[year]])

    print "--------"
    print "used records:", used_records
    print "skipped (no harvest):", skip_noharvest
    print "skipped (errors):", skip_error

if __name__ == "__main__":
    main()
