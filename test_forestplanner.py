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
from forestcost import main_model as m
from forestcost import routing as r
from forestcost import landing
import operator
import random
import json
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

    # Mill information
    mill_shp = 'Data/mills.shp'

    # Landing Coordinates
    center = scenario.input_property.geometry_final.point_on_surface
    centroid_coords = center.transform(4326, clone=True).tuple
    landing_coords = landing.landing(centroid_coords=centroid_coords)

    haulDist, haulTime, coord_mill = r.routing(
        landing_coords,
        mill_shp=mill_shp
    )

    annual_total_cost = defaultdict(float)
    annual_haul_cost = defaultdict(float)
    annual_heli_harvest_cost = defaultdict(float)
    annual_ground_harvest_cost = defaultdict(float)
    annual_cable_harvest_cost = defaultdict(float)
    used_records = 0
    skip_noharvest = 0
    skip_error = 0

    year = None
    years = []
    for row in data:
        ### GIS Data
        stand_wkt = row['stand_wkt']
        area = row['acres']
        if year != int(row['year']):
            year = int(row['year'])
            print "Calculating cost per stand in year", year
            years.append(year)
            annual_total_cost[year] += 0
            annual_haul_cost[year] += 0
            annual_heli_harvest_cost[year] += 0
            annual_ground_harvest_cost[year] += 0
            annual_cable_harvest_cost[year] += 0

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
            cut_type = 0

        # PartialCut(clear cut = 0, partial cut = 1)
        if cut_type == 3:
            PartialCut = 0
        elif cut_type in [1, 2]:
            PartialCut = 1
        else:
            # no harvest so don't attempt to calculate
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
            annual_haul_cost[year] += result['total_haul_cost']
            annual_total_cost[year] += result['total_cost']

            system = result['harvest_system']
            if system.startswith("Helicopter"):
                annual_heli_harvest_cost[year] += result['total_harvest_cost']
            elif system.startswith("Ground"):
                annual_ground_harvest_cost[year] += result['total_harvest_cost']
            elif system.startswith("Cable"):
                annual_cable_harvest_cost[year] += result['total_harvest_cost']
            else:
                # TODO
                annual_cable_harvest_cost[year] += result['total_harvest_cost']
                #raise ValueError
            used_records += 1
        except (ZeroDivisionError, ValueError):
            skip_error += 1

            # import traceback
            # print cost_args
            # print traceback.format_exc()


    def ordered_costs(x):
        sorted_x = sorted(x.iteritems(), key=operator.itemgetter(0))
        return [-1 * z[1] for z in sorted_x]

    print "--------"
    print "    var heli =", json.dumps(ordered_costs(annual_heli_harvest_cost)), ";"
    print "    var cable =", json.dumps(ordered_costs(annual_cable_harvest_cost)), ";"
    print "    var ground =", json.dumps(ordered_costs(annual_ground_harvest_cost)), ";"
    print "    var haul =", json.dumps(ordered_costs(annual_haul_cost)), ";"
    print "    var years =", json.dumps(sorted(annual_haul_cost.keys())), ";"

    # RANDOMLY determine a revenue w/in % of total cost; HACK
    rev = [-1 * x * (1.0 + (0.35 - (random.random() * 0.5))) for x in ordered_costs(annual_total_cost)]
    #rev = [-1 * x for x in ordered_costs(annual_total_cost)]
    print "    var revenue =", json.dumps(rev), ";"

    # determine profit
    profit = [revenue + cost for revenue, cost in zip(rev, ordered_costs(annual_total_cost))]
    print "    var profit =", json.dumps(profit), ";"

    print "--------"
    print "year, heliHarvestCost, cableHarvestCost, groundHarvestCost, transportationCost"
    for year in sorted(dict(annual_haul_cost).keys()):
        print ", ".join(str(x)
            for x in [
                year,
                annual_heli_harvest_cost[year],
                annual_cable_harvest_cost[year],
                annual_ground_harvest_cost[year],
                annual_haul_cost[year]
            ]
        )

    print "--------"
    print "used records:", used_records
    print "skipped (no harvest):", skip_noharvest
    print "skipped (errors):", skip_error

if __name__ == "__main__":
    main()
