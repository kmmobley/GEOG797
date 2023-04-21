import arcpy
import os
import pandas as pd

# Set up input and output folders
input_folder = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\Global_Conditions_Split"
output_folder = r"C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\Global_Conditions"
excel_file = r'C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Regions\GlobalCM_Preprocessing2.xlsx'

# Set the overwrite output option
arcpy.env.overwriteOutput = True

# Loop through shapefiles in input folder
for shpfile in os.listdir(input_folder):
    if shpfile.endswith(".shp") and "Global_" in shpfile:

        # Set up paths for input and output shapefiles
        input_shp = os.path.join(input_folder, shpfile)
        output_shp = os.path.join(output_folder, shpfile.replace("_Split.shp", "_calendar.shp"))
        output_shp_sorted = os.path.join(output_folder, shpfile.replace("_Split.shp", ".shp"))

        # create a copy of the shapefile and overwrite if it already exists
        arcpy.CopyFeatures_management(input_shp, output_shp)

        # Add new fields and calculate values
        arcpy.management.AddField(output_shp, "CM_Group", "TEXT", field_length=50)
        arcpy.management.CalculateField(output_shp, "CM_Group", "!CMGroup!", "PYTHON3")

        arcpy.management.AddField(output_shp, "Subregion", "TEXT", field_length=50)
        arcpy.management.CalculateField(output_shp, "Subregion", "!Region_1!", "PYTHON3")

        arcpy.management.AddField(output_shp, "Country", "TEXT", field_length=50)
        arcpy.management.CalculateField(output_shp, "Country", "!ADM0_NAME!", "PYTHON3")

        arcpy.management.AddField(output_shp, "CM_Region", "TEXT", field_length=50)
        arcpy.management.CalculateField(output_shp, "CM_Region", "!Name!", "PYTHON3")


        arcpy.management.AddField(output_shp, "Crop_Type", "TEXT", field_length=50)
        arcpy.management.CalculateField(output_shp, "Crop_Type", "!Crop!", "PYTHON3")

        arcpy.management.AddField(output_shp, "Condition", "TEXT", field_length=50)
        arcpy.management.CalculateField(output_shp, "Condition", "!Conditions!", "PYTHON3")

        arcpy.management.AddField(output_shp, "Driver", "TEXT", field_length=50)
        arcpy.management.CalculateField(output_shp, "Driver", "!Drivers!", "PYTHON3")

        # Delete old fields
        arcpy.management.DeleteField(output_shp, ["CMGroup", "Region_1", "ADM0_NAME", "Name", "Crop", "Conditions", "Drivers"])

        #Add new fields
        arcpy.management.AddField(output_shp, "Month", "TEXT", field_length=5)
        month = output_shp[-15:-13]  # get the last two characters before the file extension
        arcpy.management.AddField(output_shp, "Month", "TEXT", field_length=5)
        arcpy.management.CalculateField(output_shp, "Month", "'" + month + "'", "PYTHON3")

        arcpy.management.AddField(output_shp, "Key", "TEXT", field_length=150)
        expression = "!Country! + ' ' + !CM_Region!"
        arcpy.management.CalculateField(output_shp, "Key", expression, "PYTHON3")

        arcpy.management.AddField(output_shp, "Key2", "TEXT", field_length=150)
        expression = "!CM_Group! + ' ' + !Country! + ' ' + !CM_Region! + ' ' + !Crop_Type!+ ' ' + !Month!"
        arcpy.management.CalculateField(output_shp, "Key2", expression, "PYTHON3")

        arcpy.management.AddField(output_shp, "Crop_Cal", "TEXT", field_length=5)


        # Read the Excel file into a Pandas DataFrame
        df = pd.read_excel(excel_file)

        # Create a dictionary with the matching Key information
        country_region_dict = dict(zip(df['Key'], df['Crop_Cal']))

        # Use an UpdateCursor to update the "Crop_Cal" field based on the matching key infomration in the Excel sheet
        with arcpy.da.UpdateCursor(output_shp, ["Key2", "Crop_Cal"]) as cursor:
            for row in cursor:
                country = row[0]
                if country in country_region_dict:
                    row[1] = country_region_dict[country]
                    cursor.updateRow(row)

        # Add the "Sort" field and calculate its values
        arcpy.management.AddField(output_shp, "Sort", "TEXT", field_length=150)
        expression = "!Country! + ' ' + !Crop_type! + ' ' + !CM_Region!"
        arcpy.management.CalculateField(output_shp, "Sort", expression, "PYTHON3")

        # Sort the output shapefile based on the "Sort" field
        arcpy.management.Sort(output_shp, output_shp_sorted, [["Sort", "ASCENDING"]])

        # Delete old files and fields
        arcpy.management.Delete(output_shp)
        arcpy.management.DeleteField(output_shp_sorted, ["Key2"])
        arcpy.management.DeleteField(output_shp_sorted, ["Month"])

        print(os.path.basename(output_shp_sorted))
