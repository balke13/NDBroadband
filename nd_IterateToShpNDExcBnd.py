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
fieldName = "UNIQUE"

# Process: Get the InputDataset File Name
InputFileName = os.path.basename(InputDataset).rstrip(os.path.splitext(InputDataset)[1])
OutputShapefile = "Z:\\Broadband\\BBND\\Provider_Update\\201403\\Shapefiles\\"
OutputZipFiles = "Z:\\Broadband\\BBND\\Provider_Update\\201403\\ZipFiles\\"

#Set a list variable to hold the unique values from TOTMaxAddDownTemp
list = []

#Open a search cursor on the OutputProject feature class and loop through all the unique values in the TOTMaxAddDownTemp field
rows = arcpy.SearchCursor (InputDataset)
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
    arcpy.Select_analysis (InputDataset, OutputShapefile + list[x] + ".shp", query )

    #Create a new zip file using the original input coverage feature class file name and the value from TOTMaxAddDownTemp field (i.e., 10_4) and write the contents of the shapefile to it
    zip = zipfile.ZipFile (OutputZipFiles + list[x] + "_exc_bnd.zip", 'w', zlib.DEFLATED)
    zip.write (OutputShapefile + list[x] + ".dbf", InputFileName + "_" + list[x] + ".dbf")
    zip.write (OutputShapefile + list[x] + ".prj", InputFileName + "_" + list[x] + ".prj")
    zip.write (OutputShapefile + list[x] + ".sbn", InputFileName + "_" + list[x] + ".sbn")
    zip.write (OutputShapefile + list[x] + ".sbx", InputFileName + "_" + list[x] + ".sbx")
    zip.write (OutputShapefile + list[x] + ".shp", InputFileName + "_" + list[x] + ".shp")
    zip.write (OutputShapefile + list[x] + ".shp.xml",InputFileName + "_" + list[x] + ".shp.xml")
    zip.write (OutputShapefile + list[x] + ".shx", InputFileName + "_" + list[x] + ".shx")
    x = x + 1
