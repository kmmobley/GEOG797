import os
import glob
import arcpy
import pandas as pd
import datetime

# Set up paths to input and output folders and shapefiles
input_folder = r'C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\Global_Conditions'
output_folder = r'C:\Users\kmobley\Documents\CM4EW\Crop Patterns Paper\Preprocessing\Consecutive_Outcomes'
regions_shapefile = r'G:\.shortcut-targets-by-id\124w7m2nLuu5QquBZmh7UAIcN_vqhysTY\CM4EW\Regions\Global_Regions_2023-04.shp'

# Set the overwrite output option
arcpy.env.overwriteOutput = True

# Define a dictionary of subregions and their corresponding names
valid_subregions = {
    'AP': 'Asia Pacific','CSA': 'Central & South Asia','CAC': 'Central America & Caribbean','CA': 'Central Asia','EA': 'East Africa', 'EE': 'Eastern Europe','EU27': 'EU-27',
    'EU28': 'EU-28','MENA': 'Middle East & North Africa', 'NA': 'North America','SA': 'South America', 'SEA': 'Southeast Asia','SAF': 'Southern Africa','WA': 'West Africa','GL': 'Global'}

# Define a list of valid crop types
valid_crop_types = ['Maize 1', 'Maize 2', 'Maize', 'Rice 1', 'Rice 2', 'Rice 3', 'Rice', 'Winter Wheat', 'Spring Wheat', 'Wheat', 'Soybean 1', 'Soybean 2', 'Soybean', 'Millet 1',
                    'Millet', 'Sorghum 1', 'Sorghum 2', 'Sorghum', 'Teff 1', 'Teff', 'Beans 1', 'Beans 2', 'Beans 3', 'Beans', 'Synthesis']

# Get user inputs for start and end dates, crop type, and subregion
start_date = input('Enter start date (yyyy-mm): ')
end_date = input('Enter end date (yyyy-mm): ')
# Validate start date and end date formats
while True:
    try:
        datetime.datetime.strptime(start_date, '%Y-%m')
        datetime.datetime.strptime(end_date, '%Y-%m')
        break
    except ValueError:
        print("Incorrect date format, please enter dates in yyyy-mm format")
        start_date = input('Enter start date (yyyy-mm): ')
        end_date = input('Enter end date (yyyy-mm): ')

# Display a list of available crop types for the user to choose from
print('Available crop types:')
for c in valid_crop_types:
    print(c)

# Prompt user to enter crop type
crop_type = input('Enter crop type: ')
while crop_type not in valid_crop_types:
    print('Invalid crop type. Please choose from the available crop types:')
    for c in valid_crop_types:
        print(c)
    crop_type = input('Enter crop type: ')

# Display a list of available subregions for the user to choose from
print('Available subregions:')
for key, value in valid_subregions.items():
    print(key + ': ' + value)

# Prompt user to enter subregion code
subregion_code = input('Enter subregion code: ')

# Check if subregion code is valid
if subregion_code.upper() not in valid_subregions:
    print('Invalid subregion code. Please choose from the available subregions:')
    for key, value in valid_subregions.items():
        print(key + ': ' + value)
    subregion_code = input('Enter subregion code: ')

subregion = valid_subregions.get(subregion_code.upper(), '')
print(subregion)



# Define the output shapefile name with the given user inputs
output_shapefile = os.path.join(output_folder, 'ConsecOut_{}_{}_{}_{}.shp'.format(subregion_code.upper(), crop_type.replace(' ', '_'), start_date, end_date))
arcpy.Copy_management(regions_shapefile, output_shapefile)
arcpy.AddField_management(output_shapefile, 'Consec_Out', 'LONG')

# Define the output excel file name with the given user inputs
output_excel = os.path.join(output_folder, 'ConsecOut_{}_{}_{}_{}.xlsx'.format(subregion_code.upper(), crop_type.replace(' ', '_'), start_date, end_date))


# Create empty list to store print statements
output_data = []

