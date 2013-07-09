import main_model as m
from pprint import pprint


error_cases = [
    #       File "/usr/local/apps/cost_model/harvesting.py", line 2069, in harvestcost
    #     LoadVolALT = LoadWeight*2000/(WoodDensityALT*100)
    # ZeroDivisionError: float division by zero
    (2.47576327441736, 481.666667, 57.333333,
        u'POLYGON((-13842104.4357139 5280195.6384591,-13842086.1398596 5280186.97130064,-13842027.4171602 5280183.33844236,-13842018.6592795 5280171.68920807,-13842004.4516435 5280148.14201403,-13841994.3832237 5280130.64964902,-13841980.6709483 5280118.01097792,-13841959.1403103 5280103.39201004,-13841938.6639338 5280094.97068399,-13841932.4697944 5280086.45638794,-13841935.6947739 5280086.13475863,-13841952.5447452 5280084.03741252,-13841975.8387481 5280080.32464832,-13842000.1948121 5280071.29501901,-13842023.3694338 5280064.95387604,-13842040.9233867 5280049.65476146,-13842064.0979369 5280043.31354433,-13842077.8092712 5280029.50932202,-13842089.9811332 5280010.50884655,-13842090.6350671 5280008.52404882,-13842100.9462222 5280016.65571482,-13842116.8431273 5280027.17013179,-13842123.4114357 5280109.98329996,-13842121.7063528 5280136.89221412,-13842114.3080809 5280170.15104848,-13842104.4357139 5280195.6384591))',
        69.3708869491744, 0.173303429209215, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1,
        (-124.36079, 42.7944), 217.965140751, 370.08, (-123.567700, 41.256400)),

    #    File "/usr/local/apps/cost_model/harvesting.py", line 1628, in harvestcost
    #     CostYardCTL =  round (WeightingProductYardCYCTL/ WeightingDivisiorYardCYCTL, 2)
    # ZeroDivisionError: float division by zero
    (9.49770453465532, 431.555556, 41.111111,
        u'POLYGON((-13842669.4771842 5280242.64789385,-13842652.4987943 5280237.77793674,-13842656.8897637 5280204.6578773,-13842660.1058989 5280188.69189003,-13842661.7352753 5280180.60310464,-13842652.0748432 5280163.1358853,-13842648.1626288 5280142.40190329,-13842641.1933446 5280118.80961512,-13842639.4317074 5280080.0608401,-13842635.3834413 5280056.33323589,-13842618.753999 5280015.27423176,-13842620.4578035 5279988.36562231,-13842630.3708708 5279946.07585109,-13842629.0603866 5279917.25006741,-13842653.7647084 5279919.44713993,-13842681.570485 5279945.07242101,-13842688.726131 5279955.96941589,-13842723.1392391 5279931.9151481,-13842742.0625281 5279908.6651808,-13842758.4732936 5279878.67449844,-13842770.2407412 5279844.52780767,-13842791.201188 5279816.64052826,-13842801.8413193 5279807.14669698,-13842825.4113225 5279788.13850003,-13842844.7387277 5279773.78435355,-13842863.6575785 5279750.44906435,-13842875.183063 5279727.30477752,-13842881.9655168 5279713.68493111,-13842874.0978632 5279687.13566173,-13842870.7761682 5279662.60408373,-13842874.3654791 5279644.52327233,-13842884.0322439 5279612.70340441,-13842877.6500012 5279570.31426809,-13842876.5334185 5279545.76641286,-13842875.6152569 5279525.58077308,-13842879.8576578 5279520.92683543,-13842892.51449 5279520.33947308,-13842921.0626795 5279577.21375358,-13842923.2299166 5279624.85564144,-13842923.0809859 5279627.17682714,-13842921.6207884 5279654.75878729,-13842932.3667956 5279696.08865533,-13842930.6253875 5279723.08388864,-13842918.1975066 5279774.40400295,-13842899.1660594 5279811.11632445,-13842885.520131 5279835.66431469,-13842880.8153475 5279862.79749769,-13842862.5967357 5279917.38718403,-13842852.6943554 5279936.53061215,-13842843.6071725 5279954.09805781,-13842824.3028271 5279984.82343409,-13842822.6972561 5280014.8133687,-13842807.1690661 5280063.27879305,-13842805.3067556 5280066.95128315,-13842796.3074131 5280084.69803503,-13842770.8500141 5280109.79467004,-13842748.3134729 5280134.7558011,-13842717.9205678 5280180.9969214,-13842695.5159876 5280208.8664804,-13842669.4771842 5280242.64789385))',
        0.0, 0.0, 1797.82049136491, 232.978692235095, 238.962246091928, 1865.44414765165, 0.0, 0.51, 0.0, 0,
        (-124.36079, 42.7944), 217.965140751, 370.08, (-123.567700, 41.256400)),

    #    File "/usr/local/apps/cost_model/harvesting.py", line 62, in harvestcost
    #     DBH =((RemovalsCT*(DBHCT**2.0)+RemovalsALT*(DBHALT**2.0))/Removals)**0.5
    # ZeroDivisionError: float division by zero
    (2.07030545679967, 489.25, 47.5,
        u'POLYGON((-13842027.4171602 5280183.33844236,-13841945.1135143 5280178.24620034,-13841899.4676553 5280182.93186196,-13841864.6825283 5280178.28531141,-13841830.6068867 5280157.49064577,-13841808.6545581 5280117.79081857,-13841800.2426322 5280102.57817645,-13841809.8210442 5280098.54852602,-13841825.0124533 5280088.62674605,-13841845.6453818 5280083.72059,-13841866.5168874 5280084.07096527,-13841888.6891353 5280084.36105941,-13841911.0403481 5280088.59353505,-13841932.4697944 5280086.45638794,-13841938.6639338 5280094.97068399,-13841959.1403103 5280103.39201004,-13841980.6709483 5280118.01097792,-13841994.3832237 5280130.64964902,-13842004.4516435 5280148.14201403,-13842018.6592795 5280171.68920807,-13842027.4171602 5280183.33844236))',
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1,
        (-124.36079, 42.7944), 217.965140751, 370.08, (-123.567700, 41.256400)),

    #   File "/usr/local/apps/cost_model/harvesting.py", line 2278, in harvestcost
    #     Price = min(filter(lambda t:not math.isnan(t[1]), HarvestingSystem),key=operator.itemgetter(1))
    # ValueError: min() arg is an empty sequence
    # Note... previously this returned Nan ... need an appropriate return value for this case!
    (2.71492708952138, 377.25, 47.0,
        u'POLYGON((-13843408.733415 5280337.5965661,-13843373.0984388 5280350.65295566,-13843367.3080292 5280353.92219075,-13843338.5994566 5280357.91313726,-13843339.0266171 5280307.66071561,-13843182.3804864 5280307.22104532,-13843209.1283432 5280285.32025666,-13843236.2365453 5280253.63059746,-13843253.9486899 5280233.6066872,-13843310.1717808 5280181.70646813,-13843317.2263558 5280180.51371843,-13843340.2301456 5280176.62432728,-13843350.0815601 5280174.9666405,-13843354.0375004 5280174.26856123,-13843369.1731046 5280187.1091622,-13843383.2601561 5280239.34395355,-13843408.733415 5280337.5965661))',
        11.6741864849419, 0.434388334323421, 39.2578457144792, 112.533727860661, 22.7782382810844, 534.62344246855, 1.0, 0.71, 0.26, 1,
        (-124.36079, 42.7944), 217.965140751, 370.08, (-123.567700, 41.256400)),

    # OGR ERROR
    # THIS TEST MUST COME LAST due to stupid OGR exception handling
    # ERROR 6: Incompatible geometry for operation
    (8.42383839584886, 288.647059, 56.529412,
        u'POLYGON((-13843317.2263558 5280180.51371843,-13843310.1717808 5280181.70646813,-13843253.9486899 5280233.6066872,-13843236.2365453 5280253.63059746,-13843209.1283432 5280285.32025666,-13843182.3804864 5280307.22104532,-13843158.9193813 5280307.19608964,-13843180.7994756 5280212.83065364,-13843193.5430684 5280119.06191462,-13843207.3697173 5280043.50183757,-13843230.3203916 5279959.63268963,-13843240.2682856 5279919.32038605,-13843248.7651429 5279884.88808611,-13843283.4990202 5279808.27325109,-13843313.7942978 5279751.57961882,-13843331.475017 5279717.84377628,-13843344.661721 5279707.45975461,-13843365.9661744 5279690.46620752,-13843372.0465947 5279685.61613435,-13843430.9125446 5279680.65285725,-13843470.6243148 5279660.29347678,-13843490.2456322 5279636.58179679,-13843489.2322893 5279655.31458884,-13843490.2023601 5279676.61440715,-13843490.591821 5279685.16577849,-13843485.927085 5279712.21125175,-13843449.6122045 5279758.7275645,-13843418.6357979 5279792.99576888,-13843394.1308963 5279838.96362799,-13843388.7917221 5279863.04121265,-13843369.0291293 5279863.95927203,-13843336.1907388 5279865.48467692,-13843329.6002641 5279887.52907366,-13843328.0618439 5279909.3388576,-13843318.0889141 5279940.49158606,-13843303.6447395 5279984.63946336,-13843295.167068 5280020.83795992,-13843284.0470807 5280054.60182832,-13843279.7069555 5280098.28095854,-13843298.4352258 5280120.42872132,-13843317.1054791 5280141.30044509,-13843321.7079625 5280158.98934369,-13843317.2948091 5280173.2607479,-13843317.2263558 5280180.51371843))',
        755.112873803892, 1.76900606312826, 0.0, 0.0, 0.0, 0.0, 0.32, 0.0, 0.0, 1,
        (-124.35033096, 42.980014393), 226.057876655, 382.13, (-123.567700, 41.256400)),

]

# cost_args = (
#     # 1. stand info
#     area, elevation, slope,
#
#     # 2. stand geometry
#     stand_wkt,
#
#     # 3. harvest info
#     RemovalsCT, TreeVolCT,
#     RemovalsSLT, TreeVolSLT,
#     RemovalsLLT, TreeVolLLT,
#     HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT,
#     PartialCut,
#
#     # 4. routing info
#     landing_coords, haulDist, haulTime, coord_mill
# )


def main():
    for i, cost_args in enumerate(error_cases):
        print "Test %d: " % (i + 1,), cost_args[0]
        try:
            cost = m.cost_func(*cost_args)
            pprint(cost)
        except:
            import traceback
            print traceback.format_exc()
            print


if __name__ == '__main__':
    main()
