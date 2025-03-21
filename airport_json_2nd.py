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
#        json.dump(data, f, indent=2)
        json.dump(data, f, separators=(",", ":"))  # Minified version

    print(f"✅ Created: {char_json_path}")

print("✅ All split JSON files have been created successfully!")


MAX_FILE_SIZE_KB = 75
output_dir = "json_clean_split"
os.makedirs(output_dir, exist_ok=True)

# airport_data = { "KATL": [...], ... } ← Your full dictionary

# Group by first and second letter
grouped_by_first = {}
filenames = []

for code, coords in airport_data.items():
    if not code or len(code) < 2:
        continue
    first = code[0].upper()
    second = code[1].upper()

    grouped_by_first.setdefault(first, {})
    grouped_by_first[first].setdefault(second, {})
    grouped_by_first[first][second][code] = coords

# Process each first-letter group
for first_letter, second_groups in grouped_by_first.items():
    all_codes = {}
    for second_data in second_groups.values():
        all_codes.update(second_data)
    
    estimated_total_kb = len(json.dumps(all_codes).encode("utf-8")) / 1024

    if estimated_total_kb <= MAX_FILE_SIZE_KB:
        # ✅ Small enough to be a single file
        filename = f"airport_data_{first_letter}_48_90.json"
        filenames.append(filename)

        with open(os.path.join(output_dir, filename), "w") as f:
#            json.dump(all_codes, f, indent=2)
            json.dump(all_codes, f, separators=(",", ":"))  # Minified version
        print(f"✅ Wrote {filename} (ALL in one file, {round(estimated_total_kb, 1)} KB)")
        continue

    # 🔁 Split if too large
    file_index = 1
    current_chunk = {}
    current_range_start = None
    current_range_end = None

    for second_letter in sorted(second_groups.keys()):
        second_ascii = ord(second_letter)
        new_chunk = {**current_chunk, **second_groups[second_letter]}
        new_size_kb = len(json.dumps(new_chunk).encode("utf-8")) / 1024

        if new_size_kb > MAX_FILE_SIZE_KB and current_chunk:
            # Write previous chunk
            filename = f"airport_data_{first_letter}_{current_range_start}_{current_range_end}.json"
            filenames.append(filename)

            with open(os.path.join(output_dir, filename), "w") as f:
            #    json.dump(current_chunk, f, indent=2)
                json.dump(current_chunk, f, separators=(",", ":"))  # Minified version
            print(f"✅ Wrote {filename} ({len(current_chunk)} codes)")

            # Start new chunk
            current_chunk = second_groups[second_letter].copy()
            current_range_start = second_ascii
            current_range_end = second_ascii
        else:
            current_chunk.update(second_groups[second_letter])
            if current_range_start is None:
                current_range_start = second_ascii
            current_range_end = second_ascii

    # Final chunk
    if current_chunk:
        filename = f"airport_data_{first_letter}_{current_range_start}_{current_range_end}.json"
        filenames.append(filename)

        with open(os.path.join(output_dir, filename), "w") as f:
        #    json.dump(current_chunk, f, indent=2)
            json.dump(current_chunk, f, separators=(",", ":"))  # Minified version
        print(f"✅ Wrote {filename} ({len(current_chunk)} codes)")

manifest_path = os.path.join(output_dir, "filenames.json")
with open(manifest_path, "w") as f:
    json.dump(filenames, f, indent=2)

