import gzip
import os
import shutil
import tempfile
from datetime import datetime, timedelta

import requests
import xarray as xr

try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for very old python versions if necessary
    from backports.zoneinfo import ZoneInfo

def get_mrms_24h_rainfall(lat, lon, date_str, time_str):
    try:
        # 1. Parse user input as Eastern Time
        # Expects date_str: YYYYMMDD and time_str: HHMM
        naive_dt = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M")
        eastern_dt = naive_dt.replace(tzinfo=ZoneInfo("America/New_York"))
        
        # 2. Convert to UTC
        utc_dt = eastern_dt.astimezone(ZoneInfo("UTC"))
        
        # 3. Round to the nearest whole hour for the archive
        if utc_dt.minute >= 30:
            utc_rounded = utc_dt.replace(second=0, microsecond=0, minute=0) + timedelta(hours=1)
        else:
            utc_rounded = utc_dt.replace(second=0, microsecond=0, minute=0)

        # 4. Format for the URL
        r_date = utc_rounded.strftime("%Y%m%d")
        r_time = utc_rounded.strftime("%H00")
        
        base_url = f"https://mtarchive.geol.iastate.edu/{r_date[:4]}/{r_date[4:6]}/{r_date[6:8]}/mrms/ncep/MultiSensor_QPE_24H_Pass2/"
        filename = f"MultiSensor_QPE_24H_Pass2_00.00_{r_date}-{r_time}00.grib2.gz"
        full_url = base_url + filename

        print(f"\n--- Processing ---")
        print(f"Input (ET):  {eastern_dt.strftime('%Y-%m-%d %I:%M %p %Z')}")
        print(f"Target (UTC): {utc_rounded.strftime('%Y-%m-%d %H:%M UTC')}")
        
        response = requests.get(full_url)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(suffix=".grib2.gz", delete=False) as tmp_gz:
            tmp_gz.write(response.content)
            gz_path = tmp_gz.name

        raw_grib_path = gz_path.replace('.gz', '')
        with gzip.open(gz_path, 'rb') as f_in:
            with open(raw_grib_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        mrms_lon = float(lon) if float(lon) >= 0 else float(lon) + 360
        ds = xr.open_dataset(raw_grib_path, engine='cfgrib', backend_kwargs={'indexpath': ''})
        
        var_name = list(ds.data_vars)[0]
        point_data = ds[var_name].sel(latitude=float(lat), longitude=mrms_lon, method='nearest')
        rainfall = float(point_data.values)
        
        ds.close()
        os.remove(gz_path)
        os.remove(raw_grib_path)
        return f"{rainfall:.2f} mm"

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("=== MRMS 24-Hour Rainfall Tool (Eastern Time) ===")
    u_lat = input("Enter Latitude:  ")
    u_lon = input("Enter Longitude: ")
    u_date = input("Enter Date (YYYYMMDD): ")
    u_time = input("Enter Time (HHMM): ")
    
    result = get_mrms_24h_rainfall(u_lat, u_lon, u_date, u_time)
    print(f"\nResult: {result}")
