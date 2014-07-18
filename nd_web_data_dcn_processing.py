#-------------------------------------------------------------------------------
# Name:        nd_web_data_dcn_processing
# Purpose:     Script to clone all of the Dakota Carrier Network (DCN) member
#              company's wired broadband coverage and add back to the
#              Web_ProviderAndTechnology feature class
# Author:      KBalke
#
# Created:     16/05/2014
# Copyright:   (c) KBalke 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os, string, sys
arcpy.env.overwriteOutput = True

################################################################################
def createDCN (featureclass, transtech):
    # Calculate the Attribute Fields for the Cloned DCN Data
    arcpy.CalculateField_management (featureclass, "PROVNAME", "'Dakota Carrier Network'", "PYTHON_9.3")
    arcpy.CalculateField_management (featureclass, "DBANAME", "'DCN (Government and Business Only)'", "PYTHON_9.3")
    arcpy.CalculateField_management (featureclass, "FRN", "'9999'", "PYTHON_9.3")
    arcpy.CalculateField_management (featureclass, "SPECTRUM", 0, "PYTHON_9.3")
    if transtech == "50":
        arcpy.CalculateField_management (featureclass, "TRANSTECH", 50, "PYTHON_9.3")
        arcpy.CalculateField_management (featureclass, "MAXADDOWN", "'11'", "PYTHON_9.3")
        arcpy.CalculateField_management (featureclass, "MAXADUP", "'11'", "PYTHON_9.3")
    elif transtech == "30":
        arcpy.CalculateField_management (featureclass, "TRANSTECH", 30, "PYTHON_9.3")
        arcpy.CalculateField_management (featureclass, "MAXADDOWN", "'5'", "PYTHON_9.3")
        arcpy.CalculateField_management (featureclass, "MAXADUP", "'5'", "PYTHON_9.3")
    # Dissolve the Cloned DCN Data
    arcpy.Dissolve_management(featureclass, tempFC4, dzFields, "", "MULTI_PART")
    # Append the Cloned Data to the Web_ProviderAndTechnology Feature Class
    arcpy.Append_management(tempFC4, inWebProvTech, "NO_TEST")

################################################################################
inWebProvTech = arcpy.GetParameterAsText(0)
scratchGDB = arcpy.GetParameterAsText(1)
# The provName variable is the list of DCN Member Companies whose data is to be
# cloned and renamed as DCN.  This is the list of company names that may change
# over the course of time and should be an input from a text file Travis manages.
provName = "\"PROVNAME\" = 'BEK Communications Cooperative' OR \"PROVNAME\" = 'Consolidated Telcom' OR \"PROVNAME\" = 'Dakota Central Telecommunications Cooperative' OR \"PROVNAME\" = 'Dickey Rural Telephone Cooperative' OR \"PROVNAME\" = 'Griggs County Telephone Company' OR \"PROVNAME\" = 'Inter-Community Telephone Company' OR \"PROVNAME\" = 'Midstate Communications Inc.' OR \"PROVNAME\" = 'Midstate Telephone Company' OR \"PROVNAME\" = 'Moore & Liberty Telephone Company' OR \"PROVNAME\" = 'Moore & Liberty/Griggs County Telephone' OR \"PROVNAME\" = 'North Dakota Telephone Company' OR \"PROVNAME\" = 'Northwest Communications Cooperative, Inc.' OR \"PROVNAME\" = 'Polar Communications Mutual Aid Corporation' OR \"PROVNAME\" = 'Polar Telcom, Inc.' OR \"PROVNAME\" = 'Red River Rural Telephone Association, Inc.' OR \"PROVNAME\" = 'Reservation Telephone Cooperative' OR \"PROVNAME\" = 'SRT Communications, Inc.' OR \"PROVNAME\" = 'Turtle Mountain Communications' OR \"PROVNAME\" = 'United Telephone Mutual Aid Corporation' OR \"PROVNAME\" = 'West River Telecommunications Cooperative' OR \"PROVNAME\" = 'Wolverton Telephone Company'"
tempFC1 = scratchGDB + os.path.sep + "tempFC1"
tempFC2 = scratchGDB + os.path.sep + "tempFC2"
tempFC3 = scratchGDB + os.path.sep + "tempFC3"
tempFC4 = scratchGDB + os.path.sep + "tempFC4"
tempTblChkGeo = scratchGDB + os.path.sep +"temp_tbl_chk_geo"
dzFields = ["PROVNAME", "DBANAME", "FRN", "TRANSTECH", "SPECTRUM", "MAXADDOWN", "MAXADUP"]
techFiber = "50"
techCopper = "30"

try:
    # Select the DCN Members Features from the Web_ProviderTecnology Feature Class
    arcpy.Select_analysis(inWebProvTech, tempFC1, provName)

    # Select the Fiber to the End User Features and Create the DCN Clone
    arcpy.Select_analysis(tempFC1, tempFC2, "\"TRANSTECH\" = 50")
    createDCN (tempFC2, techFiber)

    # Select the DSL and Copper Features and Create the DCN Clone
    arcpy.Select_analysis(tempFC1, tempFC3, "\"TRANSTECH\" = 10 OR \"TRANSTECH\" = 20 OR \"TRANSTECH\" = 30")
    createDCN (tempFC3, techCopper)

    # Check Geometry of the Final Feature Class and Repair if Errors Found
    arcpy.CheckGeometry_management(inWebProvTech, tempTblChkGeo)
    if arcpy.GetCount_management(tempTblChkGeo) [0] < "1":
        arcpy.AddMessage ("The feature class does not contain any geomeotry errors")
    else:
        arcpy.RepairGeometry_management (inWebProvTech)

    #Delete Temporary Feature Classes
    arcpy.env.workspace = scratchGDB
    fcTemp = arcpy.ListFeatureClasses ("tempFC*", "")
    for fcTempDel in fcTemp:
        arcpy.Delete_management (fcTempDel, "")
except Exception as e:
    print e.message
    arcpy.AddError(e.message)