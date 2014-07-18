# ---------------------------------------------------------------------------
# IterateToShp.py
# Created on: 2012-04-24 10:40:13.00000
# Created by: Kyle Balke - Senior GIS Analyst
# Description: This script takes a provider's coverage feature class and prepares it for use on the Broadband Editing App.  The input feature class is re-project to WGS84 (required by the editing app),
#              calculates a temporary field (TOTMaxAddDownTemp field), and then loops through each unique TOTMaxAddDownTemp value which is exported to shapefile.  The final shapefiles are compress into individual zip files.
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy, os, sys, string, zipfile, zlib

# Local variables:
InputDataset = arcpy.GetParameterAsText(0)
fieldName = "TOTMaxAddDownTemp"

# Process: Get the InputDataset File Name
InputFileName = os.path.basename(InputDataset).rstrip(os.path.splitext(InputDataset)[1])
OutputProject = "Z:\\Broadband\\BBND\\Provider_Update\\201409\\Scratch.gdb\\" + InputFileName + "_Project"
OutputShapefile = "Z:\\Broadband\\BBND\\Provider_Update\\201409\\Shapefiles\\"
OutputZipFiles = "Z:\\Broadband\\BBND\\Provider_Update\\201409\\ZipFiles\\"
OutputFCLocation = "Z:\\Broadband\\BBND\\Provider_Update\\201409\\NDUpdate20140930.gdb\\Provider_Coverage\\"
OutTable = "Z:\\Broadband\\BBND\\Provider_Update\\201409\\NDUpdate20140930.gdb\\" + "tbl_CheckGeo_" + InputFileName

# Create a copy of the input FeatureClass
arcpy.FeatureClassToFeatureClass_conversion(InputDataset, OutputFCLocation, InputFileName,"")

# Process: Project the Input Dataset to WGS84
arcpy.Project_management(InputDataset, OutputProject, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NAD_1983_To_WGS_1984_1", "PROJCS['NAD_1983_StatePlane_North_Dakota_South_FIPS_3302_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-100.5],PARAMETER['Standard_Parallel_1',46.18333333333333],PARAMETER['Standard_Parallel_2',47.48333333333333],PARAMETER['Latitude_Of_Origin',45.66666666666666],UNIT['Foot_US',0.3048006096012192]]")

#Check Geometry
arcpy.CheckGeometry_management(OutputProject, OutTable)

#Repair Geometry
arcpy.RepairGeometry_management (OutputProject)

#Set a list variable to hold the unique values from TOTMaxAddDownTemp
list = []

#Open a search cursor on the OutputProject feature class and loop through all the unique values in the TOTMaxAddDownTemp field
rows = arcpy.SearchCursor (OutputProject)
row = rows.next()

#Use a while loop to cursor through all the records and append unique values to the list variable
while row:
    value = row.getValue (fieldName)
    if value not in list:
        list.append (value)
    row = rows.next()

#Sort the list variable
list.sort()

#If a value in the list variable is blank, remove it from the list variable
if ' ' in list:
    list.remove (' ')

#Loop through the list variable
x = 0
for item in list:

    #Create the query
    query = fieldName + " = '" + list[x] + "'"

    #Execute the Select tool
    arcpy.Select_analysis (OutputProject, OutputShapefile + InputFileName + "_" + list[x] + ".shp", query )

    #Create a new zip file using the original input coverage feature class file name and the value from TOTMaxAddDownTemp field (i.e., 10_4) and write the contents of the shapefile to it
    zip = zipfile.ZipFile (OutputZipFiles + InputFileName + "_" + list[x] + ".zip", 'w', zlib.DEFLATED)
    zip.write (OutputShapefile + InputFileName + "_" + list[x] + ".dbf", InputFileName + "_" + list[x] + ".dbf")
    zip.write (OutputShapefile + InputFileName + "_" + list[x] + ".prj", InputFileName + "_" + list[x] + ".prj")
    zip.write (OutputShapefile + InputFileName + "_" + list[x] + ".sbn", InputFileName + "_" + list[x] + ".sbn")
    zip.write (OutputShapefile + InputFileName + "_" + list[x] + ".sbx", InputFileName + "_" + list[x] + ".sbx")
    zip.write (OutputShapefile + InputFileName + "_" + list[x] + ".shp", InputFileName + "_" + list[x] + ".shp")
    zip.write (OutputShapefile + InputFileName + "_" + list[x] + ".shp.xml",InputFileName + "_" + list[x] + ".shp.xml")
    zip.write (OutputShapefile + InputFileName + "_" + list[x] + ".shx", InputFileName + "_" + list[x] + ".shx")
    x = x + 1
