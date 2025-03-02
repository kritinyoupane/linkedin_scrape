from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import sys
import itertools


def loading_animation(message, duration=5):
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f"\r{message} {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\rDone!                     \n")


max_pages = 5 


chrome_options = Options()

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.linkedin.com/login")
time.sleep(2)

username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password")

username.send_keys("Your email")
password.send_keys("Your password")

loading_animation("Signing in...")
password.send_keys(Keys.RETURN)
time.sleep(3)

target_url = "https://www.linkedin.com/search/results/people/?keywords=python%20developers%20in%20kathmandu&origin=CLUSTER_EXPANSION&sid=9uY"
print(f"Navigating to search page: {target_url}")
driver.get(target_url)
time.sleep(5)


def auto_scroll():
    scroll_pause_time = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        # Calculate new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Exit the loop when no more content to scroll
        last_height = new_height


def extract_profiles():
    auto_scroll()
    profiles = driver.find_elements(By.CLASS_NAME, "linked-area.flex-1.cursor-pointer")
    for profile in profiles:
        try:
            name_element = profile.find_element(
                By.CSS_SELECTOR, "span[aria-hidden='true']"
            )
            name = name_element.text.strip() if name_element else ""

            link_element = profile.find_element(By.TAG_NAME, "a")
            profile_link = link_element.get_attribute("href") if link_element else ""

            title_element = profile.find_element(
                By.CLASS_NAME, "TprpsUPltxghzRAzIhrQAIywZXWaxYIMnTZ"
            )
            title = title_element.text.strip() if title_element else ""

            location_element = profile.find_element(
                By.CLASS_NAME, "shiVWSRcOGIFALybpHnoAmRKqCkgQDYlLBRelU"
            )
            location = location_element.text.strip() if location_element else ""

            extracted_data.append([name, profile_link, title, location])
        except Exception as e:
            print("Error extracting profile:", e)
            continue


extracted_data = []
current_page = 1

while current_page <= max_pages:
    print(f"Scraping page {current_page}...")
    extract_profiles()

    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@aria-label, 'Next')]")
            )
        )
        next_button.click()
        time.sleep(5) 
        current_page += 1
    except Exception:
        print("No more pages or pagination button not found.")
        break

df = pd.DataFrame(extracted_data, columns=["Name", "Profile Link", "Title", "Location"])
df.to_csv("python_developers.csv", index=False)

print(
    f"Data saved to 'python_developers.csv'. Scraped {len(extracted_data)} profiles from {current_page} pages."
)

driver.quit()
