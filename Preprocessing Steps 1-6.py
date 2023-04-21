import subprocess

# Define the file paths of the scripts
scripts = [
    "Step 1 - Create Global CM Regions shp.py",
    "Step 2 - Create copy of AMIS Crop Condition shps and standardize.py",
    "Step 3 - Create copy of EW Crop Condition shps and standardize.py",
    "Step 4 - Combine AMIS and EW Crop Condition shps.py",
    "Step 5 - Split the Global Crop Conditions shps by the Global CM Regions shp.py",
    "Step 6 - Finalize the Global Crop Conditions shps and add calendar dates.py"
]


# Run the scripts sequentially
for script in scripts:
    try:
        subprocess.run(["python", script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script}: {e}")
        break