# Loop through input shapefiles in the specified time period
input_shapefiles = glob.glob(os.path.join(input_folder, 'Global_' + '*.shp'))
for input_shapefile in input_shapefiles:
    input_date = input_shapefile[-11:-4]  # Extract yyyy-mm from filename
    if start_date <= input_date <= end_date:
        #print(input_date)

        if subregion != 'Global':
            if crop_type != 'Synthesis':
                # Loop through rows in input shapefile
                with arcpy.da.SearchCursor(input_shapefile, ['Crop_Type', 'Subregion', 'Crop_Cal', 'Condition', 'Key', 'Country', 'CM_Region', 'Driver']) as cursor:
                    for row in cursor:
                        if str(crop_type) in str(row[0]) and str(row[1]) == str(subregion) and str(row[2]) == str(4) and str(row[3]) in ['Poor', 'Failure']:
                            output_row = [input_date, str(row[0]), str(row[1]), str(row[5]), str(row[6]), str(row[2]),str(row[3]), str(row[7])]
                            output_data.append(output_row)
                            print("%s; %s; %s; %s; %s; %s; %s; %s" % (input_date, str(row[0]), str(row[1]), str(row[5]), str(row[6]),str(row[2]), str(row[3]), str(row[7])))

                            # Match key values between input shapefile and output shapefile and update Consec_Out field
                            input_key = row[4]
                            with arcpy.da.UpdateCursor(output_shapefile, ['Key', 'Consec_Out']) as update_cursor:
                                for update_row in update_cursor:
                                    if update_row[0] == input_key:
                                        update_row[1] += 1
                                        update_cursor.updateRow(update_row)
                                        break

            else:
                # Loop through rows in input shapefile
                with arcpy.da.SearchCursor(input_shapefile,
                                           ['Crop_Type', 'Subregion', 'Crop_Cal', 'Condition', 'Key', 'Country', 'CM_Region', 'Driver']) as cursor:
                    processed_rows = set()  # Keep track of processed rows
                    for row in cursor:
                        if (str(row[1]), str(row[5]), str(row[6]), str(row[2])) not in processed_rows:  # Check if row has been processed
                            processed_rows.add((str(row[1]), str(row[5]), str(row[6]), str(row[2])))  # Add row to processed set
                            if str(row[1]) == str(subregion) and str(row[2]) == str(4) and str(row[3]) in ['Poor','Failure']:
                                output_row = [input_date, str(row[0]), str(row[1]), str(row[5]), str(row[6]),str(row[2]), str(row[3]), str(row[7])]
                                output_data.append(output_row)
                                print("%s; %s; %s; %s; %s; %s; %s; %s" % (input_date, str(row[0]), str(row[1]), str(row[5]), str(row[6]),str(row[2]), str(row[3]), str(row[7])))
                                # Match key values between input shapefile and output shapefile and update Consec_Out field
                                input_key = row[4]
                                with arcpy.da.UpdateCursor(output_shapefile, ['Key', 'Consec_Out']) as update_cursor:
                                    for update_row in update_cursor:
                                        if update_row[0] == input_key:
                                            update_row[1] += 1
                                            update_cursor.updateRow(update_row)
                                            break

            # Delete features where the Subregion field does not equal the user-input subregion
            with arcpy.da.UpdateCursor(output_shapefile, 'Region') as update_cursor:
                for row in update_cursor:
                    if row[0] != subregion:
                        update_cursor.deleteRow()


        else:
            if crop_type != 'Synthesis':
                # Loop through rows in input shapefile
                with arcpy.da.SearchCursor(input_shapefile, ['Crop_Type', 'Subregion', 'Crop_Cal', 'Condition', 'Key', 'Country','CM_Region', 'Driver']) as cursor:
                    for row in cursor:
                        if str(crop_type) in str(row[0]) and str(row[2]) == str(4) and str(row[3]) in ['Poor', 'Failure']:
                            output_row = [input_date, str(row[0]), str(row[1]), str(row[5]), str(row[6]), str(row[2]),str(row[3]), str(row[7])]
                            output_data.append(output_row)
                            print("%s; %s; %s; %s; %s; %s; %s; %s" % (input_date, str(row[0]), str(row[1]), str(row[5]), str(row[6]),str(row[2]), str(row[3]), str(row[7])))
                            # Match key values between input shapefile and output shapefile and update Consec_Out field
                            input_key = row[4]
                            with arcpy.da.UpdateCursor(output_shapefile, ['Key', 'Consec_Out']) as update_cursor:
                                for update_row in update_cursor:
                                    if update_row[0] == input_key:
                                        update_row[1] += 1
                                        update_cursor.updateRow(update_row)
                                        break

            else:
                # Loop through rows in input shapefile
                with arcpy.da.SearchCursor(input_shapefile,['Crop_Type', 'Subregion', 'Crop_Cal', 'Condition', 'Key', 'Country','CM_Region', 'Driver']) as cursor:
                    processed_rows = set()  # Keep track of processed rows
                    for row in cursor:
                        if (str(row[1]), str(row[5]), str(row[6]),str(row[2])) not in processed_rows:  # Check if row has been processed
                            processed_rows.add((str(row[1]), str(row[5]), str(row[6]), str(row[2])))  # Add row to processed set
                            if str(row[2]) == str(4) and str(row[3]) in ['Poor','Failure']:
                                output_row = [input_date, str(row[0]), str(row[1]), str(row[5]), str(row[6]),str(row[2]), str(row[3]), str(row[7])]
                                output_data.append(output_row)
                                print("%s; %s; %s; %s; %s; %s; %s; %s" % (input_date, str(row[0]), str(row[1]), str(row[5]), str(row[6]),str(row[2]), str(row[3]), str(row[7])))
                                # Match key values between input shapefile and output shapefile and update Consec_Out field
                                input_key = row[4]
                                with arcpy.da.UpdateCursor(output_shapefile, ['Key', 'Consec_Out']) as update_cursor:
                                    for update_row in update_cursor:
                                        if update_row[0] == input_key:
                                            update_row[1] += 1
                                            update_cursor.updateRow(update_row)
                                            break

# Create pandas dataframe from output data list
df = pd.DataFrame(output_data, columns=['Input Date', 'Crop Type', 'Subregion', 'Country', 'CM Region', 'Crop Cal', 'Condition', 'Driver'])

# Save dataframe to Excel file
df.to_excel(output_excel, index=False)

# Print name of output shapefile
print('Output shapefile:', output_shapefile)
print('Output excel file:', output_excel)

