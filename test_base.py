# """
# test_base.py — Enhanced shared base class with healthcare-specific helpers
# Import this in every test file.
# """

# import unittest
# import time
# import random
# import string
# import os
# from functools import wraps
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # ─── Global Config ────────────────────────────────────────────
# BASE_URL = os.getenv('TEST_BASE_URL', 'https://smarthealthcaresystems.onrender.com')
# TEST_USERNAME = os.getenv('TEST_USERNAME', 'selenium_tester')
# TEST_PASSWORD = os.getenv('TEST_PASSWORD', 'TestPass@123')
# TEST_EMAIL = os.getenv('TEST_EMAIL', 'selenium_tester@example.com')
# TEST_FNAME = os.getenv('TEST_FNAME', 'Selenium')
# TEST_ADDRESS = os.getenv('TEST_ADDRESS', '123 Test Road, Dhaka')
# TEST_MOBILE = os.getenv('TEST_MOBILE', '01700000001')

# # Test configuration
# TEST_TIMEOUT = int(os.getenv('TEST_TIMEOUT', '20'))
# SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'True').lower() == 'true'
# HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
# # ──────────────────────────────────────────────────────────────


# def retry_on_failure(max_retries=3, delay=2):
#     """Decorator to retry flaky tests"""
#     def decorator(func):
#         @wraps(func)
#         def wrapper(self, *args, **kwargs):
#             last_exception = None
#             for attempt in range(max_retries):
#                 try:
#                     return func(self, *args, **kwargs)
#                 except Exception as e:
#                     last_exception = e
#                     if attempt < max_retries - 1:
#                         print(f"  ⚠️  Attempt {attempt + 1} failed, retrying in {delay}s...")
#                         time.sleep(delay)
#                     else:
#                         print(f"  ❌ All {max_retries} attempts failed")
#             if last_exception:
#                 raise last_exception
#         return wrapper
#     return decorator


# def chrome_options():
#     """Configure Chrome options for testing"""
#     opts = webdriver.ChromeOptions()
#     opts.add_argument("--no-sandbox")
#     opts.add_argument("--disable-dev-shm-usage")
#     opts.add_argument("--disable-gpu")
#     opts.add_argument("--window-size=1920,1080")
    
#     if HEADLESS_MODE:
#         opts.add_argument("--headless")
    
#     # Disable notifications and popups
#     opts.add_experimental_option("prefs", {
#         "profile.default_content_setting_values.notifications": 2,
#         "profile.default_content_settings.popups": 0,
#     })
    
#     return opts


# def send_keys_safe(driver, by, value, text):
#     """Safely send keys to an element with explicit wait"""
#     el = WebDriverWait(driver, TEST_TIMEOUT).until(
#         EC.presence_of_element_located((by, value))
#     )
#     el.clear()
#     el.send_keys(text)
#     time.sleep(0.3)


# def click_submit(driver):
#     """Click submit button using JavaScript"""
#     btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#     driver.execute_script("arguments[0].click();", btn)


# def fill_registration(driver, username, email, password,
#                        fname, address, mobile):
#     """Fill registration form with provided data"""
#     fields = {
#         "u_name": username,
#         "u_fname": fname,
#         "u_email": email,
#         "u_password": password,
#         "u_address": address,
#         "u_mobile": mobile,
#     }
#     for name, val in fields.items():
#         try:
#             el = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.NAME, name))
#             )
#             el.clear()
#             el.send_keys(val)
#             time.sleep(0.4)
#         except Exception as e:
#             print(f"Warning: Could not fill field {name}: {e}")
#             pass
    
#     # Select Male gender
#     try:
#         radio = driver.find_element(By.CSS_SELECTOR, "input[value='Male']")
#         driver.execute_script("arguments[0].click();", radio)
#     except Exception:
#         pass
    
#     click_submit(driver)


# def ensure_user_registered():
#     """Register TEST_USERNAME once. Safe to call multiple times."""
#     driver = webdriver.Chrome(service=Service(), options=chrome_options())
#     try:
#         print("  🔄 Ensuring test user is registered...")
#         driver.get(f"{BASE_URL}/accounts/register/")
#         time.sleep(6)
#         fill_registration(driver, TEST_USERNAME, TEST_EMAIL,
#                           TEST_PASSWORD, TEST_FNAME, TEST_ADDRESS, TEST_MOBILE)
#         time.sleep(6)
#         print("  ✅ Test user registration complete")
#     except Exception as e:
#         print(f"  ℹ️  Note: {e}")
#     finally:
#         driver.quit()


# # ─── Base Test Class ──────────────────────────────────────────

# class HealthcareTestBase(unittest.TestCase):
#     """Enhanced base test class with healthcare-specific helpers"""

#     @classmethod
#     def setUpClass(cls):
#         """Called once before all tests in the class"""
#         ensure_user_registered()

#     def setUp(self):
#         """Called before each test method"""
#         self.driver = webdriver.Chrome(service=Service(), options=chrome_options())
#         self.driver.maximize_window()
#         self.wait = WebDriverWait(self.driver, TEST_TIMEOUT)
#         self.test_start_time = time.time()

#     def tearDown(self):
#         """Called after each test method"""
#         time.sleep(0.5)
        
