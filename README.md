# ✈️ airport_data

This project parses airport and navigation waypoint data from FAA NASR 28-day subscription CSV files and outputs them as optimized JSON files.
Data from https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/

## 📦 Purpose

FAA updates NASR (National Airspace System Resource) data every 28 days. This script extracts latitude and longitude coordinates for:

- Airports (APT_BASE.csv)
- Waypoints/Fixes (FIX_BASE.csv)
- Navigation Aids (NAV_BASE.csv)

The goal is to generate compact and structured JSON files suitable for fast lookup within **Google Apps Script**, particularly for aviation tools like:

- Airport distance calculators
- Waypoint mapping utilities
- Custom pilot logbook integrations

## ⚙️ How It Works

1. Parses each CSV file using pandas
2. Extracts coordinates based on column indices
3. Outputs a combined `airport_data.json` file
4. Splits the file into smaller chunks:
   - First by the **first letter** of the airport/nav code
   - Then optionally by **ASCII ranges of the second letter** (for performance)

Example output file:
json_data/split/airport_data_K_65_70.json


## 🧰 Requirements

- Python 3.7+
- `pandas`

Install dependencies:
```bash
pip install pandas

python airport_json.py
