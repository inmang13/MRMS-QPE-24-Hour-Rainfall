import pandas as pd

from single_rainfall_24H import get_mrms_24h_rainfall  # Import your original function


def process_spreadsheet(input_file, output_file):
    # 1. Load the data
    print(f"Reading {input_file}...")
    if input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    else:
        df = pd.read_excel(input_file)

    # 2. Prepare the new column
    results = []

    # 3. Loop through rows
    for index, row in df.iterrows():
        print(f"Processing row {index + 1}/{len(df)}...")
        
        # Adjust column names below to match your spreadsheet exactly
        lat = row['Latitude']
        lon = row['Longitude']
        date = str(int(row['Date'])) # Ensure it's a string YYYYMMDD
        time = str(int(row['Time'])).zfill(4) # Ensure it's HHMM (e.g., 900 -> 0900)

        rain = get_mrms_24h_rainfall(lat, lon, date, time)
        results.append(rain)

    # 4. Add results and save
    df['Rainfall_24H_mm'] = results
    df.to_csv(output_file, index=False)
    print(f"Done! Saved to {output_file}")

if __name__ == "__main__":
    file_in = input("Enter path to input spreadsheet (e.g., sites.csv): ")
    file_out = file_in
    process_spreadsheet(file_in, file_out)