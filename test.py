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

# Function to display a "Signing in..." animation
def loading_animation(message, duration=5):
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f'\r{message} {next(spinner)}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!                     \n')

# Configurable maximum number of pages to scrape
max_pages = 25  # Change this variable to adjust the page limit


chrome_options = Options()
# Initialize options for headless mode (if you want to run the script without opening a browser window)

# chrome_options.add_argument("--headless")  # Enable headless mode
# chrome_options.add_argument("--disable-gpu")  # Recommended for headless mode
# chrome_options.add_argument("--no-sandbox")  # Useful for Linux systems
# chrome_options.add_argument("--disable-dev-shm-usage")  # Handle large memory usage

# Replace your existing WebDriver initialization with this
driver = webdriver.Chrome(options=chrome_options)

# Step 1: Open LinkedIn Login Page
driver.get("https://www.linkedin.com/login")
time.sleep(2)

# Step 2: Log in to LinkedIn
username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password")

# Prompt user for LinkedIn email and password
email = input("Enter your LinkedIn email: ")
password_input = input("Enter your LinkedIn password: ")

username.send_keys(email)
password.send_keys(password_input)

# Display "Signing in..." animation
loading_animation("Signing in...")
password.send_keys(Keys.RETURN)
time.sleep(3)

target_url = "https://www.linkedin.com/search/results/people/?geoUrn=%5B%2290000084%22%5D&industry=%5B%22109%22%2C%223131%22%5D&network=%5B%22F%22%2C%22S%22%5D&origin=FACETED_SEARCH&sid=ZsH"
print(f"Navigating to search page: {target_url}")
driver.get(target_url)
time.sleep(5)  # Wait for the page to load


# Function to scroll the page to ensure all elements are loaded
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

# Step 4: Function to Extract Profile Information from Current Page
def extract_profiles():
    auto_scroll()
    profiles = driver.find_elements(By.CLASS_NAME, "linked-area.flex-1.cursor-pointer")
    for profile in profiles:
        try:
            # Extract Name and Profile Link
            name_element = profile.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
            name = name_element.text.strip() if name_element else ""
            print(name)

            link_element = profile.find_element(By.TAG_NAME, "a")
            profile_link = link_element.get_attribute("href") if link_element else ""
            print(profile_link)

            # Extract Title/Designation
            title_element = profile.find_element(By.CLASS_NAME, "oTADryLUgiMDrgOUzFvMrgfyhayVgwHRk")
            title = title_element.text.strip() if title_element else ""

            # Extract Location
            location_element = profile.find_element(By.CLASS_NAME, "fNudNcxdGdiIrrwNWmOrvRbyvWHgpRzME")
            location = location_element.text.strip() if location_element else ""

            # Append to data list
            extracted_data.append([name, profile_link, title, location])
        except Exception as e:
            print("Error extracting profile:", e)
            continue

# Step 5: Extract Data from Multiple Pages
extracted_data = []
current_page = 1

while current_page <= max_pages:
    print(f"Scraping page {current_page}...")
    extract_profiles()
    
    # Check if there is a next page button
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Next')]"))
        )
        next_button.click()
        time.sleep(5)  # Wait for the next page to load
        current_page += 1
    except Exception:
        print("No more pages or pagination button not found.")
        break

# Step 6: Save Data to CSV
df = pd.DataFrame(extracted_data, columns=["Name", "Profile Link", "Title", "Location"])
df.to_csv("linkedin_profiles.csv", index=False)

print(f"Data saved to 'linkedin_profiles.csv'. Scraped {len(extracted_data)} profiles from {current_page} pages.")

# Step 7: Close the Browser
driver.quit()
