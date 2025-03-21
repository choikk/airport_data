#
# Check https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/ regularly and update your data as needed.
#
# pilot.DrChoi@gmail.com Kevin Choi  Copyright 2025
#

import os
import pandas as pd
import json

# ✅ Set your path correctly
path = "/Users/kchoi/Workspace/airport_json/28DaySubscription_Effective_2025-03-20/CSV_Data/20_Mar_2025_CSV"

# ✅ Define column indices for each CSV file
csv_files = {
    "APT_BASE.csv": {"code_col": "len-4", "fallback_col": 4, "lat_col": 19, "lon_col": 24},
    "FIX_BASE.csv": {"code_col": 1, "lat_col": 9, "lon_col": 14},
    "NAV_BASE.csv": {"code_col": 1, "lat_col": 26, "lon_col": 31},
}

# ✅ Dictionary to store airport data
airport_data = {}

for fn, col_indices in csv_files.items():
    file_name = os.path.join(path, fn)
    
    print(f"Processing {file_name}...")

    try:
        # ✅ Load CSV file, skipping the header row
        df = pd.read_csv(file_name, header=0, low_memory=False)

        # ✅ Check if the dataframe is empty
        if df.empty:
            print(f"❌ {file_name} is empty! Skipping...")
            continue

        # ✅ Handle APT_BASE Exception (Code Column at len-4 or fallback to column 4)
        if fn == "APT_BASE.csv":
            code_col_index = len(df.columns) - 4  # Dynamically calculate CI column
            df["Code"] = df.iloc[:, code_col_index].fillna(df.iloc[:, col_indices["fallback_col"]])
        else:
            df["Code"] = df.iloc[:, col_indices["code_col"]]

        # ✅ Extract relevant columns
        df["Latitude"] = df.iloc[:, col_indices["lat_col"]]
        df["Longitude"] = df.iloc[:, col_indices["lon_col"]]

        # ✅ Remove rows where Code, Latitude, or Longitude are empty
        df = df.fillna("").dropna(subset=["Code", "Latitude", "Longitude"])

        # ✅ Convert airport codes to uppercase and strip whitespace
        df["Code"] = df["Code"].astype(str).str.upper().str.strip()

        # ✅ Convert lat/lon to float
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        # ✅ Drop invalid rows where lat/lon are NaN
        df = df.dropna()

        # ✅ Print how many valid rows are left
        print(f"✅ {len(df)} valid rows found in {fn}")

        # ✅ Add data to the dictionary
        for _, row in df.iterrows():
            airport_data[row["Code"]] = [row["Latitude"], row["Longitude"]]

    except Exception as e:
        print(f"❌ Error processing {file_name}: {e}")

# ✅ Save to JSON file
json_output_dir = "json_data"
os.makedirs(json_output_dir, exist_ok=True)  # Create directory if not exists
full_json_path = os.path.join(json_output_dir, "airport_data.json")
with open(full_json_path, "w") as json_file:
    json.dump(airport_data, json_file, indent=2)

print(f"✅ Full JSON file saved: {full_json_path}")

# ✅ Split data into smaller JSON files by first character (including numbers)
split_data = {}

for code, details in airport_data.items():
    first_char = code[0] 
    if first_char.isdigit():  
        first_char = str(first_char)

    if first_char not in split_data:
        split_data[first_char] = {}  # Initialize dictionary for that character
    split_data[first_char][code] = details  # Store airport data

# ✅ Save each split JSON file
split_json_dir = os.path.join(json_output_dir, "split")
os.makedirs(split_json_dir, exist_ok=True)

for char, data in split_data.items():
    char_json_path = os.path.join(split_json_dir, f"airport_data_{char}.json")
    with open(char_json_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Created: {char_json_path}")

print("✅ All split JSON files have been created successfully!")

