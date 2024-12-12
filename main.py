from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import platform
import time
from datetime import datetime
import glob
import pandas as pd

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)


# URL and Credentials
login_url = 'https://wbo-etail.wallmob.com/login'  # Replace with the actual login URL
username = 'brian@lostacos.no'  # Replace with your username
password = '6F$x5L!dA'  # Replace with your password
sales_report_url = 'https://wbo-etail.wallmob.com/reports/sales'
today = datetime.today().strftime("%d.%m.%Y")
# Determine the default download folder
def get_download_directory():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    elif platform.system() == "Darwin":  # macOS
        return os.path.join(os.environ["HOME"], "Downloads")
    else:  # Linux
        return os.path.join(os.environ["HOME"], "Downloads")
try:
    # Open the login page
    driver.get(login_url)

    # Find and fill in the username
    username_field = wait.until(EC.presence_of_element_located((By.ID, 'LoginForm_username')))  # Replace 'username' with the actual ID
    username_field.send_keys(username)

    # Find and fill in the password
    password_field = driver.find_element(By.ID, 'LoginForm_password')  # Replace 'password' with the actual ID
    password_field.send_keys(password)
    # login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'button block-button ng-binding')))  # Replace with the actual ID
    time.sleep(10)
    # Submit the form
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
    login_button.click()
    # Wait until login is successful and the dashboard page is loaded
    wait.until(EC.presence_of_element_located((By.ID, 'highcharts-0')))  # Replace 'dashboard' with an element ID on the next page

    # Navigate to the sales report page
    driver.get(sales_report_url)  # Replace with the actual sales report URL
    time.sleep(30)
    date_picker = wait.until(EC.element_to_be_clickable((By.ID, "filter-timestamp")))
    date_picker.click()
    time.sleep(10)
    # Step 2: Set today's date
    # Clear existing value
    today_button = None
    try:
        calendar = driver.find_element(By.CLASS_NAME, "daterangepicker.ltr.auto-apply.show-ranges.show-calendar.opensleft")
        print(calendar)
        
        today_button = calendar.find_element(By.XPATH, "//td[contains(@class, 'today') and contains(@class, 'available')]")
        print(today_button, "today button")
    except Exception as e:
        print(e)
    print('date set')
    # Enter today's date
    today_button.click()
    print('ek click bho')
    time.sleep(5)
    today_button = calendar.find_element(By.XPATH, "//td[contains(@class, 'active') and contains(@class, 'today')]")

    today_button.click()
    print('dui click bho')
    time.sleep(30)
    download_all_button = wait.until(EC.element_to_be_clickable((By.ID, 'download-all-shops')))  # Replace with the actual ID
    download_all_button.click()
    # Step 3: Click the "Transactions CSV" link
    time.sleep(10)
    transaction_span = wait.until(
        EC.presence_of_element_located((By.XPATH, "//span[text()='Product sales CSV']"))
    )
    # Click the parent <a> tag of the span
    parent_link = transaction_span.find_element(By.XPATH, "./parent::a")
    parent_link.click()
    # Optional: Move or verify the downloaded file
    download_dir = get_download_directory()
    time.sleep(100)
    pattern = os.path.join(download_dir, 'sales_report*')
    files = glob.glob(pattern)
    downloaded_file = max(files, key=os.path.getctime)  # Get the most recently created file

    if os.path.exists(downloaded_file):
        df = pd.read_csv(downloaded_file,delimiter=';')
        df.to_csv('123.csv')

        
    else:
        print("Sales report not found.")
        
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the WebDriver
    driver.quit()
