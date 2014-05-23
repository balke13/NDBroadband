#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      KBalke
#
# Created:     20/05/2014
# Copyright:   (c) KBalke 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy, os, string, sys, datetime

now = datetime.datetime.now()
from arcpy import env
scratchGDB = env.scratchWorkspace
scriptPath = sys.path[0]
dirPath = os.path.dirname (scriptPath)
if not env.scratchWorkspace:
    scratchGDB = os.path.join (dirPath, "Scratch.gdb") + os.path.sep
if not env.workspace:
    arcpy.env.workspace = os.path.join (dirPath, "BaseData.gdb")

outCS = arcpy.SpatialReference(3857)
codeCalcPct = """def calcPct(fld,pop):
    dec = float(fld)/float(pop)
    pct = dec*100
    return round(pct,2)"""
codeCalcCls = """def calcCls(div):
    cls = 0
    if div > 10.0 and div <= 40.0:
        cls = 1
    elif div > 40.0 and div <= 70.0:
        cls = 2
    elif div > 70.0:
        cls = 3
    return cls"""

try:
    arcpy.CreateFileGDB_management (dirPath, "NDUnserved" + now.strftime("%Y%m%d") )
    finalGDB = os.path.join (dirPath, "NDUnserved" + now.strftime("%Y%m%d") + ".gdb" + os.path.sep)
    listFC = arcpy.ListFeatureClasses("fc_final_nd*")
    for fc in listFC:
        tempUnion = scratchGDB + "u_" + fc
        tempSel = scratchGDB + "s_" + fc
        tempDz = scratchGDB + "dz_" + fc
        tempSj = scratchGDB + "sj_" + fc
        tempLyrDz = scratchGDB + "lyr_dz_" + fc
        tempLyrFinal = scratchGDB + "lyr_final" + fc
        tempSumTbl = scratchGDB + "tbl_pophu_sum_" + fc
        arcpy.Union_analysis ([fc, "fc_nd_Web_ProviderAndTechnology_class"], tempUnion)
        arcpy.AddField_management (tempUnion, "UNIQUE", "TEXT", "", "", 50)
        arcpy.CalculateField_management (tempUnion, "UNIQUE", "!NAME! + \"_\" + !CLASS!", "PYTHON_9.3")
        arcpy.Select_analysis (tempUnion, tempSel, "\"NAME\" <> '' AND \"CLASS\" <> ''")
        arcpy.Dissolve_management(tempSel, tempDz, "UNIQUE", "", "MULTI_PART")
        arcpy.SpatialJoin_analysis("fc_tabblock2010_38_pophu_pts", tempDz, tempSj, "", "KEEP_COMMON")
        arcpy.Statistics_analysis (tempSj, tempSumTbl, [["TOTPOP_CY", "SUM"]], "UNIQUE" )
        arcpy.JoinField_management (tempDz, "UNIQUE", tempSumTbl, "UNIQUE", "SUM_TOTPOP_CY")
        arcpy.MakeFeatureLayer_management (tempDz, tempLyrDz)
        arcpy.SelectLayerByAttribute_management (tempLyrDz, "NEW_SELECTION", "\"SUM_TOTPOP_CY\" IS NULL")
        arcpy.CalculateField_management (tempLyrDz, "SUM_TOTPOP_CY", 0)
        arcpy.AddField_management (tempDz, "NAME", "TEXT", "", "", 30)
        arcpy.AddField_management (tempDz, "CLASS", "TEXT", "", "", 20)
        arcpy.CalculateField_management (tempDz, "NAME", '!UNIQUE!.partition("_") [0]', "PYTHON_9.3")
        arcpy.CalculateField_management (tempDz, "CLASS", '!UNIQUE!.partition("_") [2]', "PYTHON_9.3")
        arcpy.PivotTable_management (tempDz, "NAME", "CLASS", "SUM_TOTPOP_CY", scratchGDB + "tbl_pivot_" + fc)
        arcpy.Project_management (fc, finalGDB + fc, outCS, "WGS_1984_(ITRF00)_To_NAD_1983")
        arcpy.JoinField_management (finalGDB + fc, "NAME", scratchGDB + "tbl_pivot_" + fc, "NAME", ["Advanced_TOTPOP", "Basic_TOTPOP", "Moderate_TOTPOP", "Standard_TOTPOP"])
        #Select Null Values in the TOTPOP Fields and Change to Zero
        arcpy.MakeFeatureLayer_management (finalGDB + fc, tempLyrFinal)
        arcpy.SelectLayerByAttribute_management (tempLyrFinal, "NEW_SELECTION", "\"Advanced_TOTPOP\" IS NULL")
        arcpy.CalculateField_management (tempLyrFinal, "Advanced_TOTPOP", 0)
        arcpy.SelectLayerByAttribute_management (tempLyrFinal, "NEW_SELECTION", "\"Standard_TOTPOP\" IS NULL")
        arcpy.CalculateField_management (tempLyrFinal, "Standard_TOTPOP", 0)
        arcpy.SelectLayerByAttribute_management (tempLyrFinal, "NEW_SELECTION", "\"Moderate_TOTPOP\" IS NULL")
        arcpy.CalculateField_management (tempLyrFinal, "Moderate_TOTPOP", 0)
        arcpy.SelectLayerByAttribute_management (tempLyrFinal, "NEW_SELECTION", "\"Basic_TOTPOP\" IS NULL")
        arcpy.CalculateField_management (tempLyrFinal, "Basic_TOTPOP", 0)
        #Calculate the Final Population Class and Percentage Fields
        arcpy.CalculateField_management (finalGDB + fc, "AdvPopPct", "calcPct(!Advanced_TOTPOP!, !TOTPOP_CY!)", "PYTHON_9.3", codeCalcPct)
        arcpy.CalculateField_management (finalGDB + fc, "AdvPopCls", "calcCls(!AdvPopPct!)", "PYTHON_9.3", codeCalcCls)
        arcpy.CalculateField_management (finalGDB + fc, "StdPopPct", "calcPct(!Standard_TOTPOP!, !TOTPOP_CY!)", "PYTHON_9.3", codeCalcPct)
        arcpy.CalculateField_management (finalGDB + fc, "StdPopCls", "calcCls(!StdPopPct!)", "PYTHON_9.3", codeCalcCls)
        arcpy.CalculateField_management (finalGDB + fc, "ModPopPct", "calcPct(!Moderate_TOTPOP!, !TOTPOP_CY!)", "PYTHON_9.3", codeCalcPct)
        arcpy.CalculateField_management (finalGDB + fc, "ModPopCls", "calcCls(!ModPopPct!)", "PYTHON_9.3", codeCalcCls)
        arcpy.CalculateField_management (finalGDB + fc, "BasPopPct", "calcPct(!Basic_TOTPOP!, !TOTPOP_CY!)", "PYTHON_9.3", codeCalcPct)
        arcpy.CalculateField_management (finalGDB + fc, "BasPopCls", "calcCls(!BasPopPct!)", "PYTHON_9.3", codeCalcCls)
        arcpy.CalculateField_management (finalGDB + fc, "NonePopPct", "100-(!AdvPopPct!+ !StdPopPct!+ !ModPopPct!+ !BasPopPct!)", "PYTHON_9.3" )
    #Delete Temporary Feature Classes and Tables
    arcpy.env.workspace = scratchGDB
    fcTemp = arcpy.ListFeatureClasses ()
    for fcTempDel in fcTemp:
        arcpy.Delete_management (fcTempDel, "")
    fcTbl = arcpy.ListTables()
    for fcTblDel in fcTbl:
        arcpy.Delete_management(fcTblDel, "")
except Exception as e:
    print e.message
    arcpy.AddError(e.message)