import xlrd

def haulcost(TravelDistanceOneWay, TimeRoundTrip):

    ################################################
    ################PRE CALCULATIONS################
    ################################################

    data = xlrd.open_workbook('U:\My Documents\Tool\Data\hauling.xls')
    sh = data.sheet_by_index(0)
    sh.cell(rowx=4,colx=1).value

    ##############################
    ### FUEL AND LUBE          ###
    ##############################
    LubeCostPerGal = sh.cell(rowx=2,colx=1).value
    FuelCostPerGal = sh.cell(rowx=3,colx=1).value
    TruckMilesPerYear = sh.cell(rowx=4,colx=1).value
    OperatingMonthsPerYear = sh.cell(rowx=5,colx=1).value
    MilesPerMonth =  TruckMilesPerYear/OperatingMonthsPerYear
    FuelMileage = sh.cell(rowx=6,colx=1).value
    FuelCostPerMile = FuelCostPerGal/FuelMileage
    LubeUseGalMonth = sh.cell(rowx=7,colx=1).value
    LubeCostPerMile = LubeUseGalMonth*LubeCostPerGal/MilesPerMonth
    TotalFuelLubePerMile = LubeCostPerMile+FuelCostPerMile

    ##############################
    ###MAINT AND REPAIR        ###
    ##############################

    # Shop Labor Cost Per Hour
    ShopLaborPerHour = sh.cell(rowx=11,colx=1).value

    # Weekly Service
    MinPerTruck = sh.cell(rowx=12,colx=1).value
    WeeklyServiceCPM = MinPerTruck/60*ShopLaborPerHour/TruckMilesPerYear*48

    # Seven Week Service
    OilChangeGal = sh.cell(rowx=13,colx=1).value
    FilterCost = sh.cell(rowx=14,colx=1).value
    ShopLaborHrs = sh.cell(rowx=15,colx=1).value
    OilSampleExamCost = sh.cell(rowx=16,colx=1).value
    SevenWeekServiceCPM  = (OilChangeGal*LubeCostPerGal+FilterCost+ShopLaborHrs*ShopLaborPerHour+OilSampleExamCost)*51/7/TruckMilesPerYear

    # Engine Rebuild
    RebuildMiles = sh.cell(rowx=17,colx=1).value
    RebuildCost = sh.cell(rowx=18,colx=1).value
    EngineRebuildCPM  = RebuildCost/RebuildMiles

    # Transmission Replace
    ReplaceMiles = sh.cell(rowx=19,colx=1).value
    ReplaceCost = sh.cell(rowx=20,colx=1).value
    TransmissionReplaceCPM  = ReplaceCost/ReplaceMiles

    # Rear End Replace
    ReplaceMiles = sh.cell(rowx=21,colx=1).value
    ReplaceCost = sh.cell(rowx=22,colx=1).value
    RearEndReplaceCPM  = ReplaceCost/ReplaceMiles

    # Suspension Service
    ServiceMiles = sh.cell(rowx=23,colx=1).value
    SuspensionServieTruckCPM  = (1450+16*ShopLaborPerHour)/ServiceMiles
    SuspensionServieTrailerCPM  = (250+4*ShopLaborPerHour)/ServiceMiles

    # Brakes Replace
    ReplaceMiles = sh.cell(rowx=24,colx=1).value
    BrakeCPM = 1000.0/ReplaceMiles

    # Total Maintain and Repair Cost per Mile
    TotalTruckMainRepairCPM  = round(WeeklyServiceCPM + SevenWeekServiceCPM + EngineRebuildCPM + TransmissionReplaceCPM + RearEndReplaceCPM + SuspensionServieTruckCPM + BrakeCPM/2, 2)
    TotalTrailerMainRepairCPM = round(WeeklyServiceCPM + SuspensionServieTrailerCPM + BrakeCPM/2, 2)
    TotalMainRepairCPM = TotalTruckMainRepairCPM + TotalTrailerMainRepairCPM

    ##############################
    ###TIRE                   ####
    ##############################

    CostNewTire = sh.cell(rowx=28,colx=1).value
    CostRecape = sh.cell(rowx=29,colx=1).value
    TotalCostTire = CostNewTire + CostRecape
    TiresTruck = sh.cell(rowx=30,colx=1).value
    TiresTrailer = sh.cell(rowx=31,colx=1).value
    TireLifeMiles = sh.cell(rowx=32,colx=1).value
    TireRepairPercent = sh.cell(rowx=33,colx=1).value
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
    TruckCost = sh.cell(rowx=37,colx=1).value
    SeasonsWeeks = sh.cell(rowx=38,colx=1).value
    HoursPerDay = sh.cell(rowx=39,colx=1).value
    DaysPerWeek = sh.cell(rowx=40,colx=1).value
    HoursPerYear = SeasonsWeeks*HoursPerDay*DaysPerWeek
    SalvagePercent = sh.cell(rowx=41,colx=1).value
    TruckYears = sh.cell(rowx=42,colx=1).value
    AAITruck = (TruckCost-SalvagePercent*TruckCost)*(TruckYears+1)/(2*TruckYears)+SalvagePercent*TruckCost
    InsTaxLicPercent = sh.cell(rowx=43,colx=1).value
    TotalTruckCPH = ((TruckCost-SalvagePercent*TruckCost)/TruckYears+InsTaxLicPercent*AAITruck)/HoursPerYear

    ###TRAILER###
    TrailerCost = sh.cell(rowx=44,colx=1).value
    SeasonsWeeks = sh.cell(rowx=45,colx=1).value
    HoursPerDay = sh.cell(rowx=46,colx=1).value
    DaysPerWeek = sh.cell(rowx=47,colx=1).value
    HoursPerYear = SeasonsWeeks*HoursPerDay*DaysPerWeek
    SalvagePercent = sh.cell(rowx=48,colx=1).value
    TrailerYears = sh.cell(rowx=49,colx=1).value
    AAITrailer = (TrailerCost-SalvagePercent*TrailerCost)*(TrailerYears+1)/(2*TrailerYears)+SalvagePercent*TrailerCost
    Damage = sh.cell(rowx=50,colx=1).value
    TotalTrailerCPH = ((TrailerCost-SalvagePercent*TrailerCost)/TrailerYears+Damage*AAITrailer)/HoursPerYear

    ###TOTAL OWNERHSHIP COST PER HOUR###
    TotalOwnershipCPH = round(TotalTrailerCPH + TotalTruckCPH,2)


    ##############################
    ##########LABOR COST##########
    ##############################

    ###STRAIGT TIME###
    RatePerHourOR = sh.cell(rowx=54,colx=1).value
    RatePerHourWa = sh.cell(rowx=55,colx=1).value
    RatePerHourCa = sh.cell(rowx=56,colx=1).value
    AveRaterPerHour = RatePerHourOR
    OverHeadinflator = sh.cell(rowx=57,colx=1).value
    TotalStraightLaborCPH = round(AveRaterPerHour*OverHeadinflator, 2)

    ###OVERTIME###
    TotalOvertimeLaborCPH = round(TotalStraightLaborCPH*1.5, 2)


    ##############################
    #####TRUCK OPERATING COST#####
    ##############################

    # PUC weight-mile tax
    PUCTaxPerMile = sh.cell(rowx=61,colx=1).value

    # Total cost per mile
    TotalTruckOperatingCPM = TotalTireCPM + TotalMainRepairCPM + TotalFuelLubePerMile + PUCTaxPerMile

    # Operating Cost per hour
    WorkHoursPerDay = sh.cell(rowx=62,colx=1).value
    StandingTimeRoundTrip = sh.cell(rowx=63,colx=1).value
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
