def haulcost(TravelDistanceOneWay, TimeRoundTrip):

    ################################################
    ################PRE CALCULATIONS################
    ################################################

    ##############################
    ### FUEL AND LUBE          ###
    ##############################
    LubeCostPerGal = 9.75
    FuelCostPerGal = 3.00
    TruckMilesPerYear = 36000.0
    MilesPerMonth =  TruckMilesPerYear/11
    FuelMileage = 7.5
    FuelCostPerMile = FuelCostPerGal/FuelMileage
    LubeUseGalMonth = 1.0
    LubeCostPerMile = LubeUseGalMonth*LubeCostPerGal/MilesPerMonth
    TotalFuelLubePerMile = LubeCostPerMile+FuelCostPerMile

    ##############################
    ###MAINT AND REPAIR        ###
    ##############################

    # Shop Labor Cost Per Hour
    ShopLaborPerHour = 31.2

    # Weekly Service
    MinPerTruck = 60.0
    WeeklyServiceCPM = MinPerTruck/60*ShopLaborPerHour/TruckMilesPerYear*48

    # Seven Week Service
    OilChangeGal = 11.0
    FilterCost = 25.0
    ShopLaborHrs = 2.0
    OilSampleExamCost = 8.5
    SevenWeekServiceCPM  = (OilChangeGal*LubeCostPerGal+FilterCost+ShopLaborHrs*ShopLaborPerHour+OilSampleExamCost)*51/7/TruckMilesPerYear

    # Engine Rebuild
    RebuildMiles = 250000.0
    RebuildCost = 6000.0
    EngineRebuildCPM  = RebuildCost/RebuildMiles

    # Transmission Replace
    ReplaceMiles = 1000000.0
    ReplaceCost = 19000.0
    TransmissionReplaceCPM  = ReplaceCost/ReplaceMiles

    # Rear End Replace
    ReplaceMiles = 1000000.0
    ReplaceCost = 5000.0
    RearEndReplaceCPM  = ReplaceCost/ReplaceMiles

    # Suspension Service
    ServiceMiles = 200000.0
    SuspensionServieTruckCPM  = (1450+16*ShopLaborPerHour)/ServiceMiles
    SuspensionServieTrailerCPM  = (250+4*ShopLaborPerHour)/ServiceMiles

    # Brakes Replace
    ReplaceMiles = 30000.0
    BrakeCPM = 1000/ReplaceMiles

    # Total Maintain and Repair Cost per Mile
    TotalTruckMainRepairCPM  = round(WeeklyServiceCPM + SevenWeekServiceCPM + EngineRebuildCPM + TransmissionReplaceCPM + RearEndReplaceCPM + SuspensionServieTruckCPM + BrakeCPM/2, 2)
    TotalTrailerMainRepairCPM =  round(WeeklyServiceCPM + SuspensionServieTrailerCPM + BrakeCPM/2, 2)
    TotalMainRepairCPM = TotalTruckMainRepairCPM + TotalTrailerMainRepairCPM

    ##############################
    ###TIRE                   ####
    ##############################

    CostNewTire = 600.0
    CostRecape = 600.0
    TotalCostTire = CostNewTire + CostRecape
    TiresTruck = 10.0
    TiresTrailer = 8.0
    TireLifeMiles = 30000.0
    TireRepairPercent = 0.2
    TotalTruckTireCPM = round(TiresTruck*TotalCostTire/(TireLifeMiles*3)*(1+TireRepairPercent),2)
    TotalTrailerTireCPM = round(TiresTrailer*TotalCostTire/(TireLifeMiles*3)*(1+TireRepairPercent),2)
    TotalTireCPM = round(TotalTruckTireCPM + TotalTrailerTireCPM, 2)


    ################################################
    #####OWNING AND OPERATING COST CALCULATIONS#####
    ################################################

    ##############################
    ###OWNERSHIP COST          ###
    ##############################

    ###TRUCK###
    TruckCost = 123735.0
    SeasonsWeeks = 40.0
    HoursPerDay = 9.7
    DaysPerWeek = 5.0
    HoursPerYear = SeasonsWeeks*HoursPerDay*DaysPerWeek
    SalvagePercent = 0.2
    TruckYears = 9.0
    AAITruck = (TruckCost-SalvagePercent*TruckCost)*(TruckYears+1)/(2*TruckYears)+SalvagePercent*TruckCost
    InsTaxLicPercent = 0.078
    TotalTruckCPH = ((TruckCost-SalvagePercent*TruckCost)/TruckYears+InsTaxLicPercent*AAITruck)/HoursPerYear

    ###TRAILER###
    TrailerCost = 34871.0
    SeasonsWeeks = 40.0
    HoursPerDay = 9.7
    DaysPerWeek = 5.0
    HoursPerYear = SeasonsWeeks*HoursPerDay*DaysPerWeek
    SalvagePercent = 0.2
    TrailerYears = 7.0
    AAITrailer = (TrailerCost-SalvagePercent*TrailerCost)*(TrailerYears+1)/(2*TrailerYears)+SalvagePercent*TrailerCost
    Damage = 0.04
    TotalTrailerCPH = ((TrailerCost-SalvagePercent*TrailerCost)/TrailerYears+Damage*AAITrailer)/HoursPerYear

    ###TOTAL OWNERHSHIP COST PER HOUR###
    TotalOwnershipCPH = round(TotalTrailerCPH + TotalTruckCPH,2)


    ##############################
    ##########LABOR COST##########
    ##############################

    ###STRAIGT TIME###
    RatePerHourOR = 18.08
    RatePerHourWa = 19.39
    RatePerHourCa = 32.14
    AveRaterPerHour = RatePerHourOR
    OverHeadinflator = 1.0 + 0.05
    TotalStraightLaborCPH = round(AveRaterPerHour*OverHeadinflator, 2)

    ###OVERTIME###
    TotalOvertimeLaborCPH = round(TotalStraightLaborCPH*1.5, 2)


    ##############################
    #####TRUCK OPERATING COST#####
    ##############################

    # PUC weight-mile tax
    PUCTaxPerMile = 0.12

    # Total cost per mile
    TotalTruckOperatingCPM = TotalTireCPM + TotalMainRepairCPM + TotalFuelLubePerMile + PUCTaxPerMile

    # Operating Cost per hour
    WorkHoursPerDay = 9.7
    StandingTimeRoundTrip = 65.0
    Trips = (60.0*WorkHoursPerDay)/(TimeRoundTrip+StandingTimeRoundTrip)
    TotalDistance = Trips*TravelDistanceOneWay*2
    DistanceHalf = TotalDistance/2
    TotalTruckOperatingC = TotalDistance*TotalTruckOperatingCPM-DistanceHalf*PUCTaxPerMile
    TotalTruckOperatingCPH = round(TotalTruckOperatingC/WorkHoursPerDay,2)

    ################################################
    ######TOTAL OWNING, OPERATING, LABOR COST ######
    ################################################

    # Standing (Ownership and Labor Cost)
    TotalStandingStraightCPH = TotalStraightLaborCPH + TotalOwnershipCPH
    TotalStandingOvertimeCPH = TotalOvertimeLaborCPH + TotalOwnershipCPH
    TotalStandingStraigtCPMin = TotalStandingStraightCPH/60.0
    TotalStandingOvertimeCPMin = TotalStandingOvertimeCPH/60.0

    # Traveling (Ownership and Labor and Operating Costs)
    TotalTravelingStraigtCPH = TotalStandingStraightCPH + TotalTruckOperatingCPH
    TotalTravelingOvertimeCPH = TotalStandingOvertimeCPH + TotalTruckOperatingCPH
    TotalTravelingStraigtCPMin = TotalTravelingStraigtCPH/60.0
    TotalTravelingOvertimeCPMin = TotalTravelingOvertimeCPH/60.0

    # Average Costs
    AverageTravelingCPmin = round((TotalTravelingStraigtCPMin*8+TotalTravelingOvertimeCPMin*(HoursPerDay-8))/HoursPerDay,4)
    AverageStandingCPmin = round((TotalStandingStraigtCPMin*8+TotalStandingOvertimeCPMin*(HoursPerDay-8))/HoursPerDay,4)
    AverageCPmin = round((AverageTravelingCPmin*TimeRoundTrip+AverageStandingCPmin*StandingTimeRoundTrip)/(TimeRoundTrip+StandingTimeRoundTrip),4)

    return AverageCPmin
