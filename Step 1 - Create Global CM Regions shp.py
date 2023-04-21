import datetime
import pandas as pd
import arcpy
import os

# Set the workspace
arcpy.env.workspace = r"G:\.shortcut-targets-by-id\124w7m2nLuu5QquBZmh7UAIcN_vqhysTY\CM4EW\Regions"
work = arcpy.env.workspace

# Overwrite the output shapefile if it already exists
arcpy.env.overwriteOutput = True

# Input shapefiles
input_shp1 = work + "\AMIS_Regions_202209.shp"

input_shp2 = work + "\EWCM_Regions_v34.shp"

#Temporary shapefile
temp_shp = work + "\Global_Regions_temp.shp"

# Get the current date and time
now = datetime.datetime.now()

# Format the year and month in YYYYMM format
current_year_month = now.strftime("%Y-%m")

# Output shapefile
output_shp_name = "Global_Regions_%s_temp.shp"%(current_year_month)
output_shp = work + "\\" + output_shp_name
output_project_shp = os.path.join(work, "Global_Regions_%s.shp"%(current_year_month))

# Merge the two shapefiles
arcpy.Merge_management([input_shp1, input_shp2], temp_shp)

# Delete the "Shape_Length" and "Shape_Area" fields
arcpy.DeleteField_management(temp_shp, ["Shape_Leng", "Shape_Area"])

# Re-calculate the "Key" field
expression = "!ADM0_Name! + ' ' + !Name!"
arcpy.CalculateField_management(temp_shp, "Key", expression, "PYTHON3")

# Re-calculate the "Key2" field
expression = "!Name! + ' ' + !ADM0_Name!"
arcpy.CalculateField_management(temp_shp, "Key2", expression, "PYTHON3")

# Sort the shapefile based on the "Key" field
arcpy.Sort_management(temp_shp, output_shp, [["Key", "ASCENDING"]])

# Delete the temporary shapefile
arcpy.Delete_management(temp_shp)

# Delete duplicate regions based on the "Key" field
arcpy.DeleteIdentical_management(output_shp, ["Key"])

# Add the new "CM Group" column to the shapefile
arcpy.AddField_management(output_shp, "CMGroup", "TEXT", field_length=20)
# Excel file with matching country and region information
excel_file = work + "\CM_Regions.xlsx"

# Read the Excel file into a Pandas DataFrame
df = pd.read_excel(excel_file)

# Create a dictionary with the matching country and region information
country_region_dict = dict(zip(df['Country'], df['Subregion']))

# Use an UpdateCursor to update the "Region" field based on the matching country and corresponding region in the Excel sheet
with arcpy.da.UpdateCursor(output_shp, ["ADM0_NAME", "Region"]) as cursor:
    for row in cursor:
        country = row[0]
        if country in country_region_dict:
            row[1] = country_region_dict[country]
            cursor.updateRow(row)

# Create a dictionary with the matching country and CM Group information
country_region_dict2 = dict(zip(df['Country'], df['CMGroup']))

# Use an UpdateCursor to update the "CM Group" field based on the matching country and corresponding region in the Excel sheet
with arcpy.da.UpdateCursor(output_shp, ["ADM0_NAME", "CMGroup"]) as cursor:
    for row in cursor:
        country = row[0]
        if country in country_region_dict2:
            row[1] = country_region_dict2[country]
            cursor.updateRow(row)

# Delete the unwanted fields
arcpy.DeleteField_management(output_shp, "Shape_Lenth")
arcpy.DeleteField_management(output_shp, "Shape_Area")
arcpy.DeleteField_management(output_shp, "OBJECTID")

# Define the output coordinate system as WGS 1984 Web Mercator
output_coord_system = arcpy.SpatialReference(3857)

# Project the input shapefile to WGS 1984 Web Mercator
arcpy.Project_management(output_shp, output_project_shp, output_coord_system)

# Delete the temporary2 shapefile
arcpy.Delete_management(output_shp)

print("%s created successfully!"%(output_project_shp))

