# MRMS 24-Hour Rainfall Fetcher

A Python tool to retrieve 24-hour rainfall accumulation (QPE Pass 2) from the NOAA/NWS Multi-Radar Multi-Sensor (MRMS) system for specific coordinates and times.

## Features
* **Timezone Aware:** Automatically converts Eastern Time (ET) to UTC for archive retrieval.
* **Auto-Rounding:** Rounds user input to the nearest whole hour to match the MRMS hourly archive.
* **Point Extraction:** Uses `xarray` and `cfgrib` to extract precise rainfall depth (mm) from GRIB2 files.

## How to Use

### For Non-Technical Users (Windows)
1. Go to the **Releases** tab on the right side of this page.
2. Download `single_rainfall_24H.exe`.
3. Double-click to run. (Note: You may need to click "More Info" -> "Run Anyway" if Windows shows a warning).

### For Developers
1. Clone the repo: `git clone https://github.com/YOUR_USERNAME/mrms-rainfall-fetcher.git`
2. Install dependencies: `pip install -r requirements.txt`
3. **Note:** You must have `eccodes` installed on your system to read GRIB2 files.
4. Run: `python single_rainfall_24H.py`

## Data Source
Data is fetched from the [Iowa Environmental Mesonet (IEM) MTArchive](https://mtarchive.geol.iastate.edu/).