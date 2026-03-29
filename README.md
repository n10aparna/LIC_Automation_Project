# LIC Policy Automation Bot

## Overview

This project automates LIC policy data fetching using Selenium and processes Excel records.

It includes:

* UI for input (file + retries + mode)
* Automated chatbot interaction
* Excel update with results

---

##  Setup Instructions

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

##  How to Run

```bash
python main.py
```

---

## Processing Modes

* **A (Untried)** → Processes new records only
* **B (Only Error)** → Processes failed records
* **C (All False)** → Processes all false entries

---

## Built-in Libraries Used

(No installation required)

* re
* time
* datetime
* tkinter

---

##  Notes

* Ensure Chrome browser is installed
* Internet connection required
* Do not close browser during execution

---

## ⚠️ Important Usage Instructions

* 🚫 **Do NOT open the output file (`output.xlsx`) during execution**
  Opening the file while the script is running may cause write conflicts or data corruption.

* 👀 **If you need to view progress:**
  Make a copy of the output file and open the copy instead.

* 🔁 **If the script stops/crashes in between:**
  Re-run the script using the existing `output.xlsx` as input.
  The script is designed to resume processing based on the selected mode.

* 💾 **All updates are saved in the output file only**
  The original input file remains unchanged.

* ⏳ **Do not interrupt the browser or network during execution**
  This may result in incomplete or failed data extraction.

---

## 📁 Backup File Handling

* 🔐 Before each run, the script automatically creates a backup of the existing output file.

* 🕒 Backup files are saved with an incremental count (if duplicates) format:

  ```
  output_backup_{count}.xlsx
  ```

* 📂 All backups can be stored in the same directory or inside a `backups/` folder (if configured).

* ⚠️ Backup files ensure that no data is lost if:

  * The script crashes
  * The system shuts down
  * Unexpected errors occur during execution

* ♻️ Multiple backups are maintained — **existing backups are NOT overwritten**

* 🧹 (Optional) Old backups can be cleaned manually if storage becomes large


##  Author

Automation Script for LIC Data Extraction
LIC_Automation_Project.zip
│
├── main.py
├── requirements.txt
├── README.md
├── output.xlsx            
│
├── UI/
│   └── ui_input.py
│
├── backups/               
│
└── data/sample_input.xlsx      
