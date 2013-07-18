import math
import operator
import xlrd
import os


def harvestcost(PartialCut, Slope, SkidDist, Elevation,
                RemovalsCT, TreeVolCT,
                RemovalsSLT, TreeVolSLT,
                RemovalsLLT, TreeVolLLT,
                HdwdFractionCT, HdwdFractionSLT, HdwdFractionLLT):

        ################################################
        # General functions                            #
        ################################################

        def relevancefunction(cost, relevances, volumes):
            sum_map = sum(map( operator.mul, relevances, volumes))
            if sum_map == 0:
                sum_map = 0.000001
            return 100*cost*sum(relevances)/sum_map

        def volumePMH (vol, ti):   # Volume per PMH (Volumte, Time) Function
           return (vol/(ti/60.0))

        def costpmhfunc (purchaseprice, horespower, machinelife, salvagevaluepercent, utilizationrate, repairmaintenance, interestrate, insurancetaxrate,
                     fuelconsumptionrate, fuelcostgallon, lubeoil, crewSize, crewwagebenefitsrate, smh):

            # Productive Machine Hours
            pmh = smh*utilizationrate

            # Ownership Cost per PMH
            # Salvage Value
            salvagevalue = purchaseprice*salvagevaluepercent
            # Average Yearly Investment
            yearlyinvestment = ((purchaseprice-salvagevalue)*(machinelife+1)/(machinelife*2))+salvagevalue
            # Insurance and tax cost
            insurancetaxcost = insurancetaxrate*yearlyinvestment
            # Annual Depreciation
            depreciation = (purchaseprice-salvagevalue)/machinelife
            # Interest Cost
            interestcost = interestrate*yearlyinvestment
            # Yearly Ownership Costs 
            yearlyownershipcost = insurancetaxcost+interestcost+depreciation
            # Ownership Cost per PMH
            ownershipcost=yearlyownershipcost/pmh

            # Operating Cost per PMH
            # Operator labor and benfit cost per PMH
            operatorcost = crewwagebenefitsrate/utilizationrate
            # Fuel Cost
            fuelcost = horespower*fuelconsumptionrate*fuelcostgallon
            # Lube Cost
            lubecost = lubeoil*fuelcost
            # Repair and maintenance cost
            repairmaintenancecost = depreciation*(repairmaintenance/pmh)
            # Operating Cost per PMH
            operatingcost = fuelcost+lubecost+repairmaintenancecost+operatorcost

            # Cost per PMH
            costpmh = ownershipcost+operatingcost
            costpmh = round(costpmh, 2)
            return costpmh


        ################################################
        # Skidding Cost unbunched                      #
        ################################################
        def CostSkidUBfunc():

            if SkidDist>0:
                # Precalculations
                if PartialCut == 0:
                    TurnVol = 44.87*TreeVol**0.282*CSlopeSkidForwLoadSize
                else:
                    TurnVol = 31.62*TreeVol**0.282*CSlopeSkidForwLoadSize
                LogsPerTurnS = TurnVol/LogVol
                ChokerLogs = min(10.0, LogsPerTurnS)
                ChokerTurnVol = ChokerLogs*LogVol   
                
                # relevance Inputs
                # CC (Johnson&Lee, 88)
                if ChokerTurnVol < 90:
                    relevanceSUJohnson881 = 1.0
                elif ChokerTurnVol < 180:
                    relevanceSUJohnson881 = round(2-ChokerTurnVol/90,2)
                else:
                    relevanceSUJohnson881 = 0.0

                # CC (Gibson&Egging, 73)
                relevanceSUGibson73 = 1.0

                # CC (Gardner, 79)
                relevanceSUGardner79 = 1.0

                # Cat 518 or Cat D4H, cable (Andersson, B. and G. Young  1998)
                if TreeVol < 5:
                    relevanceSUAnderson98 = 0.0
                elif TreeVol < 15:
                    relevanceSUAnderson98 = round(-0.5+TreeVol/10,2)
                elif TreeVol < 75:
                    relevanceSUAnderson98 = 1.0
                elif TreeVol < 150:
                    relevanceSUAnderson98 = round(2-TreeVol/75,2)
                else:
                    relevanceSUAnderson98 = 0.0
                
                # Cat 518 (Johnson, 88)
                if ButtDiam < 20:
                    relevanceSUJohnson882 = 1.0
                elif ButtDiam < 25:
                    relevanceSUJohnson882 = round(5-ButtDiam/5,2)
                else:
                    relevanceSUJohnson882 = 0.0

                # JD 648 (Gebhardt, 77)
                relevanceSUGebhardt77 = 1.0

                relevanceSkidUn = []
                relevanceSkidUn.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceSU'))

                # Turn Time
                turnTimeJohnson881 = -15.58+0.345*ChokerLogs+0.037*ChokerTurnVol+4.05*math.log(SkidDist+25)
                turnTimeGibson73 = 2.74+0.726*ChokerLogs+0.00363*ChokerTurnVol*5+0.0002*ChokerTurnVol*WoodDensity+0.00777*SkidDist+0.00313*Slope**2
                turnTimeGardner79 = 2.57+0.823*ChokerLogs+0.0054*ChokerTurnVol*5+0.0078*2*SkidDist
                turnTimeAndersson98 = 7.36+0.0053*SkidDist
                turnTimeJohnson882 = 0.518+0.0107*SkidDist+0.0011*Slope**3+1.62*math.log(LogsPerTurnS)
                turnTimeGebhardt77 = 1.072+0.00314*SkidDist+0.0192*Slope+0.315*1.5*PartialCut+0.489*LogsPerTurnS-0.819*1.1+0.00469*17+0.00139*TurnVol*5

                # Skidding Volume/ PMH (ccf)
                USkidVolPMHJohnson881 = round(volumePMH (TurnVol, turnTimeJohnson881))
                USkidVolPMHGibson73 = round(volumePMH (TurnVol, turnTimeGibson73))
                USkidVolPMHGardner79 = round(volumePMH (TurnVol, turnTimeGardner79))
                USkidVolPMHAndersson98 = round(volumePMH (TurnVol, turnTimeAndersson98))
                USkidVolPMHJohnson882 = round(volumePMH (TurnVol, turnTimeJohnson882))
                USkidVolPMHGebhardt77 = round(volumePMH (TurnVol, turnTimeGebhardt77))

                volumeSkidUn = []
                volumeSkidUn.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('USkidVolPMH'))

                # Skidding cost ($/ ccf)
                CostSkidUB = round(CHardwood*relevancefunction(SkidderHourlyCost, relevanceSkidUn, volumeSkidUn),2)

            else:
                CostSkidUB = 0

            return CostSkidUB

			
        ################################################
        # Skidding Cost bunched                        #
        ################################################
        def CostSkidBunfunc():

            if SkidDist>0:
                # Precalculations
                if PartialCut == 0:
                    TurnVol = 44.87*TreeVol**0.282*CSlopeSkidForwLoadSize
                else:
                    TurnVol = 31.62*TreeVol**0.282*CSlopeSkidForwLoadSize
                LogsPerTurnS = TurnVol/LogVol
                ChokerLogs = min(10.0, LogsPerTurnS)
                ChokerTurnVol = ChokerLogs*LogVol   

                # relevance Inputs
                # Grapple Skidders (Johnson, 88)
                if ButtDiam < 15:
                    relevanceSBJohnson88 = 1
                elif ButtDiam < 20:
                    relevanceSBJohnson88 = 4 - ButtDiam/5.0
                else:
                    relevanceSBJohnson88 = 0

                # Grapple Skidders (Tufts et al, 88)
                relevanceSBTufts88 = 0.5

                # John Deere 748E (Kosicki, K. 00. Productivities and costs of two harvesting trials in a western Alberta riparian zone.  FERIC Advantage 1(19))
                if TreeVol < 5:
                    relevanceSBKosicki00 = 0
                elif TreeVol < 10:
                    relevanceSBKosicki00 = -1 + TreeVol/5.0
                elif TreeVol < 50:
                    relevanceSBKosicki00 = 1
                elif TreeVol < 100:
                    relevanceSBKosicki00 = 2 - TreeVol/50.0
                else:
                    relevanceSBKosicki00 = 0

                # Cat D5H TSK Custom Track (Henderson, B. 01. Roadside harvesting with low ground-presssure skidders in northwestern British Columbia. FERIC Advantage 2(54))
                if TreeVol < 5:
                    relevanceSBHenderson01 = 0
                elif TreeVol < 10:
                    relevanceSBHenderson01 = -1 + TreeVol/5.0
                elif TreeVol < 50:
                    relevanceSBHenderson01 =  1
                elif TreeVol < 100:
                    relevanceSBHenderson01 = 2 - TreeVol/50.0
                else:
                    relevanceSBHenderson01 = 0

                # JD 748_G-II & TJ 560 (Kosicki, K. 02. Productivity and cost of summer harvesting in a central Alberta mixedwood stand. FERIC Advantage 3(6))
                if TreeVol < 30:
                    relevanceSBKosicki021 = 1
                elif TreeVol < 60:
                    relevanceSBKosicki021 = 2 - TreeVol/30.0
                else:
                    relevanceSBKosicki021 = 0

                # Tigercat 635 (Boswell, B. 98. Vancouver Island mechanized thinning trials. FERIC Technical Note TN-271)
                if TreeVol < 5:
                    relevanceSBBoswell98 = 0
                elif TreeVol < 10:
                    relevanceSBBoswell98 = -1 + TreeVol/5.0
                elif TreeVol < 100:
                    relevanceSBBoswell98 = 1
                elif TreeVol < 150:
                    relevanceSBBoswell98 = 3 - TreeVol/50.0
                else:
                    relevanceSBBoswell98 = 0
                    
                # Tigercat 635 (Kosicki, K. 02. Evaluation of Trans-Gesco TG88C and Tigercat 635 grapple skidders working in central Alberta. FERIC Advantage 3(37))
                if TreeVol < 40:
                    relevanceSBKosicki022 = 1
                elif TreeVol < 80:
                    relevanceSBKosicki022 = 2 - TreeVol/40.0
                else:
                    relevanceSBKosicki022 = 0

                relevanceSkidB = []
                relevanceSkidB.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceSB'))

                # Trees per Turn
                TreesPerTurnS = TurnVol/TreeVol
                
                # Turn relevance (lb)
                Turnrelevance = TurnVol*WoodDensity

                # Turn Time Johnson 88
                TravelEmpty = -2.179+0.0362*Slope+0.711*math.log(SkidDist)
                TravelLoaded = -0.919+0.00081*SkidDist+0.000062*Slope**3+0.353*math.log(SkidDist)
                LoadTime = max(0,0.882+0.0042*Slope**2-0.000048*(TreesPerTurnS)**3)
                DeckTime = 0.063+0.55*math.log(3)+0.0076*3*TreesPerTurnS
                turnTimeJohnson88 = TravelEmpty + TravelLoaded + LoadTime + DeckTime

                # Turn Time Tufts 88
                skidderHP=50.5+5.74*(TreeVol**0.5)
                treesPerBunch = 6 #  F44 ='Fell&Bunch'!E28 just temporary
                bunchVolume = TreeVol*treesPerBunch
                bunchesPerTurn = max(1,TurnVol/bunchVolume)
                travelEmpty =(0.1905*SkidDist+0.3557*skidderHP-0.0003336*SkidDist*skidderHP)/100
                grapple = min(5,(-38.36+161.6*bunchesPerTurn-0.5599*bunchesPerTurn*skidderHP+1.398*bunchesPerTurn*treesPerBunch)/100)
                travelLoaded =(-34.52+0.2634*SkidDist+0.7634*skidderHP-0.00122*SkidDist*skidderHP+0.03782*SkidDist*bunchesPerTurn)/100
                ungrapple = max(0,(5.177*bunchesPerTurn+0.002508*Turnrelevance-0.00007944*Turnrelevance*bunchesPerTurn*treesPerBunch*bunchesPerTurn)/100)
                turnTimeTufts88 = 1.3*(travelEmpty+grapple+travelLoaded+ungrapple)

                # Turn Time Kosicki 00
                turnTimeKosicki00 = 0.65+0.0054*SkidDist+0.244*2.1

                # Turn Time Henderson 01
                turnTimeHenderson01 = 2.818+0.0109*SkidDist

                # Turn Time Kosicki 02-1
                turnTimeKosicki021 = 0.649+0.0058*SkidDist+0.581*bunchesPerTurn

                # Turn Time Boswell 98
                turnTimeBoswell98 = 5.77 + 0.007 * SkidDist

                # Turn Time Kosicki 02-2
                turnTimeKosicki022 = 2.98+0.006*SkidDist+0.27*TreesPerTurnS

                # Skidding Volume/ PMH (ccf)
                BSkidVolPMHJohnson88 = volumePMH (TurnVol, turnTimeJohnson88)
                BSkidVolPMHTufts88 = volumePMH (TurnVol, turnTimeTufts88)
                BSkidVolPMHKosicki00 = volumePMH (TurnVol, turnTimeKosicki00)
                BSkidVolPMHHenderson01 = volumePMH (TurnVol, turnTimeHenderson01)
                BSkidVolPMHKosicki021 = volumePMH (TurnVol, turnTimeKosicki021)
                BSkidVolPMHBoswell98 = volumePMH (TurnVol, turnTimeBoswell98)
                BSkidVolPMHKosicki022 = volumePMH (TurnVol, turnTimeKosicki022)

                volumeSkidB = []
                volumeSkidB.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('BSkidVolPMH'))

                # Skidding cost ($/ ccf)
                CostSkidBun = round (CHardwood*relevancefunction(SkidderHourlyCost, relevanceSkidB, volumeSkidB), 2)

            else:
                CostSkidBun = 0

            return CostSkidBun


        ################################################
        # Felling                                      #
        ################################################
        def fellfunc(removals, treevol, dbh, hardwood):

            walkdistance = (max((43560/removals),1))**0.5
            
            # relevance Inputs

            # McNeel, 94
            relevanceMFeNeel94 = 1

            # Peterson, 87
            relevanceMFePeterson87 = 1

            # Keatley, 2000
            relevanceMFeKeatley00 = 1

            # Andersson, B. and G. Young, 98
            if treevol < 5:
                    relevanceMFeAndersson98 = 0
            elif treevol < 15:
                    relevanceMFeAndersson98 = -0.5 + treevol/10.0
            elif treevol < 90:
                    relevanceMFeAndersson98 = 1
            elif treevol < 180:
                    relevanceMFeAndersson98 = 2 - treevol/90.0
            else:
                    relevanceMFeAndersson98 = 0

            relevanceMF = []
            relevanceMF.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceMFe'))

            # Time per Tree
            if PartialCut==1:
                TPTmcneel94 = 0.163+0.0444*0.305*walkdistance+0.0323*2.54*dbh
            else:
                TPTmcneel94 = min((0.163+0.0444*0.305*walkdistance+0.0323*2.54*dbh),(0.163+0.0444*0.305*walkdistance+0.0323*2.54*dbh))

            if dbh<10:
                TPTpeterson87 = 0.33+0.012*dbh
            else:
                TPTpeterson87 = 0.1+0.0111*dbh**1.496
            TPTkeatley00 = (4.58+0.07*walkdistance+0.16*dbh)**0.5
            TPTandersoon98 = 1.082+0.01505*treevol-0.634/treevol

            # Calculate Volume per PMH
            MFeVolumePMHmcneel94 = volumePMH (treevol, TPTmcneel94)
            MFeVolumePMHpeterson87 = volumePMH (treevol, TPTpeterson87)
            MFeVolumePMHkeatley00 = volumePMH (treevol, TPTkeatley00)
            MFeVolumePMHandersoon98 = volumePMH (treevol, TPTandersoon98)

            volumeMF = []
            volumeMF.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('MFeVolumePMH'))

            # Felling Cost ($/ ccf)
            costMF = hardwood*relevancefunction(costPMHCSa, relevanceMF, volumeMF)
            return costMF

        def felllimbbuckfunc(removals, treevol, dbh, logspertree, hardwood):

            walkdistance = (max((43560/removals),1))**0.5
            
            # relevance Inputs

            # Kellogg&Olsen, 86
            relevanceMFLBKellogg1986 = 1

            # Kellogg, L., M. Miller and E. Olsen, 1999
            if treevol < 1:
                    relevanceMFLBKellogg1999 = 0
            elif treevol < 2:
                    relevanceMFLBKellogg1999 = -1 + treevol/1.0
            elif treevol < 70:
                    relevanceMFLBKellogg1999 = 1
            else:
                    relevanceMFLBKellogg1999 = 1.2-treevol/350.0

            # Andersson, B. and G. Young, 98
            if treevol < 5:
                    relevanceMFLBAndersson1998 = 0
            elif treevol < 15:
                    relevanceMFLBAndersson1998 = -0.5+treevol/10.0
            else:
                    relevanceMFLBAndersson1998 = 1

            relevanceMaFLB = []
            relevanceMaFLB.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceMFLB'))

            # Time per Tree
            if PartialCut == 0:
                HeavyThin = 1
            else:
                HeavyThin = 0
            TPTkellogg1999 =(-0.465+0.102*dbh+0.016*31.5+0.562*logspertree+0.009*Slope+0.734*0.02+0.137*0.21+0.449+0.426*HeavyThin)*(1+0.25)
            if PartialCut == 1:
                TPTkellogg1986 = 1.2*(1.33+0.0187*walkdistance+0.014*Slope+0.0987*treevol+0.14)
            else:
                TPTkellogg1986 = 1.2*0.9*(1.33+0.0187*walkdistance+0.014*Slope+0.0987*treevol+0.14)
            TPTandersson1998 =(1.772+0.02877*treevol-2.6486/treevol)*(1+0.197)

            # Calculate Volume per PMH
            MFLBVolumePMHkellogg1999 = volumePMH (treevol, TPTkellogg1999)
            MFLBVolumePMHkellogg1986 = volumePMH (treevol, TPTkellogg1986)
            MFLBVolumePMHandersson1998 = volumePMH (treevol, TPTandersson1998)

            volumeMaFLB = []
            volumeMaFLB.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('MFLBVolumePMH'))

            # Felling Cost ($/ ccf)
            costMFLB = hardwood*relevancefunction(costPMHCSa, relevanceMaFLB, volumeMaFLB)
            return costMFLB

        def CostManFLBfunc():
            CostManFLB = round (felllimbbuckfunc(Removals, TreeVol, DBH, LogsPerTree, CHardwoodLLT), 2)
            return CostManFLB
        
        def CostManFellfunc():
            CostManFell = round (fellfunc(Removals, TreeVol, DBH, CHardwoodLLT), 2)
            return CostManFell

        def CostManFLBLLTfunc():
            if TreeVolLLT>0:
                CostManFLBLLT = round (felllimbbuckfunc(RemovalsLLT, TreeVolLLT, DBHLLT, LogsPerTreeLLT, CHardwoodLLT), 2)
            else:
                CostManFLBLLT = 0
            return CostManFLBLLT
        
        def CostManFellLLTfunc():
            if TreeVolLLT>0:
                CostManFellLLT = round (fellfunc(RemovalsLLT, TreeVolLLT, DBHLLT, CHardwoodLLT), 2)
            else:
                CostManFellLLT = 0 
            return CostManFellLLT
            
        def CostManFellST2func():
            if TreeVolST>0:
                CostManFellST2 = round (fellfunc(Removals, TreeVolST, DBHST, CHardwoodST), 2)
            else:
                CostManFellST2 = 0
            return CostManFellST2

        def CostManFLBLLT2func():
            if TreeVolLLT>0:
                CostManFLBLLT2 = round (felllimbbuckfunc(Removals, TreeVolLLT, DBHLLT, LogsPerTreeLLT, CHardwoodLLT), 2)
            else:
                CostManFLBLLT2 = 0
            return CostManFLBLLT2

        def CostManFLBALT2func():
            if TreeVolALT>0:
                CostManFLBALT2 = round (felllimbbuckfunc(Removals, TreeVolALT, DBHALT, LogsPerTreeALT, CHardwoodALT), 2)
            else:
                CostManFLBALT2 = 0
            return CostManFLBALT2

        def CostManFellCT2func():
            if TreeVolCT>0:
                CostManFellCT2 = round (fellfunc(Removals, TreeVolCT, DBHCT, CHardwoodALT), 2)
            else:
                CostManFellCT2 = 0
            return CostManFellCT2


        ################################################
        # Fell and Bunc                                #
        ################################################
        def CostFellBunchfunc():
            if TreeVolST>0:

                DistBetweenTrees =(43560.0/(max(RemovalsST,1)))**0.5

                # Drive-to-Tree
                # Melroe Bobcat (Johnson, 79)
                if DBHST<10:
                    relevanceFBDJohnson79 = 1.0
                elif DBHST<15:
                    relevanceFBDJohnson79 = 3.0-DBHST/5.0
                else:
                    relevanceFBDJohnson79 = 0

                if Slope<10:
                    relevanceFBDJohnson79 = relevanceFBDJohnson79
                elif Slope<20:
                    relevanceFBDJohnson79 = relevanceFBDJohnson79*(2.0-Slope/10.0)
                else:
                    relevanceFBDJohnson79 = 0

                # Chainsaw Heads (Greene&McNeel, 91)
                if DBHST<15:
                    relevanceFBDGreene911 = 1.0
                elif DBHST<20:
                    relevanceFBDGreene911 = 4.0-DBHST/5.0
                else:
                    relevanceFBDGreene911 = 0

                if Slope<10:
                    relevanceFBDGreene911 = relevanceFBDGreene911
                elif Slope<20:
                    relevanceFBDGreene911 = relevanceFBDGreene911*(2.0-Slope/10.0)
                else:
                    relevanceFBDGreene911 = 0

                # Intermittent Circular Sawheads (Greene&McNeel, 91)
                relevanceFBDGreene912 = relevanceFBDGreene911

                # Hydro-Ax 211 (Hartsough, 01)
                if DBHST<10:
                    relevanceFBDHartsough01 = 1.0
                elif DBHST<20:
                    relevanceFBDHartsough01 = 3.0-DBHST/5.0
                else:
                    relevanceFBDHartsough01= 0

                if Slope<10:
                    relevanceFBDHartsough01 = relevanceFBDHartsough01
                elif Slope<20:
                    relevanceFBDHartsough01 = relevanceFBDHartsough01*(2.0-Slope/10.0)
                else:
                    relevanceFBDHartsough01 = 0

                # Swing Boom
                #  Timbco 2520&Cat 227 (Johnson, 88)
                if DBHST<15:
                   relevanceFBSJohnson88 = 1.0
                elif DBHST<20:
                    relevanceFBSJohnson88 = 4.0-DBHST/5.0
                else:
                    relevanceFBSJohnson88 = 0

                if Slope<5:
                    relevanceFBSJohnson88 = 0
                elif Slope<20:
                    relevanceFBSJohnson88 = relevanceFBSJohnson88*(1.0/3.0+Slope/15.0)
                else:
                    relevanceFBSJohnson88 = relevanceFBSJohnson88

                # JD 693B&TJ Timbco 2518 (Gingras, 88)
                if DBHST<12:
                   relevanceFBSGingras88 = 1.0
                elif DBHST<18:
                    relevanceFBSGingras88 = 3.0-DBHST/6.0
                else:
                    relevanceFBSGingras88 = 0

                if Slope<5:
                    relevanceFBSGingras88 = 0
                elif Slope<20:
                    relevanceFBSGingras88 = relevanceFBSGingras88*(-1.0/3.0+Slope/15.0)
                else:
                    relevanceFBSGingras88 = relevanceFBSGingras88

                # Timbco (Gonsier&Mandzak, 87)
                if DBHST<15:
                   relevanceFBSGonsier87 = 1.0
                elif DBHST<20:
                    relevanceFBSGonsier87 = 4.0-DBHST/5.0
                else:
                    relevanceFBSGonsier87 = 0

                if Slope<15:
                    relevanceFBSGonsier87 = 0
                elif Slope<35:
                    relevanceFBSGonsier87 = relevanceFBSGonsier87*((-3.0/4.0)+(Slope/20))
                else:
                    relevanceFBSGonsier87 = relevanceFBSGonsier87

                #  FERIC Generic (Gingras, J.F., 96.  The cost of product sorting during harvesting.  FERIC Technical Note TN-245)
                if Slope<5:
                    relevanceFBSGingras96 = 0
                elif Slope<20:
                    relevanceFBSGingras96 = -1.0/3.0+Slope/15.0
                else:
                    relevanceFBSGingras96 = 1.0

                # Plamondon, J. 1998.  Trials of mechanized tree-length harvesting in eastern Canada. FERIC Technical Note TN-273)
                if TreeVolST<20:
                   relevanceFBSPlamondon98 = 1.0
                elif TreeVolST<50:
                    relevanceFBSPlamondon98 = 5.0/3.0-TreeVolST/30.0
                else:
                    relevanceFBSPlamondon98 = 0

                if Slope<5:
                    relevanceFBSPlamondon98 = 0
                elif Slope<20:
                    relevanceFBSPlamondon98 = relevanceFBSPlamondon98*(-1.0/3.0+Slope/15.0)
                else:
                    relevanceFBSPlamondon98 = relevanceFBSPlamondon98

                # Timbco 420 (Hartsough, B., E. Drews, J. McNeel, T. Durston and B. Stokes. 97.
                if DBHST<15:
                   relevanceFBSHartsough97 = 1.0
                elif DBHST<20:
                    relevanceFBSHartsough97 = 4.0-DBHST/5.0
                else:
                    relevanceFBSHartsough97 = 0

                if Slope<5:
                    relevanceFBSHartsough97 = 0
                elif Slope<20:
                    relevanceFBSHartsough97 = relevanceFBSHartsough97*(-1.0/3.0+Slope/15.0)
                else:
                    relevanceFBSHartsough97 = relevanceFBSHartsough97


                # Time per Tree
                TPTJohnson79 = 0.204+0.00822*DistBetweenTrees+0.02002*DBHST+0.00244*Slope
                TPTGreene911 =(-0.0368+0.02914*DBHST+0.00289*DistBetweenTrees+0.2134*1.1)*(1+CSlopeFB_Harv)
                TPTGreene912 =(-0.4197+0.01345*DBHST+0.001245*DistBetweenTrees+0.7271*1.01)*(1+CSlopeFB_Harv)

                TPAccumHartsough01 = max(1,14.2-2.18*DBHST+0.0799*DBHST**2)
                TimeAccumHartsough01 = 0.114+0.266+0.073*TPAccumHartsough01+0.00999*TPAccumHartsough01*DBHST
                TPPMHHartsough01 = 60*TPAccumHartsough01/TimeAccumHartsough01

                BoomReachJohnson88 = 24
                TreesInReachJohnson88 = RemovalsST*math.pi*BoomReachJohnson88**2/43560
                TreesPCJohsnon88 = max(1,TreesInReachJohnson88)
                TPCJohnson88 = (0.242+0.1295*TreesPCJohsnon88+0.0295*DBHST*TreesPCJohsnon88)*(1+CSlopeFB_Harv)
                TPTJohnson88 = TPCJohnson88/TreesPCJohsnon88

                TPTGonsier87 = (0.324+0.00138*DBHST**2)*(1+CSlopeFB_Harv+CRemovalsFB_Harv)

                UnmerchMerchGingras88 = min(1.5,(285/(2.47*RemovalsST)))
                TreesInReachGingras88 = RemovalsST*math.pi*24**2/43560
                ObsTreesPerCycleGingras88 =(4.36+9-(0.12+0.34)*DBHST+0.00084*2.47*RemovalsST)/2
                TPCGingras88 = max(1,min(TreesInReachGingras88,ObsTreesPerCycleGingras88))
                TPPMHGingras88 = (127.8+21.2*TPCGingras88-63.1*UnmerchMerchGingras88+0.033*285)/(1+CSlopeFB_Harv)


                TreesInReachHartsough97 = RemovalsST*math.pi*24**2/43560
                TreesPAccumHartsough97 = max(1,1.81-0.0664*DBHST+3.64/DBHST-0.0058*20.0)
                MoveFracHartsough97 = 0.5/(math.trunc(TreesInReachHartsough97/TreesPAccumHartsough97)+1)
                MoveHartsough97 = 0.192+0.00779*(24+DistBetweenTrees)
                TimeFellHartsough97 = 0.285+0.126*TreesPAccumHartsough97+0.0176*DBHST*TreesPAccumHartsough97
                TPAccumHartsough97 = MoveFracHartsough97*MoveHartsough97+TimeFellHartsough97
                TPTHartsough97 = (TPAccumHartsough97*(1+0.0963)/TreesPAccumHartsough97)*(1+CSlopeFB_Harv)

                # Calculate Volume per PMH
                FBDVolumePMHJohnson79 = volumePMH (TreeVolST, TPTJohnson79)
                FBDVolumePMHGreene911 = volumePMH (TreeVolST, TPTGreene911)
                FBDVolumePMHGreene912 = volumePMH (TreeVolST, TPTGreene912)
                FBDVolumePMHHartsough01 = TreeVolST * TPPMHHartsough01
                FBSVolumePMHJohnson88 = volumePMH (TreeVolST, TPTJohnson88)
                FBSVolumePMHGingras88 = TreeVolST*TPPMHGingras88
                FBSVolumePMHGonsier87 = volumePMH (TreeVolST, TPTGonsier87)
                FBSVolumePMHGingras96 = (50.338/0.028317*(TreeVolST*0.028317)**0.3011)/(1+CSlopeFB_Harv+CRemovalsFB_Harv)
                FBSVolumePMHPlamondon98 =(5.0/0.028317+57.7*TreeVolST)/(1.0+CSlopeFB_Harv+CRemovalsFB_Harv)
                FBSVolumePMHHartsough97 = volumePMH (TreeVolST, TPTHartsough97)

                # Felling Cost ($/ ccf)
                costPMHFBSw=costPMHFBSB*NonSelfLevelCabDummy+costPMHFBSL*(1-NonSelfLevelCabDummy)

                CostFellBunch = round((CHardwoodST*100*
                    (costPMHFBDTT*relevanceFBDJohnson79
                     +costPMHFBDTT*relevanceFBDGreene911
                     +costPMHFBDTT*relevanceFBDGreene912
                     +costPMHFBDTT*relevanceFBDHartsough01
                     +costPMHFBSw*relevanceFBSJohnson88
                     +costPMHFBSw*relevanceFBSGingras88
                     +costPMHFBSL*relevanceFBSGonsier87
                     +costPMHFBSw*relevanceFBSGingras96
                     +costPMHFBSw*relevanceFBSPlamondon98
                     +costPMHFBSw*relevanceFBSHartsough97)/
                    (relevanceFBDJohnson79*FBDVolumePMHJohnson79
                     +relevanceFBDGreene911*FBDVolumePMHGreene911
                     +relevanceFBDGreene912*FBDVolumePMHGreene912
                     +relevanceFBDHartsough01*FBDVolumePMHHartsough01
                     +relevanceFBSJohnson88*FBSVolumePMHJohnson88
                     +relevanceFBSGingras88*FBSVolumePMHGingras88
                     +relevanceFBSGonsier87*FBSVolumePMHGonsier87
                     +relevanceFBSGingras96*FBSVolumePMHGingras96
                     +relevanceFBSPlamondon98*FBSVolumePMHPlamondon98
                     +relevanceFBSHartsough97*FBSVolumePMHHartsough97)), 2)

            else:
                CostFellBunch = 0

            return CostFellBunch


        ################################################
        # Cable Yarding  Clearcut, Unbunched           #
        ################################################
        def CostYardCCUBfunc():

            # Relevance
            # Idaho Jammer (Schillings, 69)
            if LogVol<5:
                relevanceCYCUSchillings69 = 0
            elif LogVol<10:
                relevanceCYCUSchillings69 = -1+LogVol/5.0
            elif LogVol<50:
                relevanceCYCUSchillings69 = 1
            elif LogVol<100:
                relevanceCYCUSchillings69 = 2-LogVol/50.0
            else:
                relevanceCYCUSchillings69 = 1

            # Idaho Jammer (Hensel&Johnson, 79)
            if LogVol<5:
                relevanceCYCUHensel791 = 0
            elif LogVol<10:
                relevanceCYCUHensel791 = -1+LogVol/5.0
            else:
                relevanceCYCUHensel791 = 1

            # LinkBelt 98 Live Skyline (Hensel&Johnson, 79)
            if LogVol<5:
                relevanceCYCUHensel792 = 0
            elif LogVol<10:
                relevanceCYCUHensel792 = -1+LogVol/5.0
            else:
                relevanceCYCUHensel792 = 1

            # Skagit GT3 Running Skyline (Hensel&Johnson, 79)
            if LogVol<5:
                relevanceCYCUHensel793 = 0
            elif LogVol<10:
                relevanceCYCUHensel793 = -1+LogVol/5.0
            else:
                relevanceCYCUHensel793 = 1

            # Skagit GT3 Running Skyline (Gardner, 80)
            if LogVol<30:
                relevanceCYCUGardner801 = 1
            elif LogVol<60:
                relevanceCYCUGardner801 = 2-LogVol/30.0
            else:
                relevanceCYCUGardner801 = 0

            #  LinkBelt 78 Shotgun Live Skyline (Gardner, 80)
            if LogVol<30:
                relevanceCYCUGardner802 = 1
            elif LogVol<60:
                relevanceCYCUGardner802 = 2-LogVol/30.0
            else:
                relevanceCYCUGardner802 = 0

            if Slope<30:
                relevanceCYCUGardner802 = 0
            elif Slope<40:
                relevanceCYCUGardner802 = relevanceCYCUGardner802*(Slope/10-3)
            else:
                relevanceCYCUGardner802 = 1

            # Washington SLH78 (Andersson, B. and G. Young. 98)
            if TreeVol<80:
                relevanceCYCUAndersson98 = 1
            elif TreeVol<160:
                relevanceCYCUAndersson98 = 2-TreeVol/80.0
            else:
                relevanceCYCUAndersson98 = 0

            relevanceCaYCU = []
            relevanceCaYCU.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceCYCU'))


            # Turn Time
            TurnArea = 800.0
            AreaLimitedTurnVol = VolPerAcre*TurnArea/43560.0

            LogsSchillings69 = 1.0
            TurnVolSchillings69 = LogVol*LogsSchillings69
            TTSchillings69 = 0.321+0.00285*SkidDist+0.009906*Slope

            LogsHensel791 = 1.0
            TurnVolHensel791 = LogVol*LogsHensel791
            TTHensel791 = (72.26+0.0638*BFperCF*LogVol+0.1152*SkidDist-996/(max(20.0,Slope)))/60.0

            YarderCapacity = (6000+ManualMachineSize*3000)/WoodDensity
            TurnVolHensel792 = min(YarderCapacity,max(AreaLimitedTurnVol,TreeVol))
            LogsHensel792 = max(1.0,(TurnVolHensel792/LogVol))
            TTHensel792 = (177.3+0.3568*LogVol+0.000522*SkidDist**2+0.0105*Slope**2)/60.0

            TurnVolHensel793 = min(YarderCapacity,max(AreaLimitedTurnVol,TreeVol))
            LogsHensel793 = max(1.0,(TurnVolHensel793/LogVol))
            TTHensel793= (164+0.04872*BFperCF*LogVol+0.000405*SkidDist**2.0+607.0/(max(20.0,Slope)))/60.0

            TurnVolGardner801 = min(YarderCapacity,max(AreaLimitedTurnVol,TreeVol))
            LogsGardner801 = max(1.0,(TurnVolGardner801/LogVol))
            TTGardner801 = math.exp(1.09+0.0196*LogsGardner801+0.00106*SkidDist+0.000617*TurnVolGardner801+0.000043*5*Slope)

            TurnVolGardner802 = min(YarderCapacity,max(AreaLimitedTurnVol,TreeVol))
            LogsGardner802 = max(1.0,(TurnVolGardner802/LogVol))
            TTGardner802 = math.exp(1.91+0.000545*SkidDist-0.0068*Slope+0.00212*TurnVolGardner802-0.416/(max(1.0,LogsGardner802)))

            TurnVolAnderson98 = min(YarderCapacity,max(AreaLimitedTurnVol,TreeVol))
            LogsAnderson98 = max(1,(TurnVolAnderson98/LogVol))
            DelayFrac = 0.042
            TTAnderson98 = (1+DelayFrac)*(0.31+0.00323*SkidDist+1.593+1.24*math.log10(LogsAnderson98)+0.326+0.107*LogsAnderson98+0.021)

            # Calculate Volume per PMH
            CYCUVolumePMHSchillings69 = volumePMH (TurnVolSchillings69, TTSchillings69)
            CYCUVolumePMHHensel791 = volumePMH (TurnVolHensel791, TTHensel791)
            CYCUVolumePMHHensel792 = volumePMH (TurnVolHensel792, TTHensel792)
            CYCUVolumePMHHensel793 = volumePMH (TurnVolHensel793, TTHensel793)
            CYCUVolumePMHGardner801 = volumePMH (TurnVolGardner801, TTGardner801)
            CYCUVolumePMHGardner802 = volumePMH (TurnVolGardner802, TTGardner802)
            CYCUVolumePMHAnderson98 = volumePMH (TurnVolAnderson98, TTAnderson98)
            volumeCaYCU = []
            volumeCaYCU.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('CYCUVolumePMH'))

            # Cable Yarding, Clearcut, Unbunched Cost ($/ ccf)
            arealineshiftJam = 50.0*2.0*SkidDist/43560.0
            arealineshiftLive = 70.0/2.0*1.5*SkidDist/43560.0
            lineshiftcostLive = 100*(YarderHourlyCost*0.5)/(VolPerAcre*arealineshiftLive)
            arealanding = math.pi/2.0*((1.5*SkidDist)**2.0)/43560.0
            landingshiftcostLive = 100.0*(YarderHourlyCost*2.0)/(VolPerAcre*arealanding)
            arealineshiftRun = arealineshiftLive
            lineshiftcostRun = 100.0*(YarderHourlyCost*0.25)/(VolPerAcre*arealineshiftRun)
            landingshiftcostRun = 100.0*(YarderHourlyCost*2.0)/(VolPerAcre*arealanding)
            CCRunSLChangeCost = lineshiftcostRun+landingshiftcostRun
            
            CCLiveSLChangeCost = lineshiftcostLive+landingshiftcostLive
            CCJammerChangeCost = 100.0*(costPMHYS*0.5)/(VolPerAcre*arealineshiftJam)
            CostCYCUSchillings69 = 100.0*costPMHYS/CYCUVolumePMHSchillings69+CCJammerChangeCost
            CostCYCUHensel791 = 100.0*costPMHYS/CYCUVolumePMHHensel791+CCJammerChangeCost
            CostCYCUHensel792 = 100.0*YarderHourlyCost/CYCUVolumePMHHensel792+CCLiveSLChangeCost
            CostCYCUHensel793 = 100.0*YarderHourlyCost/CYCUVolumePMHHensel793+CCRunSLChangeCost
            CostCYCUGardner801 = 100.0*YarderHourlyCost/CYCUVolumePMHGardner801+CCRunSLChangeCost
            CostCYCUGardner802 = 100.0*YarderHourlyCost/CYCUVolumePMHGardner802+CCLiveSLChangeCost
            CostCYCUAnderson98 = 100.0*YarderHourlyCost/CYCUVolumePMHAnderson98+CCRunSLChangeCost

            costCaYCU = []
            costCaYCU.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('CostCYCU'))

            WeightingProductYardCUB = sum([x * y * z for x, y, z in zip(relevanceCaYCU, volumeCaYCU, costCaYCU)])
            WeightingDivisiorYardPCUB = sum([x * y  for x, y in zip(relevanceCaYCU, volumeCaYCU)])

            CostYardCCUB =  round (WeightingProductYardCUB/ WeightingDivisiorYardPCUB, 2)

            return CostYardCCUB


        ################################################
        # Cable Yarding  Partialcut, Unbunched         # 
        ################################################
        def CostYardPCUBfunc(): 
            TurnArea = 800.0
            AreaLimitedTurnVol = VolPerAcre*TurnArea/43560.0
            YarderCapacity = (6000+ManualMachineSize*3000)/WoodDensity
            TurnVol = min(YarderCapacity,max(AreaLimitedTurnVol,TreeVol))
            Logs = max(1.0,(TurnVol/LogVol))
            TurnEndAre = 2.0*TurnVol/LogLength
            DeckHeight = 5.0

            # Relevance
            # Clearwater Shotgun Live Skyline (Johnson&Lee, 88)
            if TreeVol<10:
                relevanceCYPUJohnson88 = 1
            elif TreeVol<20:
                relevanceCYPUJohnson88 = 2-TreeVol/10.0
            else:
                relevanceCYPUJohnson88 = 0

            # Madill 071 Live Skyline w/Danebo MSP (Kellogg,Olsen&Hargrave, 86)
            if TurnVol<200:
                relevanceCYPUKellogg86 = 1
            elif TurnVol<400:
                relevanceCYPUKellogg86v = 2-TurnVol/200.0
            else:
                relevanceCYPUKellogg86 = 0

            # Skagit GT3 Running Skyline, Shelterwood (Gardner, 80)
            if LogVol<30:
                relevanceCYPUGardner801 = 1
            elif LogVol<60:
                relevanceCYPUGardner801 = 2-LogVol/30.0
            else:
                relevanceCYPUGardner801 = 0

            # LinkBelt 78 Shotgun Live Skyline, Group Selection (Gardner, 80)
            if LogVol<30:
                relevanceCYPUGardner802 = 1
            elif LogVol<60:
                relevanceCYPUGardner802 = 2-LogVol/30.0
            else:
                relevanceCYPUGardner802 = 0

            if Slope<30:
               relevanceCYPUGardner803 = 0
            elif Slope<40:
                relevanceCYPUGardner803 = relevanceCYPUGardner802 *(Slope/10-3)
            else:
                relevanceCYPUGardner803 = relevanceCYPUGardner802

            # Madill 044 w/Bowman Mark Vd (Boswell, B. 01)
            if TreeVol<90:
                relevanceCYPUBoswell01 = 1
            elif TreeVol<180:
                relevanceCYPUBoswell01 = 2-TreeVol/90.0
            else:
                relevanceCYPUBoswell01 = 0

            #  Skylead C40 w/Mini-Maki II (Pavel, M. 99)
            if TreeVol<90:
                relevanceCYPUPavel99 =1
            elif TreeVol<180:
                relevanceCYPUPavel99 = 2-TreeVol/90.0
            else:
                relevanceCYPUPavel99 = 0

            # Koller K501 w/Koller SKA 2.5 manual slackpulling carriage  (Yachats site: Kellogg, L., G. Milota and M. Miller. 96.)
            if TreeVol<60:
                relevanceCYPUKellogg96 = 1
            elif TreeVol<120:
                relevanceCYPUKellogg96 = 2-TreeVol/60.0
            else:
                relevanceCYPUKellogg96 = 0

            #  Koller K501 w/Eaglet mechanical slackpulling carriage (Kellogg, L., Miller, M. and E. Olsen. 99)
            if TreeVol<70:
                relevanceCYPUKellogg99 = 1
            elif TreeVol<140:
                relevanceCYPUKellogg99 = 2-TreeVol/70.0
            else:
                relevanceCYPUKellogg99 = 0

            #  (Huyler, N. and C. LeDoux. 1997)
            if TreeVol<5:
                relevanceCYPUHuyler97 = 0
            elif TreeVol<10:
                relevanceCYPUHuyler97 = -1+TreeVol/5.0
            elif TreeVol<40:
                relevanceCYPUHuyler97 = 1
            elif TreeVol<80:
                relevanceCYPUHuyler97 = 2-TreeVol/40.0
            else:
                relevanceCYPUHuyler97 = 0

            # LeDoux, C. 1985
            relevanceCYPULeDoux851 = 0

            # Bitterroot Yarder-LeDoux 1985
            relevanceCYPULeDoux852 = 0

            # Clearwater Yarder-LeDoux 1985
            relevanceCYPULeDoux853 = 0

            # Ecologger-LeDoux 1985
            relevanceCYPULeDoux854 = 0

            # Skylok 78-LeDoux 1985
            relevanceCYPULeDoux855 = relevanceCYPULeDoux854

            relevanceCaYPU = []
            relevanceCaYPU.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceCYPU'))

            # Turn Time
            LatDist = 35.0
            TTJohnson88 = 1.51+0.012*TurnVol+0.011*DeckHeight*Logs+0.021*DeckHeight*TurnEndAre+0.004*(SkidDist+LatDist)+0.0002*LatDist**2
            TTKellogg86 = 1.82+0.0024*SkidDist+0.00021*LatDist**2+0.0125*TurnVol+0.0151*Slope+1.05
            TTGardner801 = math.exp(1.46+0.000486*SkidDist+0.00114*LatDist+0.00000896*WoodDensity*TurnVol)
            TTGardner802 = math.exp(0.58+0.192*math.log(SkidDist)-0.00308*Slope+0.00193*LatDist+0.000004*Logs*WoodDensity*TurnVol)
            TTGardner803 = math.exp(1.813+0.00094*SkidDist-0.0095*Slope+0.00172*LatDist+0.00000277*Logs*WoodDensity*TurnVol)
            TTBoswell01 = 3.73+0.0028*SkidDist+0.154*LatDist
            TTPavel99 = 2.761+0.0014*SkidDist+0.0114*LatDist
            TTKellogg96 = 2.341+0.0017*SkidDist+0.012*LatDist+0.722+0.191*Logs
            TTKellogg99 = 0.231+0.003*SkidDist+0.01*LatDist+0.017*40+0.141*Logs+0.012*Slope-0.668
            TTHuyler97 = 0.223+0.004*SkidDist+0.024*LatDist+0.059*TurnVol+35.23/TreeVol


            # Calculate Volume per PMH
            CYPUVolumePMHJohnson88 = volumePMH (TurnVol, TTJohnson88)
            CYPUVolumePMHKellogg86 = volumePMH (TurnVol, TTKellogg86)
            CYPUVolumePMHGardner801 = volumePMH (TurnVol, TTGardner801)
            CYPUVolumePMHGardner802 = volumePMH (TurnVol, TTGardner802)
            CYPUVolumePMHGardner803 = volumePMH (TurnVol, TTGardner803)
            CYPUVolumePMHBoswell01 = volumePMH (TurnVol, TTBoswell01)
            CYPUVolumePMHPavel99 = volumePMH (TurnVol, TTPavel99)
            CYPUVolumePMHKellogg96 = volumePMH (TurnVol, TTKellogg96)
            CYPUVolumePMHKellogg99 = volumePMH (TurnVol, TTKellogg99)
            CYPUVolumePMHHuyler97 = volumePMH (TurnVol, TTHuyler97)
            CYPUVolumePMHLeDoux851 = 44.09/(-0.089289+(81.991053/VolPerAcre)+(0.000269*SkidDist)+(-496.820821/(VolPerAcre*DBH))+(1.535553/DBH))
            CYPUVolumePMHLeDoux852 = 23.61/(0.161995+(0.000783*DBH*DBH)+(0.000172*SkidDist))
            CYPUVolumePMHLeDoux853 = 70.45/(0.12577+(-0.00328*DBH)+(0.000048*SkidDist)+(623.08404/(VolPerAcre*DBH)))
            CYPUVolumePMHLeDoux854 = 55.77/(0.707187+(-0.050285*DBH)+(0.001089*DBH*DBH)+(33.101018/VolPerAcre)+(0.000168*SkidDist)+(-2.095831/DBH))
            CYPUVolumePMHLeDoux855 = 121.65/(0.090775+(0.000071*SkidDist)+(739.473795/(VolPerAcre*DBH))+(0.594844/DBH))

            volumeCaYPU = []
            volumeCaYPU.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('CYPUVolumePMH'))

            # Cable Yarding, PartialCut, Unbunched Cost ($/ ccf)
            Corridorspacing = 150.0
            Areacorridorchange = SkidDist*2*Corridorspacing/43560.0
            Corridorchangetime = 1.00
            PCRunSLChangeCost = 100.0*(YarderHourlyCost*Corridorchangetime)/(VolPerAcre*Areacorridorchange)

            Corridorchangetime = 1.5
            PCLiveStandSLChangeCost = 100.0*(YarderHourlyCost*Corridorchangetime)/(VolPerAcre*Areacorridorchange)

            CostCYPUJohnson88 = 100.0*YarderHourlyCost/CYPUVolumePMHJohnson88+PCRunSLChangeCost
            CostCYPUKellogg86 = 100.0*YarderHourlyCost/CYPUVolumePMHKellogg86+PCLiveStandSLChangeCost
            CostCYPUGardner801 = 100.0*YarderHourlyCost/CYPUVolumePMHGardner801+PCRunSLChangeCost
            CostCYPUGardner802 = 100.0*YarderHourlyCost/CYPUVolumePMHGardner802+PCRunSLChangeCost
            CostCYPUGardner803 = 100.0*YarderHourlyCost/CYPUVolumePMHGardner803+PCLiveStandSLChangeCost
            CostCYPUBoswell01 = 100.0*YarderHourlyCost/CYPUVolumePMHBoswell01+PCLiveStandSLChangeCost
            CostCYPUPavel99 = 100.0*YarderHourlyCost/CYPUVolumePMHPavel99+PCLiveStandSLChangeCost
            CostCYPUKellogg96 = 100.0*YarderHourlyCost/CYPUVolumePMHKellogg96+PCLiveStandSLChangeCost
            CostCYPUKellogg99 = 100.0*YarderHourlyCost/CYPUVolumePMHKellogg99+PCLiveStandSLChangeCost
            CostCYPUHuyler97 = 100.0*YarderHourlyCost/CYPUVolumePMHHuyler97+PCLiveStandSLChangeCost
            CostCYPULeDoux851 = 100.0*YarderHourlyCost/CYPUVolumePMHLeDoux851+PCLiveStandSLChangeCost
            CostCYPULeDoux852 = 100.0*YarderHourlyCost/CYPUVolumePMHLeDoux852+PCLiveStandSLChangeCost
            CostCYPULeDoux853 = 100.0*YarderHourlyCost/CYPUVolumePMHLeDoux853+PCRunSLChangeCost
            CostCYPULeDoux854 = 100.0*YarderHourlyCost/CYPUVolumePMHLeDoux854+PCRunSLChangeCost
            CostCYPULeDoux855 = 100.0*YarderHourlyCost/CYPUVolumePMHLeDoux855+PCRunSLChangeCost

            costCaYPU = []
            costCaYPU.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('CostCYPU'))

            WeightingProductYardPCUB = sum([x * y * z for x, y, z in zip(relevanceCaYPU, volumeCaYPU, costCaYPU)])
            WeightingDivisiorYardPCUB = sum([x * y  for x, y in zip(relevanceCaYPU, volumeCaYPU)])

            CostYardPCUB =  round (WeightingProductYardPCUB/ WeightingDivisiorYardPCUB, 2)

            return CostYardPCUB


        ################################################
        # Helicopter Yarding Manual Log-Length         #
        ################################################
        def CostHelifunc():
            # Relevance Helicopter Yarding
            if TreeVol<75:
                relevanceHYBell = 1.0
            elif TreeVol<150:
                relevanceHYBell = 2.0-TreeVol/75.0
            else:
                relevanceHYBell = 0.0

            relevanceHYBoeing = relevanceHYBell
            relevanceHYKmax = relevanceHYBell

            relevanceHeliYarding = []
            relevanceHeliYarding.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceHY'))

            # Helicpoter  Assumptions and Inputs
            HookAreaDiam = 75.0
            ExtraServiceFlightDist = 5000.0
            HeliCruiseSpeed = 20.0

            # Helicopter Calculated Values
            HookArea = math.pi*(HookAreaDiam/2.0)**2/43506.0
            WtInHook_Area = HookArea*VolPerAcre*WoodDensity
            WtSTInHook_Area = HookArea*VolPerAcreST*WoodDensityST
            VolInHookArea = WtInHook_Area/WoodDensity

            LogWt = WoodDensity*LogVol
            LogWtST = WoodDensityST*LogVolST

            # Flight Time and Related Assumptions			
            FlightTimeBell = 6.0
            FlightTimeBoeing = 6.76
            FlightTimeKmax = 8.5
            ServiceCyclesPD = 7.0
            YardingSpeedBell = 39.0
            YardingSpeedBoeing = 58.0
            YardingSpeedKmax = 60.0

            #Cost Assumptions			
            FixedCPDBell = 3700
            FixedCPDBoeing = 7580
            FixedCPDKmax = 6750
            VariableCPHBell = 340
            VariableCPHBoeing = 1052
            VariableCPHKmax = 840
            SupportCPDBell = 460
            SupportCPDBoeing = 2155
            SupportCPDKmax = 1000
            LaborCPPD = 263
            WoodsLandingLaborersBell = 6
            WoodsLandingLaborersBoeing = 10
            WoodsLandingLaborersKmax = 9
            ProfitRiskFraction = 0.1
            LoaderCPD = 770
            LoadersBell = 1
            LoadersBoeing = 2
            LoadersKmax = 2

            # Helicopter Cost Calculations
            def HeliCostCalFunc (VariableCPH, FlightTime, FixedCPD, WoodsLandingLaborers, SupportCPD):
                VariableCPD = VariableCPH*FlightTime
                FixedCPH = FixedCPD/FlightTime
                FixedVarCPH = FixedCPH+VariableCPH
                LaborCPD = LaborCPPD*WoodsLandingLaborers
                HeliYardCostPD = round ((1+ProfitRiskFraction)*(FixedCPD+VariableCPD+SupportCPD+LaborCPD))
                return HeliYardCostPD

            HeliYardCostPDBell = HeliCostCalFunc (VariableCPHBell,FlightTimeBell, FixedCPDBell, WoodsLandingLaborersBell, SupportCPDBell)
            HeliYardCostPDBoeing = HeliCostCalFunc (VariableCPHBoeing,FlightTimeBoeing, FixedCPDBoeing, WoodsLandingLaborersBoeing, SupportCPDBoeing)
            HeliYardCostPDKmax = HeliCostCalFunc (VariableCPHKmax,FlightTimeKmax, FixedCPDKmax, WoodsLandingLaborersKmax, SupportCPDKmax)

            # Helicopter Precalculations

            ObservedAvgAtElevBell = -0.116*Elevation+4500
            ObservedAvgAtElevBoeing = -0.0352*Elevation+8160
            ObservedAvgAtElevKMax = -0.0046*Elevation+4800.9

            LoadUnloadBell = 1.63
            LoadUnloadBoeing = 1.18
            LoadUnloadKmax = 1.15

            ### Manual Log-Length ###

            def CCFHeliYardPDMLFunc (ObservedAvgAtElev, LoadUnload, FlightTime, YardingSpeed):
                #Payload Calculations
                LogWtMaxPayload = LogWt/(1.25*ObservedAvgAtElev)
                MaxPayloadsHookArea = WtInHook_Area/(1.25*ObservedAvgAtElev)
                if MaxPayloadsHookArea<4:
                    LoadAdjustFactor = (-0.05+(0.05/3)*(MaxPayloadsHookArea-1))
                else:
                    LoadAdjustFactor = 0
                if MaxPayloadsHookArea<1:
                    LoadAdjustFactor = LoadAdjustFactor* MaxPayloadsHookArea
                else:
                    LoadAdjustFactor = LoadAdjustFactor
                if LogWtMaxPayload<0.5:
                    LoadAdjustFactor = LoadAdjustFactor + 0.9 + 0.1 - 0.2 * LogWtMaxPayload
                else:
                    LoadAdjustFactor = LoadAdjustFactor + 0.9
                AfterAdjustment = LoadAdjustFactor*ObservedAvgAtElev
                AfterOneLogMinCheck = max(AfterAdjustment,(min(LogWt,ObservedAvgAtElev)))
                AfterTenLogMaxCheck = round(min((10*LogWt),AfterOneLogMinCheck))

                # Cycle Time Calculations
                TravEmptyLoadedHeliYardML = 2*60*SkidDist/(YardingSpeed*5280)
                TotalCycleTimeHeliYard = LoadUnload+TravEmptyLoadedHeliYardML

                ServiceFlightTime = ServiceCyclesPD*2*60*ExtraServiceFlightDist/(YardingSpeed*5280)
                TuPDHeliYard =(60*FlightTime-ServiceFlightTime)/TotalCycleTimeHeliYard
                TPDHeliYard= AfterTenLogMaxCheck*TuPDHeliYard/2000

                # Helicopter Yarding, Manual Log-Length (CCF/ per day)
                CCFHeliYardPD = TPDHeliYard*2000/(WoodDensity*100)
                return CCFHeliYardPD

            CCFHeliYPDMLBell = CCFHeliYardPDMLFunc(ObservedAvgAtElevBell, LoadUnloadBell, FlightTimeBell, YardingSpeedBell)
            CCFHeliYPDMLBoeing = CCFHeliYardPDMLFunc(ObservedAvgAtElevBoeing, LoadUnloadBoeing, FlightTimeBoeing, YardingSpeedBoeing)
            CCFHeliYPDMLKmax = CCFHeliYardPDMLFunc(ObservedAvgAtElevKMax, LoadUnloadKmax, FlightTimeKmax, YardingSpeedKmax)

            CCFHYML = []
            CCFHYML.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('CCFHeliYPDML'))

            # Helicopter Yarding, Manual Log-Length ($/ ccf)
            CostHYardMLBell = HeliYardCostPDBell/ CCFHeliYPDMLBell
            CostHYardMLBoeing = HeliYardCostPDBoeing/ CCFHeliYPDMLBoeing
            CostHYardMLKmax = HeliYardCostPDKmax/ CCFHeliYPDMLKmax

            costHYML = []
            costHYML.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('CostHYardML'))

            WeightingProductHeliML = sum([x * y * z for x, y, z in zip(relevanceHeliYarding, CCFHYML, costHYML)])
            WeightingDivisiorHeliML = sum([x * y  for x, y in zip(relevanceHeliYarding, CCFHYML)])

            CostHeliYardML = round(CHardwood*WeightingProductHeliML/ WeightingDivisiorHeliML, 2)
 
            ### Load Manual Log-Lenght
            HeliLoaderCostPDBell =(1+ProfitRiskFraction)*LoadersBell*(LaborCPPD+LoaderCPD)
            HeliLoaderCostPDBoeing =(1+ProfitRiskFraction)*LoadersBoeing*(LaborCPPD+LoaderCPD)		
            HeliLoaderCostPDKmax =(1+ProfitRiskFraction)*LoadersKmax*(LaborCPPD+LoaderCPD)		

            costHLoadMLPDBell = HeliLoaderCostPDBell/CCFHeliYPDMLBell
            costHLoadMLPDBoeing = HeliLoaderCostPDBoeing/CCFHeliYPDMLBoeing
            costHLoadMLPDKmax = HeliLoaderCostPDKmax/CCFHeliYPDMLKmax

            costHLML = []
            costHLML.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('costHLoadMLPD'))

            WeightingProductHeliLoadML = sum([x * y * z for x, y, z in zip(relevanceHeliYarding, CCFHYML, costHLML)])
            WeightingDivisiorHeliLoad = sum([x * y  for x, y in zip(relevanceHeliYarding, CCFHYML)])

            CostHeliLoadML = round(CHardwood*WeightingProductHeliLoadML/ WeightingDivisiorHeliLoad, 2)

            return CostHeliYardML, CostHeliLoadML


        ################################################
        # Process                                      #
        ################################################
        def CostProcessfunc():
            if TreeVolST>0:
                # Relevance
                # Hahn Stroke Processor (Gonsier&Mandzak, 87)
                if DBHSLT<15:
                    relevanceProGonsier87= 1.0
                elif DBHSLT<20:
                    relevanceProGonsier87 = 4.0-DBHSLT/5.0
                else:
                    relevanceProGonsier87 = 0

                #  Stroke Processor (MacDonald, 90)
                if ButtDiamSLT<20:
                    relevanceProMacDonald90 = 1.0
                elif ButtDiamSLT<30:
                    relevanceProMacDonald90 = 3.0-ButtDiamSLT/10.0
                else:
                    relevanceProMacDonald90 = 0

                # Roger Stroke Processor (Johnson, 88)
                relevanceProJohnson881 = 1

                #  Harricana Stroke Processor (Johnson, 88)
                relevanceProJohnson882 = 1

                #  Hitachi EX150/Keto 500 (Schroder&Johnson, 97)
                if TreeVolSLT<50:
                    relevanceProSchroder97 = 1
                elif TreeVolSLT<100:
                    relevanceProSchroder97 = 2-TreeVolSLT/50.0
                else:
                    relevanceProSchroder97 = 0

                # FERIC Generic (Gingras, J.F. 96)
                relevanceProGingras96 = 1

                # Valmet 546 Woodstar Processor (Holtzscher, M. and B. Lanford 1997)
                if TreeVolSLT<20:
                    relevanceProHoltzscher97 = 1
                elif TreeVolSLT<40:
                    relevanceProHoltzscher97 = 2-TreeVolSLT/20.0
                else:
                    relevanceProHoltzscher97 = 0

                relevanceP = []
                relevanceP.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevancePro'))

                # Time per Tree
                TPTGonsier87 = 1.26*(0.232+0.0494*DBHSLT)
                TPTMacDonald90 = 0.153+0.0145*ButtDiamSLT
                TPTJohnson881 = -0.05+0.6844*LogsPerTreeSLT+5*10**(-8)*TreeVolSLT**2
                TPTJohnson882 = -0.13+0.001*ButtDiamSLT**2+0.5942*LogsPerTreeSLT
                TPTSchroder97 = (0.67+0.0116*TreeVolSLT)**2
                TPTHoltzscher97 = -0.341+0.1243*DBHSLT

                # Skidding Volume/ PMH (ccf)
                ProVolPMHGonsier87 = volumePMH (TreeVolSLT, TPTGonsier87)
                ProVolPMHMacDonald90 = volumePMH (TreeVolSLT, TPTMacDonald90)
                ProVolPMHJohnson881 = volumePMH (TreeVolSLT, TPTJohnson881)
                ProVolPMHJohnson882 = volumePMH (TreeVolSLT, TPTJohnson882)
                ProVolPMHSchroder97 = volumePMH (TreeVolSLT, TPTSchroder97)
                ProVolPMHGingras96 = (41.16/0.02832)*(TreeVolSLT/35.31)**0.4902
                ProVolPMHHoltzscher97 = volumePMH (TreeVolSLT, TPTHoltzscher97)

                volumeP = []
                volumeP.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('ProVolPMH'))

                # Processing cost ($/ ccf)
                CostProcess = round(CHardwoodSLT*relevancefunction(ProcessorHourlyCost, relevanceP, volumeP) ,2)

            else:
                CostProcess = 0
                
            return CostProcess


        ################################################
        # Chipping Whole Trees                         #
        ################################################
        def CostChipWTfunc():
            if TreeVolCT>0:
                #General Input
                TreeWeightDry = TreeVolCT*WoodDensityCT*(1-MoistureContent)
                ExchangeVans = 5.3
                LoadWeightDry = LoadWeightChip*(1-MoistureContent)

                # Relevance Input
                # Johnson, 89
                relevanceChipWTJohnson89 = 1
                # Morbark 22 (Hartsough, unpublished)
                relevanceChipWTHartsough = 1
                # Morbark 60/36 (Hartsough et al, 97)
                if TreeWeightDry<400:
                    relevanceChipWTHartsough97 = 1
                elif TreeWeightDry<800:
                    relevanceChipWTHartsough97 = 2-TreeWeightDry/400
                else:
                    relevanceChipWTHartsough97 = 0

                relevanceCWT = []
                relevanceCWT.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceChipWT'))

                # Chipping Volume/ PMH (ccf)
                ChipperHP = min(700,max(200,(100+100*(TreeVolCT)**0.5)))
                GTPMH = -17+ChipperHP/6
                ChipWTVolPMHJohnson89 = GTPMH*2000/WoodDensityCT
                ChipWTVolPMHHartsough = min(4000,463*TreeVolCT**0.668)
                LogPSwing = 1.2+338/TreeWeightDry
                ChipTimeSwing = 0.25+0.0264*LogPSwing+0.000498*TreeWeightDry

                TimePVan = ChipTimeSwing*(1+0.038)/(TreeWeightDry*LogPSwing)*2000*LoadWeightDry+(0.93+ExchangeVans)
                ChipWTVolPMHHartsough97 = LoadWeightChip/(WoodDensityCT/2000)/(TimePVan/60)

                volumeCWT = []
                volumeCWT.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('ChipWTVolPMH'))

                # Chipping cost whole tree ($/ ccf)
                CostChipWT = round(CHardwoodCT*relevancefunction(ChipperHourlyCost, relevanceCWT, volumeCWT), 2)    

            else:
                CostChipWT = 0

            return CostChipWT


        ################################################
        # Loading                                      #
        ################################################
        def CostLoadfunc():
            if RemovalsALT > 0: 
                # General Inputs

                ExchangeTrucks = 5.0

                # Loading Calculated Values
                LoadVolALT = LoadWeight*2000/(WoodDensityALT*100)
                LoadVolSLT = LoadWeight*2000/(WoodDensitySLT*100)

                ## I. Loading Full-Length Logs

                # Relevance
                # Front-End Loader (Vaughan, 89)
                if LogVolALT < 10:
                    relevanceLoadFLLVaughan89 = 0.0
                elif LogVolALT<40:
                    relevanceLoadFLLVaughan89 = -1.0/3.0+LogVolALT/30.0
                else:
                    relevanceLoadFLLVaughan89 = 1.0

                # Knuckleboom Loader, Small Logs (Brown&Kellogg, 96)
                if LogVolALT<10:
                    relevanceLoadFLLBrown96 = 1.0
                if LogVolALT<20:
                    relevanceLoadFLLBrown96 = 2.0-LogVolALT/10.0
                else:
                    relevanceLoadFLLBrown96 = 0.0

                # Loaders (Hartsough et al, 98)
                relevanceLoadFLLHartsough98 = 0.8

                # Loaders (Jackson et al, 84)
                if LogVolALT<75:
                    relevanceLoadFLLJackson84 = 1.0
                elif LogVolALT<100:
                    relevanceLoadFLLJackson84 = 4.0-LogVolALT/25.0
                else:
                    relevanceLoadFLLJackson84 = 0.0

                relevanceLdingFLL = []
                relevanceLdingFLL.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('relevanceLoadFLL'))

                # Time Loading
                LoadTimeVaughan89 = 22-0.129*LogVolALT+ExchangeTrucks
                LoadCCFPminBrown96 = 0.1+0.019*LogVolALT
                LoadTimeBrown96 = LoadVolALT/LoadCCFPminBrown96+ExchangeTrucks
                TimeCCFPminHartsough98 = 0.66+46.2/DBHALT
                LoadTimeHartsough98 = TimeCCFPminHartsough98*LoadVolALT

                # Loading Volume/ PMH (ccf)
                LoadFLLVolPMHVaughan89 = 100*volumePMH (LoadVolALT, LoadTimeVaughan89)
                LoadFLLVolPMHBrown96 = 100*volumePMH (LoadVolALT, LoadTimeBrown96)
                LoadFLLVolPMHHartsough98 = 6000/TimeCCFPminHartsough98
                LoadFLLVolPMHJackson84 = 100.0*(11.04+0.522*LogVolALT-0.00173*LogVolALT**2)

                volumeLdingFLL = []
                volumeLdingFLL.extend(value for name, value in sorted(locals().items(), key=lambda item: item[0]) if name.startswith('LoadFLLVolPMH'))

                CostLoad = round (CHardwood*relevancefunction(LoaderHourlyCost, relevanceLdingFLL, volumeLdingFLL), 2)

            else:
                CostLoad = 0

            return CostLoad


        ################################################
        # Final Calculations                           #
        ################################################
        if (RemovalsCT+RemovalsSLT+RemovalsLLT)>0 and (TreeVolCT+TreeVolSLT+TreeVolLLT)>0:

            ################################################
            # General Inputs                               #
            ################################################
            BFperCF = 5.0

            RemovalsALT = RemovalsSLT+RemovalsLLT
            RemovalsST = RemovalsCT+RemovalsSLT
            Removals = RemovalsCT+RemovalsSLT+RemovalsLLT

            VolPerAcreCT = RemovalsCT*TreeVolCT
            VolPerAcreLLT = RemovalsLLT*TreeVolLLT
            VolPerAcreSLT = RemovalsSLT*TreeVolSLT
            VolPerAcreST = VolPerAcreCT+VolPerAcreSLT
            VolPerAcre = VolPerAcreCT + VolPerAcreSLT + VolPerAcreLLT
            VolPerAcreALT = VolPerAcreSLT+VolPerAcreLLT

            DBHCT = ((TreeVolCT+3.675)/0.216)**0.5
            DBHSLT = ((TreeVolSLT+3.675)/0.216)**0.5
            DBHLLT = ((TreeVolLLT+3.675)/0.216)**0.5
            if RemovalsST>0:
                DBHST = ((RemovalsCT*(DBHCT**2.0)+RemovalsSLT*(DBHSLT**2.0))/RemovalsST)**0.5
            else:
                DBHST = 0
            if RemovalsALT>0:
                DBHALT = ((RemovalsSLT*(DBHSLT**2.0)+RemovalsLLT*(DBHLLT**2.0))/RemovalsALT)**0.5
            else:
                DBHALT = 0
            DBH =((RemovalsCT*(DBHCT**2.0)+RemovalsALT*(DBHALT**2.0))/Removals)**0.5

            ButtDiam=DBH+3.0
            ButtDiamSLT=DBHSLT+3.0
            ButtDiamST=DBHST+3.0

            LoadWeight = 25.0
            LoadWeightChip = 25.0
            MoistureContent = 0.5

            large_hardwood_fract = 0.0
            Large_log_tre_res_fract = 0.38 
            large_wood_density = 62.1225
            largetreeavgdbh = 0
            largetreebolewt = 0

            if VolPerAcreALT>0:
                HdwdFractionALT = (HdwdFractionSLT*VolPerAcreSLT+HdwdFractionLLT*VolPerAcreLLT)/VolPerAcreALT
            else:
                HdwdFractionALT = 0
            if VolPerAcreST>0:
                HdwdFractionST = (HdwdFractionCT*VolPerAcreCT+HdwdFractionSLT*VolPerAcreSLT)/VolPerAcreST
            else:
                HdwdFractionST = 0
            HdwdFraction =(HdwdFractionCT*VolPerAcreCT+HdwdFractionALT*VolPerAcreALT)/VolPerAcre
            HdwdCostPremium = 0.2
            CHardwood = 1.0+HdwdCostPremium*HdwdFraction
            CHardwoodALT = 1.0+HdwdCostPremium*HdwdFractionALT
            CHardwoodCT = 1.0+HdwdCostPremium*HdwdFractionCT
            CHardwoodLLT = 1.0+HdwdCostPremium*HdwdFractionLLT
            CHardwoodSLT = 1.0+HdwdCostPremium*HdwdFractionSLT
            CHardwoodST = 1.0+HdwdCostPremium*HdwdFractionST
                
            WoodDensityCT = 60.0
            WoodDensityLLT = 62.1225
            WoodDensitySLT = 58.6235
            if VolPerAcreST>0:
                WoodDensityST = (WoodDensityCT*VolPerAcreCT+WoodDensitySLT*VolPerAcreSLT)/VolPerAcreST
            else:
                WoodDensityST = 0
            if VolPerAcreALT>0:
                WoodDensityALT = (WoodDensitySLT*VolPerAcreSLT+WoodDensityLLT*VolPerAcreLLT)/VolPerAcreALT
            else:
                WoodDensityALT = 0
            if VolPerAcre>0:
                WoodDensity = (WoodDensityCT*VolPerAcreCT+WoodDensityALT*VolPerAcreALT)/VolPerAcre
            else:
                WoodDensity = 0

            LogLength = 32.0
            LogsPerTreeCT = 1.0
            LogsPerTreeLLT = max(1.0,(32.0/LogLength)*(-0.43+0.678*(DBHLLT)**0.5))
            LogsPerTreeSLT = max(1.0,(32.0/LogLength)*(-0.43+0.678*(DBHSLT)**0.5))            
            if RemovalsALT>0:
                LogsPerTreeALT = (LogsPerTreeSLT*RemovalsSLT+LogsPerTreeLLT*RemovalsLLT)/RemovalsALT 
                TreeVolALT = VolPerAcreALT/RemovalsALT 
                LogVolALT = TreeVolALT/LogsPerTreeALT
            else:
                LogsPerTreeALT = TreeVolALT = LogVolALT = 0
            if RemovalsST>0:
                LogsPerTreeST = (LogsPerTreeCT*RemovalsCT+LogsPerTreeSLT*RemovalsSLT)/RemovalsST
                TreeVolST = VolPerAcreST/RemovalsST
                LogVolST = TreeVolST/LogsPerTreeST
            else:
                LogsPerTreeST = TreeVolST = LogVolST = 0
            LogsPerTree =(LogsPerTreeCT*RemovalsCT+LogsPerTreeALT*RemovalsALT)/Removals
            TreeVol = VolPerAcre/Removals
            LogVol = TreeVol/LogsPerTree

            if Slope<15:
                NonSelfLevelCabDummy = 1.0
            elif Slope<35:
                NonSelfLevelCabDummy = 1.75-0.05*Slope
            else :
                NonSelfLevelCabDummy = 0.0

            CRemovalsFB_Harv = max(0,(0.66-0.001193*RemovalsST*2.47+5.357*10.0**(-7.0)*(RemovalsST*2.47)**2.0))

            CSlopeSkidForwLoadSize = 1.0-0.000127*Slope**2.0
            CSlopeFB_Harv = 0.00015*Slope**2.0+0.00359*NonSelfLevelCabDummy*Slope


            # Getting Arguments from Excel Spreadsheet for Machine Costs
            harvest_mc_wb = xlrd.open_workbook(
                os.path.join(os.path.dirname(__file__), 'harvest_cost.xls'))
            sh = harvest_mc_wb.sheet_by_index(0)

            mcChainsaw = sh.col_values(1, start_rowx=5, end_rowx=19)
            mcFbuncherDriveToTree = sh.col_values(2, start_rowx=5, end_rowx=19)
            mcFbuncherSwingBoom = sh.col_values(3, start_rowx=5, end_rowx=19)
            mcFbuncherSelfLeveling = sh.col_values(4, start_rowx=5, end_rowx=19)
            mcSkiddersmall = sh.col_values(7, start_rowx=5, end_rowx=19)
            mcSkidderbig = sh.col_values(8, start_rowx=5, end_rowx=19)
            mcYardersmall = sh.col_values(11, start_rowx=5, end_rowx=19)
            mcYarderintermediate = sh.col_values(12, start_rowx=5, end_rowx=19)
            mcProcessorsmall = sh.col_values(13, start_rowx=5, end_rowx=19)
            mcProcessorbig = sh.col_values(14, start_rowx=5, end_rowx=19)
            mcLoadersmall = sh.col_values(15, start_rowx=5, end_rowx=19)
            mcLoaderbig = sh.col_values(16, start_rowx=5, end_rowx=19)
            mcChippersmall = sh.col_values(17, start_rowx=5, end_rowx=19)
            mcChipperbig = sh.col_values(18, start_rowx=5, end_rowx=19)

            # Calculating final cost per PMH for each machine
            costPMHCSa = costpmhfunc (*mcChainsaw)
            costPMHFBDTT = costpmhfunc (*mcFbuncherDriveToTree)
            costPMHFBSB = costpmhfunc (*mcFbuncherSwingBoom)
            costPMHFBSL = costpmhfunc (*mcFbuncherSelfLeveling)
            costPMHSS = costpmhfunc (*mcSkiddersmall)
            costPMHSB = costpmhfunc (*mcSkidderbig)
            costPMHYS = costpmhfunc (*mcYardersmall)
            costPMHYI = costpmhfunc (*mcYarderintermediate)
            costPMHPS = costpmhfunc (*mcProcessorsmall)
            costPMHPB = costpmhfunc (*mcProcessorbig)
            costPMHLS = costpmhfunc (*mcLoadersmall)
            costPMHLB = costpmhfunc (*mcLoaderbig)
            costPMHCS = costpmhfunc (*mcChippersmall)
            costPMHCB = costpmhfunc (*mcChipperbig)

            ManualMachineSize = min (1.0, TreeVol/150.0)
            SkidderHourlyCost = round(costPMHSS*(1-ManualMachineSize)+costPMHSB*ManualMachineSize)
            YarderHourlyCost = round(costPMHYS*(1-ManualMachineSize)+costPMHYI*ManualMachineSize)
            MechMachineSize = min (1.0,TreeVolST/80.0)
            ProcessorHourlyCost = round(costPMHPS*(1-MechMachineSize)+costPMHPB*MechMachineSize)
            ChipperSize = min(1,(TreeVolCT/80))
            ChipperHourlyCost = round(costPMHCS*(1-ChipperSize)+costPMHCB*ChipperSize)
            ManualMachineSizeALT = min(1.0,TreeVolALT/150.0)
            LoaderHourlyCost = round(costPMHLS*(1-ManualMachineSizeALT)+costPMHLB*ManualMachineSizeALT)


            ################################################
            # Calculate Results                            #
            ################################################
            # Ground-Based Mech WT
            if Slope<40  and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<250 and TreeVolALT<250 and TreeVol<250:
                CostFellBunch = CostFellBunchfunc()
                CostManFLBLLT = CostManFLBLLTfunc()
                CostSkidBun = CostSkidBunfunc()
                CostProcess = CostProcessfunc()
                CostChipWT = CostChipWTfunc()
                CostLoad = CostLoadfunc()
                CostFellBunchAc = round (CostFellBunch*VolPerAcreST/100)
                CostManFLBLLTAc = round (CostManFLBLLT*VolPerAcreLLT/100)
                CostSkidBunAc = round (CostSkidBun*VolPerAcre/100)
                CostProcessAc = round (CostProcess*VolPerAcreSLT/100)
                CostChipWTAc = round (CostChipWT*VolPerAcreCT/100)
                CostLoadAc = round(CostLoad*VolPerAcreALT/100)
                GroundBasedMechWTAc = CostFellBunchAc+CostManFLBLLTAc+CostSkidBunAc+CostProcessAc+CostChipWTAc+CostLoadAc
                GroundBasedMechWT = round (GroundBasedMechWTAc/VolPerAcre,4)
            else:
                GroundBasedMechWT = float('NaN')

            # Ground-Based Manual WT
            if Slope<40 and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<500 and TreeVolALT<500 and TreeVol<500:
                CostManFLBLLT2 = CostManFLBLLT2func()
                CostManFellST2 = CostManFellST2func()
                CostSkidUB = CostSkidUBfunc()
                CostProcess = CostProcessfunc()
                CostChipWT = CostChipWTfunc()
                CostLoad = CostLoadfunc()
                CostManFLBLLT2Ac = round (CostManFLBLLT2*VolPerAcreLLT/100)
                CostManFellST2Ac = round (CostManFellST2*VolPerAcreST/100)
                CostSkidUBAc = round (CostSkidUB*VolPerAcre/100)
                CostProcessAc = round (CostProcess*VolPerAcreSLT/100)
                CostChipWTAc = round (CostChipWT*VolPerAcreCT/100)
                CostLoadAc = round(CostLoad*VolPerAcreALT/100)
                CostLoadAc = round(CostLoad*VolPerAcreALT/100)
                GroundBasedManualWTAc = CostManFLBLLT2Ac + CostManFellST2Ac + CostSkidUBAc + CostProcessAc + CostChipWTAc + CostLoadAc
                GroundBasedManualWT = round (GroundBasedManualWTAc/VolPerAcre, 4)
            else:
                GroundBasedManualWT = float('NaN') 

            # Cable Manual WT
            if SkidDist<1300 and TreeVolCT<80 and TreeVolSLT<80 and TreeVolLLT<500 and TreeVolALT<500 and TreeVol<500:
                CostManFLBLLT2 = CostManFLBLLT2func()
                CostManFellST2 = CostManFellST2func()
                CostProcess = CostProcessfunc()
                CostChipWT = CostChipWTfunc()
                CostLoad = CostLoadfunc()
                if PartialCut == 1:
                    CostYardPCUB = CostYardPCUBfunc()
                    CostYardUBAc = round (CostYardPCUB*VolPerAcre/100)
                else:
                    CostYardCCUB = CostYardCCUBfunc()
                    CostYardUBAc = round (CostYardCCUB*VolPerAcre/100)
                CostManFLBLLT2Ac = round(CostManFLBLLT2*VolPerAcreLLT/100)
                CostManFellST2Ac = round(CostManFellST2*VolPerAcreST/100)
                CostProcessAc = round(CostProcess*VolPerAcreSLT/100)
                CostChipWTAc = round (CostChipWT*VolPerAcreCT/100)
                CostLoadAc = round(CostLoad*VolPerAcreALT/100)
                CableManualWTAc = CostManFLBLLT2Ac + CostManFellST2Ac + CostProcessAc + CostChipWTAc + CostYardUBAc + CostLoadAc
                CableManualWT = round(CableManualWTAc/VolPerAcre, 4)
            else:
                CableManualWT = float('NaN')

            # Helicopter Manual WT
            if TreeVolCT<80 and TreeVolALT<250 and SkidDist<10000 and TreeVol<250 and TreeVolLLT<150:
                CostHeliYardML, CostHeliLoadML = CostHelifunc()
                CostManFLB = CostManFLBfunc()
                CostChipWT = CostChipWTfunc()
                CostHeliYardMLAc = round(CostHeliYardML*VolPerAcre/100)
                CostHeliLoadMLAc = round(CostHeliLoadML*VolPerAcreALT/100)
                CostManFLBAc = round (CostManFLB*VolPerAcre/100)
                CostChipWTAc = round (CostChipWT*VolPerAcreCT/100)
                HelicopterManualWTAc = CostHeliLoadMLAc + CostHeliYardMLAc + CostManFLBAc + CostChipWTAc
                HelicopterManualWT = round (HelicopterManualWTAc/VolPerAcre, 4)
            else:
                HelicopterManualWT = float('NaN')
       
            
            HarvestingSystemName = ['GroundBasedMechWT', 'GroundBasedManualWT', 'CableManualWT','HelicopterManualWT']
            HarvestingSystemPrice = [GroundBasedMechWT, GroundBasedManualWT, CableManualWT, HelicopterManualWT]
            HarvestingSystem = zip(HarvestingSystemName, HarvestingSystemPrice)

            try:
                Price = min(filter(lambda t:not math.isnan(t[1]), HarvestingSystem),key=operator.itemgetter(1))
                HarvestingSystem, Price = Price
            except:
                Price =  float('NaN')
                HarvestingSystem = 'NoSystem'

        else:
                Price =  0.0
                HarvestingSystem = 'NoSystem'

        return Price, HarvestingSystem # Price in ft3
