# MRMS 24-Hour Rainfall Fetcher

This repository contains tools to programmatically retrieve 24-hour rainfall accumulation (QPE Pass 2) from the NOAA Multi-Radar Multi-Sensor (MRMS) archive. 

---

## 🛠 Choose Your Tool

| File | Best For... | Input Method |
| :--- | :--- | :--- |
| **`single_rainfall_24Hr.exe`** | Quick, single-location checks. | Manual entry in the terminal. |
| **`batch_rainfall_24Hr.exe`** | Processing site lists or sensor networks. | Uploading a `.csv` or `.xlsx` spreadsheet. |

---

## 📅 Data Formatting Guide

To ensure the script successfully finds the archived data, please follow these formats exactly:

* **Date:** `YYYYMMDD` (e.g., `20260316` for March 16, 2026).
* **Time:** `HHMM` in 24-hour format (e.g., `0930` for 9:30 AM or `1415` for 2:15 PM).
* **Timezone:** The tool assumes all input is in **Eastern Time (ET)**.
* **Rounding:** The archive stores data hourly. The tool automatically rounds your input to the nearest whole hour (e.g., `12:25 PM` rounds to the `12:00 UTC` file; `12:35 PM` rounds to the `13:00 UTC` file).

---

## 📊 Batch Processing Example (`sites.csv`)

If using the **Batch Tool**, your spreadsheet must include the following headers (case-sensitive):

| Latitude | Longitude | Date | Time |
| :--- | :--- | :--- | :--- |
| 36.0476 | -78.9241 | 20260316 | 1200 |
| 35.9132 | -79.0558 | 20260316 | 0830 |
| 36.1234 | -78.1234 | 20260315 | 2215 |

### Entering the File Path
When the tool asks for the input file, it is best to provide the **full file path** to ensure the script can find your data.

**Example Path:** `C:\Users\Name\Documents\Research\sites.csv`

> **💡 Pro-Tip:** In Windows, you can right-click your CSV file and select **"Copy as path"**. Then, simply right-click inside the tool's terminal window to paste it! (Note: You may need to remove the quotation marks around the path after pasting).

**Note on Output:** To keep your workspace clean, the batch tool **edits your input file directly**. It will append a new column titled `Rainfall_24H_mm` to your existing spreadsheet once the processing is complete.
---

## 🚀 Installation & Usage

### For Non-Technical Users (Windows)
1.  Navigate to the **[Releases](https://github.com/inmang13/MRMS-QPE-24-Hour-Rainfall/releases)** section of this repository.
2.  Download the `.exe` version you need.
3.  Double-click the file to run. 
    * *Note: Windows may show a "Protected your PC" warning. Click **More Info** -> **Run Anyway**.*
4.  Follow the on-screen prompts.

### For Developers (Python)
If you wish to run or modify the source code:
1.  Clone the repository:
    ```bash
    git clone [https://github.com/inmang13/MRMS-QPE-24-Hour-Rainfall.git](https://github.com/inmang13/MRMS-QPE-24-Hour-Rainfall.git)
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  **System Requirement:** You must have `eccodes` installed (via `conda install -c conda-forge eccodes`) to decode the GRIB2 weather files.

## 🤖 Technical Note
The development of these scripts and their transformation into user-ready Windows executables was aided by **Gemini (Google AI)**.

## 📜 Acknowledgments
Data is sourced from the [Iowa Environmental Mesonet (IEM) MTArchive](https://mtarchive.geol.iastate.edu/). This tool was developed for use in water resources research at Duke University. 