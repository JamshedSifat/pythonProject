"""
test_base.py — Shared base class, helpers, and credentials
Import this in every test file.
"""

import unittest
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ─── Global Config ────────────────────────────────────────────
BASE_URL      = "https://smarthealthcaresystems.onrender.com"
TEST_USERNAME = "selenium_tester"
TEST_PASSWORD = "TestPass@123"
TEST_EMAIL    = "selenium_tester@example.com"
TEST_FNAME    = "Selenium"
TEST_ADDRESS  = "123 Test Road, Dhaka"
TEST_MOBILE   = "01700000001"
# ──────────────────────────────────────────────────────────────


def chrome_options():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    return opts


def send_keys_safe(driver, by, value, text):
    el = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((by, value))
    )
    el.clear()
    el.send_keys(text)


def click_submit(driver):
    btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].click();", btn)


def fill_registration(driver, username, email, password,
                       fname, address, mobile):
    fields = {
        "u_name": username, "u_fname": fname, "u_email": email,
        "u_password": password, "u_address": address, "u_mobile": mobile,
    }
    for name, val in fields.items():
        try:
            el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, name))
            )
            el.clear()
            el.send_keys(val)
            time.sleep(0.4)
        except Exception:
            pass
    try:
        radio = driver.find_element(By.CSS_SELECTOR, "input[value='Male']")
        driver.execute_script("arguments[0].click();", radio)
    except Exception:
        pass
    click_submit(driver)


def ensure_user_registered():
    """Register TEST_USERNAME once. Safe to call multiple times."""
    driver = webdriver.Chrome(service=Service(), options=chrome_options())
    try:
        driver.get(f"{BASE_URL}/accounts/register/")
        time.sleep(6)
        fill_registration(driver, TEST_USERNAME, TEST_EMAIL,
                          TEST_PASSWORD, TEST_FNAME, TEST_ADDRESS, TEST_MOBILE)
        time.sleep(6)
    except Exception as e:
        print(f"[ensure_user_registered] note: {e}")
    finally:
        driver.quit()


# ─── Base Test Class ──────────────────────────────────────────

class HealthcareTestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_user_registered()

    def setUp(self):
        self.driver = webdriver.Chrome(service=Service(), options=chrome_options())
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)

    def tearDown(self):
        time.sleep(1)
        self.driver.quit()

    # ── helpers ──────────────────────────────────────────────

    def login(self, username=TEST_USERNAME, password=TEST_PASSWORD):
        self.driver.get(f"{BASE_URL}/accounts/login/")
        time.sleep(5)
        send_keys_safe(self.driver, By.NAME, "u_name", username)
        send_keys_safe(self.driver, By.NAME, "u_password", password)
        click_submit(self.driver)
        time.sleep(6)

    def logout(self):
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']")
            if links:
                links[0].click()
                time.sleep(4)
        except Exception:
            pass

    def wait_for(self, by, value, timeout=15):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None

    def body_text(self):
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            return ""

    def assertPageLoaded(self, msg="Page did not load"):
        self.assertNotEqual(self.body_text().strip(), "", msg)

    def assertNotOnLoginPage(self, msg="Still on login page"):
        self.assertNotIn("/accounts/login/", self.driver.current_url, msg)

    def is_404(self):
        title = self.driver.title.lower()
        text  = self.body_text().lower()
        return "404" in title or "page not found" in text

    def find_working_path(self, candidates):
        """Return first path that isn't a 404."""
        for path in candidates:
            self.driver.get(f"{BASE_URL}{path}")
            time.sleep(4)
            if not self.is_404():
                return path
        return None
