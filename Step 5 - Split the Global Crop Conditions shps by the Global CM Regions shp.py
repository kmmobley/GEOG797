import arcpy
import os
import glob

# Set up input and output folders
input_folder = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\Global_Conditions_Combine"
output_folder = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\Global_Conditions_Split"

# Set up reference shapefile for Intersect
ref_shapefile = glob.glob(os.path.join(r"G:\.shortcut-targets-by-id\124w7m2nLuu5QquBZmh7UAIcN_vqhysTY\CM4EW\Regions", "Global_Regions_*.shp"))[0]

# Load the map and symbology layer
aprx_path = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Crop Patterns Paper.aprx"

# Set the overwrite output option
arcpy.env.overwriteOutput = True

# Loop through shapefiles in input folder
for shpfile in os.listdir(input_folder):
    if shpfile.endswith(".shp") and "Global_" in shpfile:
        # Set up paths for input and output shapefiles
        input_shp = os.path.join(input_folder, shpfile)
        output_intersect_shp = os.path.join(output_folder, shpfile.replace("_Combine.shp", "_Intersect.shp"))
        output_dissolve_shp = os.path.join(output_folder, shpfile.replace("_Combine.shp", "_Dissolve.shp"))
        output_copy_shp = os.path.join(output_folder, shpfile.replace("_Combine.shp", "_Copy.shp"))
        output_select_shp = os.path.join(output_folder, shpfile.replace("_Combine.shp", "_Select.shp"))
        output_split_shp = os.path.join(output_folder, shpfile.replace("_Combine.shp", "_Split.shp"))

        try:
            # Perform Intersect with reference shapefile
            arcpy.Intersect_analysis([input_shp, ref_shapefile], output_intersect_shp)
        except arcpy.ExecuteError:
            # If there is an "invalid topology" error, repair the geometry of the input shapefile and try again
            desc = arcpy.Describe(input_shp)
            if desc.hasSpatialIndex:
                arcpy.RepairGeometry_management(input_shp)
                arcpy.Intersect_analysis([input_shp, ref_shapefile], output_intersect_shp)

        # Set the dissolve fields
        dissolve_fields = ["CMGroup", "Region_1", "ADM0_NAME", "Name", "Crop", "Conditions", "Drivers"]

        # Dissolve the intersected shapefile based on the dissolve fields
        arcpy.Dissolve_management(output_intersect_shp, output_dissolve_shp, dissolve_fields)

        # Add a new field to store the area in square kilometers
        arcpy.AddField_management(output_dissolve_shp, "Area", "DOUBLE")

        # Calculate the area of each feature in square kilometers
        arcpy.CalculateGeometryAttributes_management(output_dissolve_shp,
                                                     [["Area", "AREA_GEODESIC"]],
                                                     "")

        # Create a feature layer from the original shapefile
        arcpy.MakeFeatureLayer_management(output_dissolve_shp, output_copy_shp)

        # Select all features where the Area value is greater than 0
        arcpy.SelectLayerByAttribute_management(output_copy_shp, "NEW_SELECTION", "Area > 0")

        # Export the selected features to a new shapefile
        output_select_shp = arcpy.FeatureClassToFeatureClass_conversion(output_copy_shp, output_folder, shpfile.replace("_Combine.shp", "_Select.shp"))

        #Add new Key field
        arcpy.management.AddField(output_select_shp, "Key", "TEXT", field_length=150)
        expression = "!Crop! + ' ' + !ADM0_NAME! + ' ' + !Name!+ ' ' + !Region_1!"
        arcpy.management.CalculateField(output_select_shp, "Key", expression, "PYTHON3")

        # Find the feature with the highest Area value for each key value
        fields = ["Key", "Area", "Conditions", "Drivers"]
        with arcpy.da.SearchCursor(output_select_shp, fields) as cursor:
            # Create a dictionary to store the maximum Area value for each key value
            max_areas = {}
            for row in cursor:
                key = row[0]
                area = row[1]
                if key in max_areas:
                    if area > max_areas[key]["Area"]:
                        max_areas[key] = {"Area": area, "Conditions": row[2], "Drivers": row[3]}
                else:
                    max_areas[key] = {"Area": area, "Conditions": row[2], "Drivers": row[3]}

        # Update the conditions and drivers fields for each feature with the maximum Area value for its key value
        fields = ["Key", "Conditions", "Drivers"]
        with arcpy.da.UpdateCursor(output_select_shp, fields) as cursor:
            for row in cursor:
                key = row[0]
                if key in max_areas:
                    row[1] = max_areas[key]["Conditions"]
                    row[2] = max_areas[key]["Drivers"]
                    cursor.updateRow(row)

        # Remove the selection on the output shapefile
        #arcpy.SelectLayerByAttribute_management(output_dissolve_shp, "CLEAR_SELECTION")

        # Set the dissolve fields
        dissolve_fields = ["CMGroup", "Region_1", "ADM0_NAME", "Name", "Crop", "Conditions", "Drivers"]

        # Dissolve the intersected shapefile based on the dissolve fields
        arcpy.Dissolve_management(output_select_shp, output_split_shp, dissolve_fields)


        # Delete the intersect shapefile using arcpy
        arcpy.management.Delete(output_intersect_shp)
        arcpy.management.Delete(output_dissolve_shp)
        arcpy.management.Delete(output_select_shp)

        # Print the basename of the output file
        print(os.path.basename(output_split_shp))