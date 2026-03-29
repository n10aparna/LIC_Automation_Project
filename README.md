# LIC Policy Automation Bot

## Overview

This project automates LIC policy data fetching using Selenium and processes JSON records.

It includes:

* UI for input (file + retries + mode)
* Automated chatbot interaction
* JSON update with results

---

## Setup Instructions

### 1. Install Python (3.10+ recommended)

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## How to Run

```bash
python main.py
```

---

## Processing Modes

* **A (Untried)** → Processes new records only
* **B (Only Error)** → Processes failed records
* **C (All False)** → Processes all false entries

---

## Input Format (JSON)

Example `input.json`:

```json
[
  {
    "Policy No.": "123456789",
    "D.O.B.": "01-01-1990"
  }
]
```

---

## Built-in Libraries Used

(No installation required)

* re
* time
* datetime
* tkinter

---

## Notes

* Ensure Chrome browser is installed
* Internet connection required
* Do not close browser during execution
* Date format in JSON should be **DD-MM-YYYY**

---

## ⚠️ Important Usage Instructions


* 🔁 **If the script stops/crashes in between:**
  Re-run the script using the existing `output.json` as input.
  The script is designed to resume processing based on the selected mode.

* 💾 **All updates are saved in the output file only**
  The original input file remains unchanged.

* ⏳ **Do not interrupt the browser or network during execution**
  This may result in incomplete or failed data extraction.

---

## 📁 Backup File Handling

* 🔐 Before each run, the script automatically creates a backup of the existing output file.

* 🕒 Backup files are saved with a timestamp format:

  ```
  output_backup_YYYYMMDD_HHMMSS.json
  ```

* 📂 Backups are stored inside the `backups/` folder.

* ⚠️ Backup files ensure that no data is lost if:

  * The script crashes
  * The system shuts down
  * Unexpected errors occur during execution

* ♻️ Multiple backups are maintained — **existing backups are NOT overwritten**

---

## Author

Automation Script for LIC Data Extraction

---

## 📁 Project Structure

```
LIC_Automation_Project/
│
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── README.md
├── output.json          # Generated output
│
├── UI/
│   └── ui_input.py      # UI logic
│
├── backups/             # Backup files
│
└── data/
    └── sample_input.json
```
