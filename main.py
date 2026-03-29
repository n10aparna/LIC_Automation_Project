import os
import re
import time
import json
import shutil
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from UI.ui_input import get_user_inputs


# -------------------- USER INPUT --------------------
env = get_user_inputs()
file_path, fail_retries, flag_mark = env["file_path"], env["retries"], env["flag"]

flag = {
    "A": "untried",
    "B": "only error",
    "C": "all false"
}.get(flag_mark, "untried")

# ----------------- LOAD DATA FROM INPUT ----------------
with open(file_path, "r") as f:
    data = json.load(f)

# print(data)

# -------------------- FILE PATH --------------------
output_file_path = "output.json"

# -------------------- BACKUP --------------------
if os.path.exists(output_file_path):
    os.makedirs("backups", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/output_backup_{timestamp}.json"
    shutil.copy(output_file_path, backup_file)
    print(f"Backup created: {backup_file}")


# -------------------- LOAD DATA --------------------
# if not os.path.exists(output_file_path):
print("Creating output file from input...")

with open(output_file_path, "w") as f:
    json.dump(data, f, indent=4)



# -------------------- DEFAULT FIELDS --------------------
for record in data:
    record.setdefault("F.U.P. New", "")
    record.setdefault("Policy Status", "")
    record.setdefault("Last Premium Paid", "")
    record.setdefault("Last Updated On", "")
    record.setdefault("Updated", False)
    record.setdefault("Remarks", "")


def format_dob(dob_str):
    try:
        return datetime.strptime(dob_str, "%d-%m-%Y").strftime("%d-%m-%Y")
    except:
        print("unable to fix the date type")
        return dob_str

for record in data:
    record["D.O.B."] = format_dob(record.get("D.O.B.", ""))

# -------------------- HELPERS --------------------
def get_input_box(driver):
    time.sleep(4)
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
        return "Limit hit"
    elif "Sorry" in visible_text:
        return visible_text

    raw_text = driver.execute_script(
        "return arguments[0].textContent;", last_msg
    )

    if "FUP Date" in raw_text:
        print("Data fetched")
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

    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "corover-cb-widget"))
    ).click()

    WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "corover-chat-frame"))
    )

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Get Started']")
        )
    ).click()

    time.sleep(5)

    driver.execute_script(
        "arguments[0].click();",
        driver.find_element(By.XPATH, "//button[.//span[normalize-space()='LIC Services']]")
    )

    time.sleep(5)

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

    input_box = get_input_box(driver)
    input_box.send_keys(dob)
    time.sleep(2)
    input_box.send_keys(Keys.ENTER)

    time.sleep(10)

    return print_lastmess(driver)


def safe_run(driver, policy, dob, retries=2):
    for _ in range(retries):
        response = fetch_policy_data(driver, policy, dob)
        if "Sorry" not in response or response == "Limit hit":
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
    driver = webdriver.Chrome(options=Options())
    driver.get("https://licindia.in/")

    if opening_chatBox(driver):
        print("Chatbot ready")
        return driver


def save_json():
    with open(output_file_path, "w") as file:
        json.dump(data, file, indent=4)


# -------------------- MAIN FLOW --------------------
batch = 0
bot_driver = launch_driver()

for index, row in enumerate(data):

    # -------- FLAG LOGIC --------
    if flag == "untried":
        if row["Updated"] is True:
            print(f"Skipping row {index} (already updated)")
            continue
        if row["Updated"] is False and row["Remarks"].lower() == "unable to fetch":
            print(f"Skipping this record at row {index} as its was 'Unable to fetch' data for this {row['Policy No']} and {row['D.O.B.']}")
            continue

    elif flag == "only error":
        if not (row["Updated"] is False and row["Remarks"].lower() == "unable to fetch"):
            print(f"Skipping row {index} (already updated)")
            continue

    elif flag == "all false":
        if row["Updated"] is True:
            print(f"Skipping row {index} (already updated)")
            continue

    policy_no = str(row["Policy No"])
    dob = row["D.O.B."]

    print(f"\nProcessing {policy_no} with {dob}")

    result = safe_run(bot_driver, policy_no, dob, fail_retries)

    if "Sorry" in result:
        data[index]["Updated"] = False
        data[index]["Remarks"] = "Unable to fetch"
        print("No response")
        continue

    if result == "Limit hit":
        raise Exception("IP exhausted")

    extracted = extract_details(result)

    if extracted:
        data[index]["F.U.P. New"] = extracted.get("F.U.P.", "")
        data[index]["Policy Status"] = extracted.get("Policy Status", "")
        data[index]["Last Premium Paid"] = extracted.get("Last Premium Paid", "")
        data[index]["Last Updated On"] = datetime.now().strftime("%d-%m-%Y %H:%M")
        data[index]["Updated"] = True
        data[index]["Remarks"] = "Success"
        print("Data Collected")
    else:
        data[index]["Updated"] = False
        data[index]["Remarks"] = "Parsing failed"

    batch += 1

    # -------- PERIODIC SAVE --------
    if index % 4 == 0:
        save_json()
        print(f"Saved at index {index}")

    # -------- RESTART DRIVER --------
    if batch == 5:
        bot_driver.quit()
        print("Waiting 3 minutes...")
        save_json()
        print(f"Saved at index {index}")
        time.sleep(180)
        bot_driver = launch_driver()
        batch = 0


# Final save
save_json()

if bot_driver:
    bot_driver.quit()

print("\n Process completed!")