import os
import arcpy

# set the input and output workspace directories
input_workspace = r"G:\.shortcut-targets-by-id\18VPZbWb8nAjt-4WxSph0ngBFywVmlSeB\Crop_Condition_Paper\Archive\AMIS"
output_workspace = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\AMIS_Conditions"

# set overwrite output to True
arcpy.env.overwriteOutput = True

# loop through each year folder
for year_folder in os.listdir(input_workspace):
    if not os.path.isdir(os.path.join(input_workspace, year_folder)) or not year_folder.isdigit() or len(
            year_folder) != 4:
        # skip any non-directory or non-year folders
        continue

    year = year_folder

    # loop through each month folder
    for month_folder in os.listdir(os.path.join(input_workspace, year_folder)):
        if not os.path.isdir(os.path.join(input_workspace, year_folder, month_folder)) or not month_folder[0].isdigit():
            # skip any non-directory or non-month folders
            continue

        month = month_folder.split("-")[0]
        month_formatted = month.zfill(2)

        # get the input shapefile and output shapefile paths
        input_shapefile = os.path.join(input_workspace, year_folder, month_folder, "{}.shp".format(month_folder))
        output_shapefile = os.path.join(output_workspace, "AMIS_{}-{}.shp".format(year, month_formatted))

        # create a copy of the shapefile and overwrite if it already exists
        arcpy.CopyFeatures_management(input_shapefile, output_shapefile)

        print("Created copy of {} as {}".format(os.path.basename(input_shapefile), os.path.basename(output_shapefile)))

        # Get a list of fields in the output shapefile
        fields = arcpy.ListFields(output_shapefile)

        # Check if the "Season" field exists in the shapefile and if it is of text data type
        if 'Season' in [field.name for field in arcpy.ListFields(output_shapefile)]:
            print('Updating "Crop" column with information from the "Season" column')
            # If the "Season" field exists and is of text data type, update the "Crop" field accordingly with the season number
            with arcpy.da.UpdateCursor(output_shapefile, ['Season', 'Crop']) as cursor:
                for row in cursor:
                    if '1' in str(row[0]):
                        row[1] = row[1] + ' 1'
                    elif '2' in str(row[0]):
                        row[1] = row[1] + ' 2'
                    cursor.updateRow(row)

        # Check if the "Seasons" field exists in the shapefile and if it is of text data type
        if 'Seasons' in [field.name for field in arcpy.ListFields(output_shapefile)]:
            print('Updating "Crop" column with information from the "Season" column')
            # If the "Season" field exists and is of text data type, update the "Crop" field accordingly with the season number
            with arcpy.da.UpdateCursor(output_shapefile, ['Seasons', 'Crop']) as cursor:
                for row in cursor:
                    if '1' in str(row[0]):
                        row[1] = row[1] + ' 1'
                    elif '2' in str(row[0]):
                        row[1] = row[1] + ' 2'
                    cursor.updateRow(row)

        # Check if the "Crop" field exists in the shapefile
        if 'Crop' in [field.name for field in arcpy.ListFields(output_shapefile)]:
            # If the "Crop" field exists and does not contain a season number or the word wheat, add a " 1" to the field
            with arcpy.da.UpdateCursor(output_shapefile, 'Crop') as cursor:
                for row in cursor:
                    if not any(x in row[0].lower() for x in ['1', '2', 'wheat']):
                        row[0] = row[0] + ' 1'
                        cursor.updateRow(row)

            # Update "Crop" field for wheat values
            with arcpy.da.UpdateCursor(output_shapefile, ["Crop"]) as cursor:
                for row in cursor:
                    if row[0] == "Wheat" or row[0] == "Wheat 1":
                        row[0] = "Winter Wheat"
                    elif row[0] == "Wheat 2":
                        row[0] = "Spring Wheat"
                    cursor.updateRow(row)

        # Add a new text field called "Key" to the output shapefile
        arcpy.AddField_management(output_shapefile, "Key", "TEXT", field_length=100)

        # Update the "Key" field with concatenated values from other fields
        with arcpy.da.UpdateCursor(output_shapefile, ["Country", "Region", "Crop", "Conditions", "Key"]) as cursor:
            for row in cursor:
                country = row[0]
                region = row[1]
                crop = row[2]
                conditions = row[3]
                key = f"{country} {region} {crop} {conditions}"
                row[4] = key
                cursor.updateRow(row)

        # delete unwanted fields from the output shapefile if they exist
        unwanted_fields = ["Trend", "Provenance", "Comment", "User", "Date_Obs", "Shape_ID", "Season", "Seasons", "Confidence", "Ass_ID", "Name_to_jo", "F14", "ADMIN1_NAME", "ADM0_NAME"]
        for field in unwanted_fields:
            if field in [f.name for f in arcpy.ListFields(output_shapefile)]:
                arcpy.DeleteField_management(output_shapefile, field)


        print("Updated attribute table of {}".format(os.path.basename(output_shapefile)))