#         # Capture screenshot on failure if enabled
#         if SCREENSHOT_ON_FAILURE and sys.exc_info()[0] is not None:
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             test_name = self._testMethodName
#             screenshot_path = f"screenshots/{test_name}_{timestamp}.png"
#             os.makedirs("screenshots", exist_ok=True)
#             try:
#                 self.driver.save_screenshot(screenshot_path)
#                 print(f"  📸 Screenshot saved: {screenshot_path}")
#             except Exception as e:
#                 print(f"  ⚠️  Could not save screenshot: {e}")
        
#         self.driver.quit()
        
#         # Print test duration
#         duration = time.time() - self.test_start_time
#         print(f"  ⏱️  Test duration: {duration:.2f}s")

#     # ── Utility Methods ──────────────────────────────────────

#     def login(self, username=TEST_USERNAME, password=TEST_PASSWORD):
#         """Login with provided credentials"""
#         self.driver.get(f"{BASE_URL}/accounts/login/")
#         time.sleep(5)
#         send_keys_safe(self.driver, By.NAME, "u_name", username)
#         send_keys_safe(self.driver, By.NAME, "u_password", password)
#         click_submit(self.driver)
#         time.sleep(6)

#     def logout(self):
#         """Logout from the system"""
#         try:
#             links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']")
#             if links:
#                 links[0].click()
#                 time.sleep(4)
#         except Exception as e:
#             print(f"  ⚠️  Logout error: {e}")

#     def wait_for(self, by, value, timeout=None):
#         """Wait for element with custom timeout"""
#         if timeout is None:
#             timeout = TEST_TIMEOUT
#         try:
#             return WebDriverWait(self.driver, timeout).until(
#                 EC.presence_of_element_located((by, value))
#             )
#         except TimeoutException:
#             return None

#     def wait_for_clickable(self, by, value, timeout=None):
#         """Wait for element to be clickable"""
#         if timeout is None:
#             timeout = TEST_TIMEOUT
#         try:
#             return WebDriverWait(self.driver, timeout).until(
#                 EC.element_to_be_clickable((by, value))
#             )
#         except TimeoutException:
#             return None

#     def body_text(self):
#         """Get body text content"""
#         try:
#             return self.driver.find_element(By.TAG_NAME, "body").text
#         except Exception:
#             return ""

#     def page_source(self):
#         """Get page source"""
#         try:
#             return self.driver.page_source
#         except Exception:
#             return ""

#     def assertPageLoaded(self, msg="Page did not load"):
#         """Assert that page has loaded with content"""
#         self.assertNotEqual(self.body_text().strip(), "", msg)

#     def assertNotOnLoginPage(self, msg="Still on login page"):
#         """Assert that user is not on login page"""
#         self.assertNotIn("/accounts/login/", self.driver.current_url, msg)

#     def assertOnPage(self, page_identifier, msg="Not on expected page"):
#         """Assert that we're on the expected page"""
#         self.assertIn(page_identifier, self.driver.current_url, msg)

#     def is_404(self):
#         """Check if current page is a 404"""
#         title = self.driver.title.lower()
#         text = self.body_text().lower()
#         return "404" in title or "page not found" in text or "not found" in text

#     def find_working_path(self, candidates):
#         """Return first path that isn't a 404"""
#         for path in candidates:
#             self.driver.get(f"{BASE_URL}{path}")
#             time.sleep(4)
#             if not self.is_404():
#                 return path
#         return None

#     def get_page_load_time(self):
#         """Get page load time in seconds"""
#         try:
#             navigation_start = self.driver.execute_script("return window.performance.timing.navigationStart")
#             load_complete = self.driver.execute_script("return window.performance.timing.loadEventEnd")
#             return (load_complete - navigation_start) / 1000
#         except Exception:
#             return 0

#     def element_count(self, by, value):
#         """Count elements matching selector"""
#         try:
#             return len(self.driver.find_elements(by, value))
#         except Exception:
#             return 0

#     # ── Healthcare-Specific Helpers ──────────────────────

#     def get_user_role(self):
#         """Get current user's role (Doctor, User, or None)"""
#         try:
#             # Check for doctor-specific elements
#             self.driver.find_element(By.LINK_TEXT, "Doctor Dashboard")
#             return "Doctor"
#         except NoSuchElementException:
#             try:
#                 # Check for patient-specific elements
#                 self.driver.find_element(By.LINK_TEXT, "My Profile")
#                 return "User"
#             except NoSuchElementException:
#                 return None

#     def check_data_privacy(self, sensitive_keywords):
#         """Check that sensitive data is not exposed in page"""
#         body = self.body_text()
#         exposed_keywords = []
#         for keyword in sensitive_keywords:
#             if keyword.lower() in body.lower():
#                 exposed_keywords.append(keyword)
#         return exposed_keywords

#     def verify_page_has_required_elements(self, required_elements):
#         """Verify page has all required elements"""
#         missing = []
#         for by, value in required_elements:
#             try:
#                 self.wait_for(by, value, timeout=5)
#             except TimeoutException:
#                 missing.append((by, value))
#         return len(missing) == 0, missing

#     def test_response_time(self, timeout_seconds=5):
#         """Test if page loaded within timeout"""
#         load_time = self.get_page_load_time()
#         return load_time < timeout_seconds, load_time


# # Import sys for exception checking
# import sys
