from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import platform
import time
from datetime import datetime
import glob
import pandas as pd
from upload_to_azure import upload_to_azure
from io import BytesIO
# Initialize WebDriver

def log_message(message,logs):
    """Log a message to the in-memory log."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logs.write(f"[{timestamp}] {message}\n")
    logs.flush()

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
def main(logs):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)
        wait = WebDriverWait(driver, 10)
    except Exception as e:
        log_message("Error initializing chrome helper with error:",logs)
        log_message(e,logs)
        return 0
    try:
        # Open the login page
        try:
            driver.get(login_url)
        except Exception as e:
            log_message("Error while opening website...",logs)
            return 0
            
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
        try:
            wait.until(EC.presence_of_element_located((By.ID, 'highcharts-0')))  # Replace 'dashboard' with an element ID on the next page
        except Exception as e:
            log_message("Error while logging in",logs)
            log_message("This has been known to happen once or twice per run",logs)
            log_message("Please report if occured more than twice",logs)
            return 0
        # Navigate to the sales report page
        driver.get(sales_report_url)  # Replace with the actual sales report URL
        time.sleep(30)
        try:
            date_picker = wait.until(EC.element_to_be_clickable((By.ID, "filter-timestamp")))
        except:
            log_message("Extenda GO timeout error",logs)
            log_message("This has been known to happen sometimes",logs)
            log_message("Please report if occuring frequently",logs)
            return 0

        date_picker.click()
        time.sleep(10)
        # Step 2: Set today's date
        # Clear existing value
        today_button = None
        try:
            calendar = driver.find_element(By.CLASS_NAME, "daterangepicker.ltr.auto-apply.show-ranges.show-calendar.opensleft")
            
            today_button = calendar.find_element(By.XPATH, "//td[contains(@class, 'today') and contains(@class, 'available')]")
        except Exception as e:
            log_message("Error while setting dates",logs)
            log_message("The UI for the calendar is constantly changed so please report if frequently occuring",logs)
            log_message(e,logs)
            return 0

        # Enter today's date
        today_button.click()
        time.sleep(5)
        today_button = calendar.find_element(By.XPATH, "//td[contains(@class, 'active') and contains(@class, 'today')]")

        today_button.click()
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
        log_message('Downloading....',logs)
        time.sleep(100)
        pattern = os.path.join(download_dir, 'sales_report*')
        files = glob.glob(pattern)
        try:
            downloaded_file = max(files, key=os.path.getctime)  # Get the most recently created file
        except Exception as e:
            log_message("Error while finding files",logs)
            log_message(e,logs)
            return 0

        if os.path.exists(downloaded_file):
            df = pd.read_csv(downloaded_file,delimiter=';')
            if 'Shop' in df.columns:
                grouped_data = {shop: group for shop, group in df.groupby('Shop')}
                # Save separated DataFrames
                for shop_name, shop_df in grouped_data.items():
                    # Convert DataFrame to CSV in memory
                    output = BytesIO()
                    shop_df.to_csv(output, index=False,sep=';')  # Write DataFrame as CSV to BytesIO
                    output.seek(0)
                    # Define the blob name
                    blob_name = f"{shop_name.replace(' ', '_').replace('/', '_')}_sales.csv"
                    
                    # Upload the CSV to Azure Blob Storage
                    try:
                        upload_to_azure(df=output,name=blob_name)
                    except Exception as e:
                        log_message('Azure upload failed',logs)
                        log_message(e,logs)
                        return 0

            
        else:
            log_message("Sales not found!",logs)
            return 0

            
    except Exception as e:
        log_message("Unknown error occured.",logs)
        log_message("If this is the first or the second time this function ran then it is known to happen.",logs)
        log_message("Please report if occuring frequently",logs)
        log_message(e,logs)
        return


    finally:
        # Close the WebDriver
        driver.quit()
        return 1
