# MRMS 24-Hour Rainfall Fetcher

This repository contains tools to programmatically retrieve 24-hour rainfall accumulation (QPE Pass 2) from the NOAA Multi-Radar Multi-Sensor (MRMS) archive.

---

## 🛠 Choose Your Tool

| File | Best For... | Input Method |
| :--- | :--- | :--- |
| **`single_rainfall_24Hr.exe`** | Quick, single-location checks. | Manual entry in the terminal. |
| **`batch_rainfall_24Hr.exe`** | Processing a list of point locations. | CSV or Excel spreadsheet. |
| **`polygon_rainfall.exe`** | Mean areal precipitation over catchment polygons. | Shapefile + CSV or Excel spreadsheet. |

---

## 📅 Data Formatting Guide

To ensure the script successfully finds the archived data, please follow these formats exactly:

* **Date:** `YYYYMMDD` (e.g., `20260316` for March 16, 2026).
* **Time:** `HHMM` in 24-hour format (e.g., `0930` for 9:30 AM or `1415` for 2:15 PM).
* **Timezone:** The tool assumes all input is in **Eastern Time (ET)**.
* **Rounding:** The archive stores data hourly. The tool automatically rounds your input to the nearest whole hour (e.g., `12:25 PM` rounds to the `12:00 UTC` file; `12:35 PM` rounds to the `13:00 UTC` file).

---

## 📊 Batch Processing (`batch_rainfall_24Hr.exe`)

Provide a spreadsheet with the following headers (case-sensitive):

| Latitude | Longitude | Date | Time |
| :--- | :--- | :--- | :--- |
| 36.0476 | -78.9241 | 20260316 | 1200 |
| 35.9132 | -79.0558 | 20260316 | 0830 |

The tool appends a `Rainfall_24H_mm` column directly to your input file.

---

## 🗺 Polygon / Catchment Processing (`polygon_rainfall.exe`)

Computes **mean areal precipitation (MAP)** — the average 24-hour rainfall depth (mm) over each catchment polygon. This is the standard input for rainfall-runoff models.

This tool takes two inputs:

**1. A reference shapefile** containing your catchment polygons, with a column that uniquely identifies each site (e.g., `Sample_ID`).

**2. A spreadsheet (CSV or Excel)** with one row per sample event, containing at minimum:

| Site_ID | Date | Time |
| :--- | :--- | :--- |
| 1.02 | 20260316 | 1200 |
| 5.00 | 20260316 | 0830 |
| 10.01 | 20260315 | 2215 |

The tool will prompt you to identify the relevant column names in both files, so headers do not need to match exactly. Results are appended as a `Rainfall_24H_mm` column directly to your spreadsheet.

> **Note on small polygons:** The MRMS grid resolution is ~1 km. Polygons smaller than one grid cell will automatically fall back to the nearest grid-cell value.

---

## 🚀 Installation & Usage

### For Non-Technical Users (Windows)
1. Navigate to the **[Releases](https://github.com/inmang13/MRMS-QPE-24-Hour-Rainfall/releases)** section of this repository.
2. Download the `.exe` version you need.
3. Double-click the file to run.
   * *Note: Windows may show a "Protected your PC" warning. Click **More Info** → **Run Anyway**.*
4. Follow the on-screen prompts.

### For Developers (Python)
1. Clone the repository:
   ```bash
   git clone https://github.com/inmang13/MRMS-QPE-24-Hour-Rainfall.git
   ```
2. Install dependencies:
   ```bash
   conda install -c conda-forge eccodes geopandas
   pip install -r requirements.txt
   ```

---

## 🤖 Technical Note
The development of these scripts and their transformation into user-ready Windows executables was aided by **Gemini (Google AI)** and **Claude (Anthropic)**.

## 📜 Acknowledgments
Data is sourced from the [Iowa Environmental Mesonet (IEM) MTArchive](https://mtarchive.geol.iaesta.edu/). This tool was developed for use in water resources research at Duke University.
