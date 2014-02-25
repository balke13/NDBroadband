#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      KBalke
#
# Created:     17/01/2013
# Copyright:   (c) KBalke 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, sys, string

# Local variables:
arcpy.env.workspace = "Z:\\OpportunityLink\\KyleTesting\\KyleTesting.gdb"

### Process: Get the InputDataset File Name
##InputFileName = os.path.basename(InputDataset).rstrip(os.path.splitext(InputDataset)[1])
##print InputFileName
##print "           "
##
##InputFileNamePart = InputFileName.partition("tbl_summary_count_mrktwn_") [2].upper()
###InputFileNamePart.upper()
##print InputFileNamePart


listTables = arcpy.ListTables ("tbl_summary_count_mrktwn*", "")
listTables.sort()
for table in listTables:
    tableStr = str(table)
    tableName = tableStr.partition("tbl_summary_count_mrktwn_")[2].upper()
    arcpy.AddField_management (table, tableName, "DOUBLE", "", "", "", "", "", "", "")
    arcpy.CalculateField_management (table, tableName, "!FREQUENCY!", "PYTHON", "")
    print tableName

listTables = arcpy.ListTables ("tbl_summary_count_twn*", "")
listTables.sort()
for table in listTables:
    tableStr = str(table)
    tableName = tableStr.partition("tbl_summary_count_twn_")[2].upper()
    arcpy.AddField_management (table, tableName, "DOUBLE", "", "", "", "", "", "", "")
    arcpy.CalculateField_management (table, tableName, "!FREQUENCY!", "PYTHON", "")
    print tableName