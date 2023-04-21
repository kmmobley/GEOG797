import arcpy
import os

# Set the workspace and output folder
ew_folder = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\EW_Conditions"
amis_folder = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\AMIS_Conditions"
output_folder = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\Global_Conditions_Combine"

# Set the overwrite output option
arcpy.env.overwriteOutput = True

# Set the workspace to the EW folder
arcpy.env.workspace = ew_folder

# Get a list of all the EW shapefiles
ew_files = arcpy.ListFeatureClasses("EW_*")

# Loop through each EW file
for ew_file in ew_files:
    # Extract the year and month from the filename
    ew_month = os.path.splitext(ew_file)[0][-7:]

    # Set the workspace to the AMIS folder
    arcpy.env.workspace = amis_folder

    # Get a list of all the AMIS shapefiles
    amis_files = arcpy.ListFeatureClasses("AMIS_*")

    # Loop through each AMIS file
    for amis_file in amis_files:
        # Extract the year and month from the filename
        amis_month = os.path.splitext(amis_file)[0][-7:]

        # Check if the months match
        if ew_month == amis_month:
            # Merge the EW and AMIS shapefiles
            output_file = os.path.join(output_folder, "Global_" + ew_month + "_Temp" + ".shp")
            arcpy.Merge_management([os.path.join(ew_folder, ew_file), os.path.join(amis_folder, amis_file)], output_file)

            # Remove duplicate rows based on the "Key" column
            arcpy.DeleteIdentical_management(output_file, ["Key"])

            # Change "Conditions" value from "Favorable" to "Favourable"
            with arcpy.da.UpdateCursor(output_file, ["Conditions"]) as cursor:
                for row in cursor:
                    if row[0] == "Favorable":
                        row[0] = "Favourable"
                        cursor.updateRow(row)

            # Change "Drivers" value from "Socio-political" to "Socio-economic"
            with arcpy.da.UpdateCursor(output_file, ["Drivers"]) as cursor:
                for row in cursor:
                    if "Socio-political" in row[0]:
                        row[0] = "Socio-economic"
                        cursor.updateRow(row)

            # Define the output coordinate system as WGS 1984 Web Mercator
            output_coord_system = arcpy.SpatialReference(3857)

            # Project the input shapefile to WGS 1984 Web Mercator
            output_project = os.path.join(output_folder, "Global_" + ew_month + "_Combine" + ".shp")
            arcpy.Project_management(output_file, output_project, output_coord_system)

            # Delete the temp shapefile using arcpy
            arcpy.management.Delete(output_file)

            # Print the basename of the output file
            print(os.path.basename(output_project))

    # Set the workspace back to the EW folder
    arcpy.env.workspace = ew_folder
