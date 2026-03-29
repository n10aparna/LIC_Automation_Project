import os
import re
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openpyxl
from UI.ui_input import get_user_inputs
import shutil
import os

env = get_user_inputs()
file_path, fail_retries, flag_mark = env["file_path"], env["retries"], env["flag"]

# flag : "untried" --> False without remark or only untried ones
# flag : "only error"   --> False only with remark 'unable to fetch'
# flag : "all false"  --> All those marked false
if flag_mark == "A":
    flag = "untried"
elif flag_mark == "B":
    flag = "only error"
else:
    flag = "all false"
# print(flag_mark, flag)



# -------------------- Load Excel --------------------
df = pd.read_excel(file_path)

output_file_path = "output.xlsx"

# -------- Backup previous Outputfile ---------
backup_file = "backups/output_backup.xlsx"
count = 1
while os.path.exists(backup_file):
    backup_file = f"output_backup_{count}.xlsx"
    count += 1
shutil.copy(output_file_path, backup_file)
print(f"📁 Backup created: {backup_file}")


# -------------------- Output File Handling --------------------
if not os.path.exists(output_file_path):
    print("📁 Output file not found. Creating new output file...")

    df = pd.read_excel(file_path)
    df.to_excel(output_file_path, index=False)

    print("✅ Output file created with initial data")



# Ensure required columns exist
for col, default in {
    "F.U.P. New": "",
    "Last Updated On": "",
    "Updated": False,
    "Remarks": ""
}.items():
    if col not in df.columns:
        df[col] = default

# Format DOB
df["D.O.B."] = pd.to_datetime(
    df["D.O.B."], errors="coerce", dayfirst=True
).dt.strftime("%d-%m-%Y")


# -------------------- Helpers --------------------
def get_input_box(driver):
    return WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Type a message...']")
        )
    )


def print_lastmess(driver):
    messages = driver.find_elements(By.XPATH, "//div[contains(@class,'justify-start')]")
    last_msg = messages[-1]

    visible_text = last_msg.text

    if "Checking" in visible_text or "Understanding" in visible_text:
        time.sleep(20)
    elif "" == visible_text:
        print("may the limit is hit please check manually over same network then try again.")
        return "Limit hit"
    elif "Sorry" in visible_text:
        print("❌ Failed:", visible_text)
        return visible_text

    raw_text = driver.execute_script(
        "return arguments[0].textContent;", last_msg
    )

    if "FUP Date" in raw_text:
        print("✅ Data fetched")
        return raw_text

    return "Sorry"


def opening_chatBox(driver):
    try:
        popup = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "welcome-popup"))
        )
        if popup:
            driver.find_element(By.ID, "englishBtn").click()
    except:
        pass

    widget = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "corover-cb-widget"))
    )
    widget.click()

    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.ID, "corover-chat-frame")
        )
    )

    get_started_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Get Started']")
        )
    )
    get_started_btn.click()
    time.sleep(5)

    licService = driver.find_element(
        By.XPATH,
        "//button[.//span[normalize-space()='LIC Services']]"
    )
    driver.execute_script("arguments[0].click();", licService)
    time.sleep(5)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class,'justify-start')]")
        )
    )

    input_box = get_input_box(driver)
    input_box.send_keys("pay premium", Keys.ENTER)
    time.sleep(5)

    return True


def fetch_policy_data(driver, policyNo, dob):

    input_box = get_input_box(driver)
    input_box.send_keys(policyNo)
    time.sleep(2)
    input_box.send_keys(Keys.ENTER)

    time.sleep(5)

    date_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@type='date']"))
    )
    date_input.send_keys(dob)
    time.sleep(1)
    submit_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[normalize-space()='Submit Date']]")
        )
    )
    submit_btn.click()

    time.sleep(10)

    return print_lastmess(driver)


