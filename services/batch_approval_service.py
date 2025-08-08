import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

USERNAME = os.getenv("ESC_USERNAME") or "APSSDCESC"
PASSWORD = os.getenv("ESC_PASSWORD") or "Durgamatha@2025"

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def approve_batches():
    driver = create_driver()
    wait = WebDriverWait(driver, 20)
    approved_count = 0

    try:
        driver.get("https://naipunyam.ap.gov.in")

        # Step 1: Click Login
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Login"))).click()

        # Step 2: Login with credentials
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(USERNAME)
        wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(PASSWORD)
        wait.until(EC.element_to_be_clickable((By.NAME, "login"))).click()

        # Step 3: Navigate to Free Batches
        driver.get("https://naipunyam.ap.gov.in/admin/admins/free-batches")
        time.sleep(3)

        # Step 4: Get all visible "batch cards"
        batch_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "card")))
        print(f"📝 Found {len(batch_cards)} batch cards to process.")

        for i in range(len(batch_cards)):
            # Re-fetch batch cards after each loop due to DOM reload
            batch_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "card")))
            card = batch_cards[i]

            try:
                # Scroll into view and click the card
                driver.execute_script("arguments[0].scrollIntoView(true);", card)
                card.click()

                # Wait for the Approve button
                approve_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Approve')]")))
                approve_btn.click()
                approved_count += 1

                print(f"✅ Batch {i+1} approved.")

                # Wait for page to reload and go back
                time.sleep(3)
                driver.get("https://naipunyam.ap.gov.in/admin/admins/free-batches")
                time.sleep(3)

            except Exception as e:
                print(f"⚠️ Failed to approve batch {i+1}: {e}")
                driver.get("https://naipunyam.ap.gov.in/admin/admins/free-batches")
                time.sleep(3)
                continue

        return f"✅ ESC batch approval completed. Total approved: {approved_count}"

    except Exception as e:
        screenshot = os.path.join(os.getcwd(), "error_screenshot.png")
        driver.save_screenshot(screenshot)
        error_msg = f"❌ Error approving ESC batches: {e}. Screenshot saved at {screenshot}"
        print(error_msg)
        return error_msg
    finally:
        driver.quit()
