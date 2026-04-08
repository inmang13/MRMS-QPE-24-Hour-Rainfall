import gzip
import os
import shutil
import tempfile
from datetime import datetime, timedelta

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import xarray as xr
from shapely.geometry import Point

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _download_mrms(date_str, time_str):
    """
    Convert Eastern Time input to UTC, build the MRMS archive URL, download
    the .grib2.gz file, and return the path to the decompressed .grib2 file.
    Caller is responsible for deleting the returned file.
    """
    naive_dt  = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M")
    eastern_dt = naive_dt.replace(tzinfo=ZoneInfo("America/New_York"))
    utc_dt     = eastern_dt.astimezone(ZoneInfo("UTC"))

    if utc_dt.minute >= 30:
        utc_rounded = utc_dt.replace(second=0, microsecond=0, minute=0) + timedelta(hours=1)
    else:
        utc_rounded = utc_dt.replace(second=0, microsecond=0, minute=0)

    r_date = utc_rounded.strftime("%Y%m%d")
    r_time = utc_rounded.strftime("%H00")

    url = (
        f"https://mtarchive.geol.iastate.edu/{r_date[:4]}/{r_date[4:6]}/{r_date[6:8]}"
        f"/mrms/ncep/MultiSensor_QPE_24H_Pass2/"
        f"MultiSensor_QPE_24H_Pass2_00.00_{r_date}-{r_time}00.grib2.gz"
    )

    print(f"  Input (ET):   {eastern_dt.strftime('%Y-%m-%d %I:%M %p %Z')}")
    print(f"  Target (UTC): {utc_rounded.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Downloading...", end=" ", flush=True)

    response = requests.get(url, timeout=120)
    response.raise_for_status()
    print("done.")

    with tempfile.NamedTemporaryFile(suffix=".grib2.gz", delete=False) as tmp_gz:
        tmp_gz.write(response.content)
        gz_path = tmp_gz.name

    grib_path = gz_path.replace(".gz", "")
    with gzip.open(gz_path, "rb") as f_in, open(grib_path, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    os.remove(gz_path)

    return grib_path


def _mean_rainfall_in_polygon(data_values, lats, lons_180, geom):
    """
    Return the mean MRMS rainfall (mm) over all grid-cell centers inside `geom`.
    Falls back to the nearest grid cell if the polygon is smaller than one
    MRMS pixel (~1 km).

    Parameters
    ----------
    data_values : np.ndarray, shape (n_lat, n_lon)
    lats        : 1-D array, latitude values (degrees N)
    lons_180    : 1-D array, longitude values (-180 to 180)
    geom        : shapely geometry in WGS-84
    """
    minx, miny, maxx, maxy = geom.bounds

    lat_indices = np.where((lats >= miny) & (lats <= maxy))[0]
    lon_indices = np.where((lons_180 >= minx) & (lons_180 <= maxx))[0]

    def _nearest_centroid():
        cx, cy = geom.centroid.x, geom.centroid.y
        li  = int(np.argmin(np.abs(lats     - cy)))
        loi = int(np.argmin(np.abs(lons_180 - cx)))
        v   = float(data_values[li, loi])
        return round(v, 2) if v >= 0 else None

    if len(lat_indices) == 0 or len(lon_indices) == 0:
        return _nearest_centroid()

    vals = []
    for li in lat_indices:
        for loi in lon_indices:
            if geom.contains(Point(float(lons_180[loi]), float(lats[li]))):
                v = float(data_values[li, loi])
                if v >= 0:      # MRMS fill values are negative (e.g. -3)
                    vals.append(v)

    if vals:
        return round(float(np.mean(vals)), 2)

    # Polygon smaller than one grid cell — use nearest centroid
    return _nearest_centroid()


# ---------------------------------------------------------------------------
# Main processing function
# ---------------------------------------------------------------------------

def process_sites(shapefile_path, shp_id_col,
                  data_file,     data_id_col, date_col, time_col):
    """
    Join shapefile polygons to a data spreadsheet by ID, then compute
    mean areal MRMS rainfall for each row's date/time.

    Groups rows by unique (date, time) so each MRMS file is only downloaded once.
    Appends a 'Rainfall_24H_mm' column and saves results back to `data_file`.
    """

    # 1. Load and reproject shapefile ------------------------------------
    print(f"\nReading shapefile...")
    gdf = gpd.read_file(shapefile_path)
    print(f"  Found {len(gdf)} polygons.")

    if gdf.crs is None:
        print("  Warning: shapefile has no CRS defined. Assuming WGS84 (EPSG:4326).")
    elif gdf.crs.to_epsg() != 4326:
        print(f"  Reprojecting from {gdf.crs.to_string()} to WGS84...")
        gdf = gdf.to_crs(epsg=4326)

    # Build a lookup: site_id (string) -> shapely geometry
    site_geoms = {str(v): geom for v, geom in zip(gdf[shp_id_col], gdf.geometry)}

    # 2. Load data file --------------------------------------------------
    print(f"\nReading data file...")
    if data_file.lower().endswith(".csv"):
        df = pd.read_csv(data_file)
    else:
        df = pd.read_excel(data_file)
    print(f"  Found {len(df)} rows.")

    # Normalise date/time to clean strings (handles numeric storage in Excel)
    df["_date"] = df[date_col].apply(lambda x: str(int(float(x))))
    df["_time"] = df[time_col].apply(lambda x: str(int(float(x))).zfill(4))

    # 3. Process each unique (date, time) group --------------------------
    results = pd.Series(index=df.index, dtype=object)
    unique_groups = df.groupby(["_date", "_time"], sort=False)

    print(f"\nFound {unique_groups.ngroups} unique date/time combination(s) across {len(df)} rows.")

    for (date_str, time_str), group in unique_groups:
        print(f"\n--- Date: {date_str}  Time: {time_str} ET  ({len(group)} row(s)) ---")

        grib_path = _download_mrms(date_str, time_str)
        try:
            ds = xr.open_dataset(
                grib_path, engine="cfgrib", backend_kwargs={"indexpath": ""}
            )
            var_name    = list(ds.data_vars)[0]
            da          = ds[var_name]
            data_values = da.values
            lats        = da.latitude.values
            lons_raw    = da.longitude.values
            lons_180    = np.where(lons_raw > 180, lons_raw - 360, lons_raw)

            for row_idx, row in group.iterrows():
                site_id = str(row[data_id_col])
                print(f"  Site {site_id}...", end=" ", flush=True)

                geom = site_geoms.get(site_id)
                if geom is None:
                    print(f"WARNING: '{site_id}' not found in shapefile.")
                    results[row_idx] = f"Error: Site ID '{site_id}' not in shapefile"
                    continue

                val = _mean_rainfall_in_polygon(data_values, lats, lons_180, geom)
                results[row_idx] = val if val is not None else float("nan")
                print(f"{val} mm" if val is not None else "no data")

            ds.close()

        except requests.HTTPError as e:
            print(f"  Could not fetch MRMS data: {e}")
            for row_idx in group.index:
                results[row_idx] = f"Error: {e}"
        finally:
            if os.path.exists(grib_path):
                os.remove(grib_path)

    # 4. Append results and save back to original file -------------------
    df.drop(columns=["_date", "_time"], inplace=True)
    df["Rainfall_24H_mm"] = results.values

    if data_file.lower().endswith(".csv"):
        df.to_csv(data_file, index=False)
    else:
        df.to_excel(data_file, index=False)

    print(f"\nDone! Results saved to: {data_file}")
    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _pick_column(df, prompt):
    """Show the user the available columns and return their chosen column name."""
    print(f"\n  Available columns: {list(df.columns)}")
    col = input(f"  {prompt} ").strip()
    while col not in df.columns:
        print(f"  Column '{col}' not found. Please try again.")
        print(f"  Available columns: {list(df.columns)}")
        col = input(f"  {prompt} ").strip()
    return col


if __name__ == "__main__":
    print("=" * 60)
    print("   MRMS 24-Hour Mean Areal Precipitation Tool")
    print("   Computes mean rainfall over catchment polygons")
    print("=" * 60)
    print()
    print("Tip: In Windows, right-click a file and choose 'Copy as path',")
    print("     then paste here. You may need to remove the quote marks.")
    print()

    # --- Shapefile ---
    shp_path = input("(1) Enter path to the shapefile (.shp): ").strip().strip('"')
    try:
        _gdf_preview = gpd.read_file(shp_path)
        shp_id_col = _pick_column(_gdf_preview, "Which column is the ID?")
    except Exception as e:
        print(f"\nError reading shapefile: {e}")
        input("\nPress Enter to exit...")
        raise SystemExit

    # --- Data file ---
    print()
    data_path = input("(2) Enter path to data file (.csv or .xlsx): ").strip().strip('"')
    try:
        if data_path.lower().endswith(".csv"):
            _df_preview = pd.read_csv(data_path)
        else:
            _df_preview = pd.read_excel(data_path)
        data_id_col = _pick_column(_df_preview, "Which column is the ID (to match shapefile)?")
        date_col    = _pick_column(_df_preview, "Which column contains the Date (YYYYMMDD)?")
        time_col    = _pick_column(_df_preview, "Which column contains the Time (HHMM, Eastern Time)?")
    except Exception as e:
        print(f"\nError reading data file: {e}")
        input("\nPress Enter to exit...")
        raise SystemExit

    # --- Run ---
    print()
    try:
        results = process_sites(
            shp_path, shp_id_col,
            data_path, data_id_col, date_col, time_col
        )
        preview_cols = [c for c in [data_id_col, date_col, time_col, "Rainfall_24H_mm"]
                        if c in results.columns]
        print("\n--- Results Preview ---")
        print(results[preview_cols].to_string(index=False))

    except Exception as e:
        print(f"\nError: {e}")

    input("\nPress Enter to exit...")
