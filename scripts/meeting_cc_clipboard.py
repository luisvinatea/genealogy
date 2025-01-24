from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configure Selenium WebDriver for Firefox
options = webdriver.FirefoxOptions()
options.profile = "/home/luisvinatea/.mozilla/firefox/h78q2mg5.default-release"  # Path to your Firefox profile
options.set_preference("media.navigator.permission.disabled", True)  # Allow mic/cam without prompts
options.set_preference("media.navigator.streams.fake", False)       # Use actual mic/cam

# Start Firefox WebDriver (GeckoDriver)
driver = webdriver.Firefox(options=options)

# Open Google Meet
google_meet_url = "https://meet.google.com/"
driver.get(google_meet_url)

# Wait for user to manually log in if needed
input("Log in to Google Meet and press Enter once ready...")

# Automatically navigate to a specific meeting
meeting_code = "gkz-ugjp-gby"
driver.get(f"https://meet.google.com/{meeting_code}")

# Simulate clicking the "Join" button
time.sleep(5)  # Adjust wait time for page to load
try:
    join_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Join now')]")
    join_button.click()
    print("Joined the meeting!")
except Exception as e:
    print("Could not join the meeting:", e)

# Keep the browser open for the duration of the meeting
input("Press Enter to exit the meeting and close the browser...")
driver.quit()
