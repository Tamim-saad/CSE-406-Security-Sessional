import time
import json
import os
import signal
import sys
import random
import traceback
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import database
from database import Database

WEBSITES = [
    "https://www.youtube.com/",
    "https://cse.buet.ac.bd/moodle/",
    "https://google.com",
    "https://cses.fi/problemset/",
]

TRACES_PER_SITE = 1000
FINGERPRINTING_URL = "http://localhost:5000" 
OUTPUT_PATH = "dataset.json"
# driver_path = "/home/admin123/chromedriver/chromedriver"
driver_path = "/home/pridesys/chromedriver/chromedriver"
database.db = Database(WEBSITES)
database.db.init_database()

def signal_handler(sig, frame):
    print("\nReceived termination signal. Exiting gracefully...")
    try:
        database.db.export_to_json(OUTPUT_PATH)
    except:
        pass
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def is_server_running(host='127.0.0.1', port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def setup_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    # ---------
    # chrome_options.add_argument("--headless")  # Optional if you want headless
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # service = Service(ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def retrieve_traces_from_backend(driver):
    traces = driver.execute_script("""
        return fetch('/api/get_traces')
            .then(response => response.ok ? response.json() : [])
            .catch(() => []);
    """)
    count = len(traces) if traces else 0
    print(f"  - Retrieved {count} traces from backend API" if count else "  - No traces found in backend storage")
    return traces or []

def clear_trace_results(driver, wait):
    clear_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Clear all results')]")
    clear_button.click()

    wait.until(EC.text_to_be_present_in_element(
        (By.XPATH, "//div[contains(@class, 'alert') or @role='alert']"), "All results cleared successfully!"))

def is_collection_complete():
    current_counts = database.db.get_traces_collected()
    remaining_counts = {website: max(0, TRACES_PER_SITE - count) 
                      for website, count in current_counts.items()}
    return sum(remaining_counts.values()) == 0

# ------------------ FULL IMPLEMENTATION STARTS HERE ------------------

def collect_single_trace(web_driver, web_wait, site_url):
    try:
        idx = WEBSITES.index(site_url)  # get index by searching the url in your list

        print(f"\n[*] Collecting trace for: {site_url} (Index: {idx})")

        # Step 1: Open fingerprinting website
        web_driver.get(FINGERPRINTING_URL)
        time.sleep(1)

        # Step 2: Click collect trace button
        btn_collect = web_wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Collect Trace Data')]"))
        )
        btn_collect.click()
        time.sleep(1)

        # Step 3: Open target website in new tab
        web_driver.execute_script("window.open('');")
        web_driver.switch_to.window(web_driver.window_handles[1])
        web_driver.get(site_url)
        print(f"  - Opened {site_url}")

        # Step 4: Interact (scroll)
        time.sleep(2)
        web_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        web_driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)

        # Step 5: Close target tab, switch back
        web_driver.close()
        web_driver.switch_to.window(web_driver.window_handles[0])
        print("  - Closed target tab")

        # Step 6: Wait for trace collection complete alert
        web_wait.until(
            EC.text_to_be_present_in_element(
                (By.XPATH, "//div[contains(@class, 'alert') or @role='alert']"),
                "Trace collection complete!"
            )
        )

        # Step 7: Retrieve traces and save to DB
        trace_list = retrieve_traces_from_backend(web_driver)
        if trace_list:
            database.db.save_trace(site_url, idx, trace_list[-1])
            print("  - Trace saved to local DB")
            return True
        else:
            print("  - No new trace found")
            return False

    except ValueError:
        print(f"Website URL not found in websites list: {site_url}")
        return False
    except Exception as err:
        print(f"Error during single trace collection: {str(err)}")
        traceback.print_exc()
        return False

def collect_fingerprints(driver, target_counts=None):
    wait = WebDriverWait(driver, 30)
    new_traces = 0

    if target_counts is None:
        target_counts = {website: TRACES_PER_SITE for website in WEBSITES}

    while not is_collection_complete():
        for website in WEBSITES:
            current_count = database.db.get_traces_collected().get(website, 0)
            remaining = target_counts[website] - current_count

            if remaining > 0:
                print(f"\nWebsite: {website} | Current: {current_count} | Remaining: {remaining}")

                success = collect_single_trace(driver, wait, website)
                if success:
                    new_traces += 1

                time.sleep(2)  # Optional delay between requests

    return new_traces

def main():
    while True:
        try:
            if not is_server_running():
                print("Error: Fingerprinting server not running. Start Flask server first.")
                time.sleep(10)
                continue

            driver = setup_webdriver()
            print("\n[*] WebDriver launched successfully")

            wait = WebDriverWait(driver, 30)
            driver.get(FINGERPRINTING_URL)
            print("[*] Opened fingerprinting app")

            # Optional: clear existing results on backend before starting
            
            # Start trace collection loop
            total_new_traces = collect_fingerprints(driver)

            print(f"\n[*] Total new traces collected: {total_new_traces}")

            # Export local DB to file
            database.db.export_to_json(OUTPUT_PATH)
            print(f"[*] Exported dataset to {OUTPUT_PATH}")

            break

        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            traceback.print_exc()
            print("Retrying after 10 seconds...\n")
            time.sleep(10)

        finally:
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    main()