def safe_run(driver, policy, dob, retries=2):
    for _ in range(retries):
        response = fetch_policy_data(driver, policy, dob)
        if "Sorry" not in response:
            return response
        elif response == "Limit hit":
            return response
        time.sleep(12)
    return response


def extract_details(text):
    try:
        return {
            "F.U.P.": re.search(r"FUP Date.*?:\s*(.*)", text).group(1),
            "Policy Status": re.search(r"Policy Status:\s*(.*)", text).group(1),
            "Last Premium Paid": re.search(r"Last Premium Paid:\s*(.*)", text).group(1),
        }
    except:
        return None


def launch_driver():
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.get("https://licindia.in/")

    if opening_chatBox(driver):
        print("✅ Chatbot ready")
        return driver


def index_flow(driver, i, r, df_policy, retries):

    policy_no = str(r["Policy No."])
    dob = r["D.O.B."]

    print(f"\n🔄 Processing {policy_no} | DOB: {dob}")

    policy_detail = safe_run(driver, policy_no, dob, retries=retries)

    # ❌ Failure case
    if "Sorry" in policy_detail:
        df_policy.at[i, "Updated"] = False
        df_policy.at[i, "Remarks"] = "Unable to fetch"
        print("❌ Failed to fetch data")
        return False
    elif "Limit hit" == policy_detail:
        raise "IP exhausted. Please check manually then try again!"

    # ✅ Success case
    extracted = extract_details(policy_detail)

    if extracted:
        df_policy.loc[i, ["F.U.P. New", "Policy Status", "Last Premium Paid"]] = [
            extracted.get("F.U.P.", ""),
            extracted.get("Policy Status", ""),
            extracted.get("Last Premium Paid", "")
        ]
        df_policy.at[i, "Last Updated On"] = datetime.now().strftime("%d-%m-%Y %H:%M")
        df_policy.at[i, "Updated"] = True
        df_policy.at[i, "Remarks"] = "Success"

        # batch += 1
        print("✅ Data saved")
        time.sleep(10)
    else:
        df_policy.at[i, "Updated"] = False
        df_policy.at[i, "Remarks"] = "Parsing failed"

    return True


# -------------------- Main Flow --------------------
batch = 0
bot_driver = launch_driver()

for index, row in df.iterrows():
    if flag == "untried":
        # ✅ Skip already updated rows and those through sorry
        if str(row["Updated"]).lower() == "true":
            print(f"⏩ Skipping row {index} (already updated)")
            continue
        elif str(row["Updated"]).lower() == "false" and str(row["Remarks"]).lower() == "unable to fetch":
            print(f"Skipping this record at row {index} as its was 'Unable to fetch' data for this {row['Policy No.']} and {row['D.O.B.']}")
            continue
    elif flag == "only error":
        # ✅ Skip already updated rows and does not throw error
        if not (str(row["Updated"]).lower() == "false" and str(row["Remarks"]).lower() == "unable to fetch"):
            print(f"⏩ Skipping row {index} (already updated)")
            continue
    elif flag == "all false":
        # ✅ Skip already updated rows
        if str(row["Updated"]).lower() == "true":
            print(f"⏩ Skipping row {index} (already updated)")
            continue

    # 💾 Save periodically (faster than every row)
    if int(index) % 4 == 0:
        df.to_excel(output_file_path, index=False)
        print(f"\nData saved to excel at index {index}")

    if batch == 0 and not bot_driver:
        bot_driver = launch_driver()

    isdata = index_flow(bot_driver,index, row, df, fail_retries)
    if isdata:
        batch += 1
    else:
        continue

    # 🔁 Restart driver after 5 records
    if batch == 5:
        bot_driver.quit()
        bot_driver = False
        batch = 0
        print("⏳ Waiting 3 minutes...")
        df.to_excel(output_file_path, index=False)
        print(f"\nData saved to excel at index {index}")
        time.sleep(180)


# Final save
df.to_excel(output_file_path, index=False)

if bot_driver:
    bot_driver.quit()

print("\n🎉 Process completed successfully!")



