#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      KBalke
#
# Created:     16/05/2014
# Copyright:   (c) KBalke 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os, string, sys

from arcpy import env
scratchGDB = env.scratchWorkspace
scriptPath = sys.path[0]
dirPath = os.path.dirname (scriptPath)
if not env.scratchWorkspace:
    scratchGDB = os.path.join (dirPath, "Scratch.gdb") + os.path.sep
if not env.workspace:
    arcpy.env.workspace = os.path.join (dirPath, "BaseData.gdb")
arcpy.env.overwriteOutput = True

inWebProvTech = arcpy.GetParameterAsText(0)
##inWebProvTech = r"Z:\Broadband\BBND\Website_Data\Submission_20140401\ND_BB_Web_Data_20140401.gdb\Web_ProviderAndTechnology"
tempFC1 = scratchGDB + os.path.sep + "tempFC1"
tempFC2 = scratchGDB + os.path.sep + "tempFC2"
tempFC3 = scratchGDB + os.path.sep + "tempFC3"
tempFC4 = scratchGDB + os.path.sep + "tempFC4"
tempFC5 = scratchGDB + os.path.sep + "tempFC5"
tempFC6 = scratchGDB + os.path.sep + "tempFC6"
tempFC7 = scratchGDB + os.path.sep + "tempFC7"
tempFC8 = scratchGDB + os.path.sep + "tempFC8"
tempTblChkGeo = scratchGDB + os.path.sep + "tblChkGeo1"
finalFC = "fc_nd_Web_ProviderAndTechnology_class"
outCS = arcpy.SpatialReference(102721)
expression1 = "calcClass(!MAXADDOWN!)"
expression2 = "calcSort(!CLASS!)"
codeCalcClass = """def calcClass (spd):
    if spd == "6":
        return "Basic_TOTPOP"
    elif spd == "7":
        return "Moderate_TOTPOP"
    elif spd == "8" or spd == "9":
        return "Standard_TOTPOP"
    elif spd == "10" or spd == "11":
        return "Advanced_TOTPOP" """
codeCalcSort = """def calcSort (cls):
    if cls == "Basic_TOTPOP":
        return "4"
    elif cls == "Moderate_TOTPOP":
        return "3"
    elif cls == "Standard_TOTPOP":
        return "2"
    elif cls == "Advanced_TOTPOP":
        return "1" """
try:
    #Project inWebProvTech to NAD_1983_StatePlane_North_Dakota_South_FIPS_3302_Feet
    arcpy.Project_management (inWebProvTech, tempFC1, outCS, "NAD_1983_To_WGS_1984_1")
    #Remove DCN and Mobile Wireless Records
    arcpy.Select_analysis(tempFC1, tempFC2, "\"PROVNAME\" <> 'Dakota Carrier Network' AND \"TRANSTECH\" <> 80")
    #Add CLASS Field (Text-10)
    arcpy.AddField_management (tempFC2, "CLASS", "TEXT", "","", 20)
    #Calculate CLASS Field Where Advanced = DownSpd 10 or 11, Standard = DownSpd 8 or 9,
    #Moderate = DownSpd 7, and Basic = DownSpd 6
    arcpy.CalculateField_management(tempFC2, "CLASS", expression1, "PYTHON_9.3", codeCalcClass)
    #Dissolve inWebProvTechPrj on CLASS Field
    arcpy.Dissolve_management(tempFC2, tempFC3, "CLASS")
    #Remove NULL Values from the CLASS Field
    arcpy.Select_analysis (tempFC3, tempFC4, "\"CLASS\" IS NOT NULL")
    #Add SORT Field (Short Int)
    arcpy.AddField_management (tempFC4, "SORT", "SHORT")
    #Calculate SORT Field Where Advanced = 1, Standard = 2, Moderate = 3, and Basic = 4
    arcpy.CalculateField_management (tempFC4, "SORT", expression2, "PYTHON_9.3", codeCalcSort)
    #Union Dissolved FC Againist Itself (basically a planarize polygon)
    arcpy.Union_analysis(tempFC4, tempFC5)
    #Convert Unioned FC to Singlepart Polygon
    arcpy.MultipartToSinglepart_management (tempFC5, tempFC6)
    #Sort on the SORT Field Ascending
    arcpy.Sort_management(tempFC6, tempFC7, [["SORT", "ASCENDING"]])
    #Add XCoord & YCoord Fields and Calculate
    arcpy.AddField_management (tempFC7, "XCoord", "LONG")
    arcpy.AddField_management (tempFC7, "YCOORD", "LONG")
    arcpy.CalculateField_management (tempFC7, "XCOORD", "!SHAPE.CENTROID!.split()[0]", "PYTHON")
    arcpy.CalculateField_management (tempFC7, "YCOORD", "!SHAPE.CENTROID!.split()[1]", "PYTHON")
    #Dissolve on XCoord, YCoord, & Area with Statistics SORT-First & CLASS-First
    arcpy.Dissolve_management (tempFC7, tempFC8, ["XCOORD", "YCOORD", "SHAPE_Area"], "CLASS FIRST", "MULTI_PART", "")
    #Re-Add CLASS Field
    arcpy.AddField_management (tempFC8, "CLASS", "TEXT", "", "", 20)
    arcpy.CalculateField_management(tempFC8, "CLASS", '!FIRST_CLASS!', "PYTHON_9.3")
    #Final Dissolve on CLASS Field
    arcpy.Dissolve_management (tempFC8, finalFC, "CLASS")
    #Check and Repair Geometry
    arcpy.CheckGeometry_management(finalFC, tempTblChkGeo)
    if arcpy.GetCount_management(tempTblChkGeo) [0] < "1":
        arcpy.AddMessage ("The feature class does not contain any geomeotry errors")
    else:
        arcpy.RepairGeometry_management (finalFC)
    #Delete Temporary Feature Classes
    arcpy.env.workspace = scratchGDB
    fcTemp = arcpy.ListFeatureClasses ("tempFC*", "")
    for fcTempDel in fcTemp:
        arcpy.Delete_management (fcTempDel, "")
except Exception as e:
    print e.message
    arcpy.AddError(e.message)










