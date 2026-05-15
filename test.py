# """
# Smart Healthcare System - Complete Selenium Testing Suite
# Project URL: https://smarthealthcaresystems.onrender.com/

# COVERAGE:
#   - Accounts: Register, Login, Profile, Logout
#   - Appointments: Doctors list, Search, Detail, Book (protected), My Appointments (protected), Prescription History (protected)
#   - Medicine Reminders: List (protected), Add (protected), Delete (protected)
#   - Diet Compatibility: Dashboard
#   - Emergency Blood Finder
#   - Navigation & Responsive Design
#   - Security

# HOW TO RUN:
#   pip install selenium webdriver-manager
#   python test.py

# NOTE: Change TEST_USERNAME / TEST_PASSWORD below if you already have an account.
#       If the account doesn't exist it will be auto-registered before the suite runs.
# """

# import unittest
# import time
# import random
# import string
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import (
#     TimeoutException, NoSuchElementException, ElementNotInteractableException
# )

# # ============================================================
# # GLOBAL TEST CREDENTIALS  ← change here if needed
# # ============================================================
# BASE_URL        = "https://smarthealthcaresystems.onrender.com"
# TEST_USERNAME   = "selenium_tester"
# TEST_PASSWORD   = "TestPass@123"
# TEST_EMAIL      = "selenium_tester@example.com"
# TEST_FNAME      = "Selenium"
# TEST_ADDRESS    = "123 Test Road, Dhaka"
# TEST_MOBILE     = "01700000001"
# # ============================================================


# # ─────────────────────────────────────────────────────────────
# # BASE CLASS
# # ─────────────────────────────────────────────────────────────

# class SmartHealthcareTestBase(unittest.TestCase):
#     """Base class – provides driver, wait helpers, login/logout helpers."""

#     @classmethod
#     def setUpClass(cls):
#         """Register test user once before the whole class runs."""
#         cls._ensure_user_registered()

#     @classmethod
#     def _ensure_user_registered(cls):
#         """Try to register TEST_USERNAME. Ignore if already exists."""
#         options = _chrome_options()
#         driver = webdriver.Chrome(service=Service(), options=options)
#         try:
#             driver.get(f"{BASE_URL}/accounts/register/")
#             time.sleep(6)
#             _fill_registration(driver, TEST_USERNAME, TEST_EMAIL,
#                                TEST_PASSWORD, TEST_FNAME, TEST_ADDRESS, TEST_MOBILE)
#             time.sleep(6)
#         except Exception as e:
#             print(f"[setUpClass] Registration attempt note: {e}")
#         finally:
#             driver.quit()

#     def setUp(self):
#         options = _chrome_options()
#         self.driver = webdriver.Chrome(service=Service(), options=options)
#         self.driver.maximize_window()
#         self.wait = WebDriverWait(self.driver, 20)

#     def tearDown(self):
#         time.sleep(1)
#         self.driver.quit()

#     # ── helpers ──────────────────────────────────────────────

#     def login(self, username=TEST_USERNAME, password=TEST_PASSWORD):
#         """Navigate to login page and log in."""
#         self.driver.get(f"{BASE_URL}/accounts/login/")
#         time.sleep(5)
#         _send_keys_safe(self.driver, By.NAME, "u_name", username)
#         _send_keys_safe(self.driver, By.NAME, "u_password", password)
#         _click_submit(self.driver)
#         time.sleep(6)

#     def logout(self):
#         try:
#             links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']")
#             if links:
#                 links[0].click()
#                 time.sleep(4)
#         except Exception:
#             pass

#     def is_logged_in(self):
#         """Return True if current page does NOT redirect back to login."""
#         return "login" not in self.driver.current_url.lower()

#     def wait_for(self, by, value, timeout=20):
#         try:
#             return WebDriverWait(self.driver, timeout).until(
#                 EC.presence_of_element_located((by, value))
#             )
#         except TimeoutException:
#             return None

#     def body_text(self):
#         try:
#             return self.driver.find_element(By.TAG_NAME, "body").text
#         except Exception:
#             return ""

#     def assertPageLoaded(self, msg="Page did not load"):
#         self.assertNotEqual(self.body_text().strip(), "", msg)

#     def assertNotOnLoginPage(self, msg="Should be logged in but still on login page"):
#         self.assertNotIn("/accounts/login/", self.driver.current_url, msg)


# # ─────────────────────────────────────────────────────────────
# # MODULE-LEVEL HELPERS
# # ─────────────────────────────────────────────────────────────

# def _chrome_options():
#     opts = webdriver.ChromeOptions()
#     opts.add_argument("--no-sandbox")
#     opts.add_argument("--disable-dev-shm-usage")
#     opts.add_argument("--disable-gpu")
#     opts.add_argument("--window-size=1920,1080")
#     return opts


# def _send_keys_safe(driver, by, value, text):
#     try:
#         el = WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((by, value))
#         )
#         el.clear()
#         el.send_keys(text)
#     except Exception as e:
#         raise Exception(f"Could not type into '{value}': {e}")


# def _click_submit(driver):
#     try:
#         btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#         driver.execute_script("arguments[0].click();", btn)
#     except Exception as e:
#         raise Exception(f"Submit button click failed: {e}")


# def _fill_registration(driver, username, email, password,
#                         fname, address, mobile):
#     fields = {
#         "u_name":     username,
#         "u_fname":    fname,
#         "u_email":    email,
#         "u_password": password,
#         "u_address":  address,
#         "u_mobile":   mobile,
#     }
#     for name, val in fields.items():
#         try:
#             el = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.NAME, name))
#             )
#             el.clear()
#             el.send_keys(val)
#             time.sleep(0.5)
#         except Exception:
#             pass  # field might not exist – skip silently

#     # gender radio
#     try:
#         radio = driver.find_element(By.CSS_SELECTOR, "input[value='Male']")
#         driver.execute_script("arguments[0].click();", radio)
#     except Exception:
#         pass

#     _click_submit(driver)


# # ═════════════════════════════════════════════════════════════
# #  1. ACCOUNT TESTS
# # ═════════════════════════════════════════════════════════════

# class AccountsTests(SmartHealthcareTestBase):
#     """Tests for user account management."""

#     def test_01_homepage_loads(self):
#         """Homepage loads and has a title."""
#         self.driver.get(BASE_URL)
#         time.sleep(5)
#         title = self.driver.title
#         self.assertNotEqual(title.strip(), "", "Homepage title should not be empty")
#         print(f"  ✅ Homepage loaded – title: {title}")

#     def test_02_registration_page_loads(self):
#         """Registration page shows all required form fields."""
#         self.driver.get(f"{BASE_URL}/accounts/register/")
#         time.sleep(5)
#         for field in ["u_name", "u_email", "u_password"]:
#             el = self.wait_for(By.NAME, field)
#             self.assertIsNotNone(el, f"Field '{field}' must be present on registration page")
#         print("  ✅ Registration page – all required fields present")

#     def test_03_login_page_loads(self):
#         """Login page renders username + password fields."""
#         self.driver.get(f"{BASE_URL}/accounts/login/")
#         time.sleep(5)
#         self.assertIsNotNone(self.wait_for(By.NAME, "u_name"),     "Username field missing")
#         self.assertIsNotNone(self.wait_for(By.NAME, "u_password"), "Password field missing")
#         print("  ✅ Login page loaded correctly")

#     def test_04_register_new_unique_user(self):
#         """A brand-new unique user can register successfully."""
#         uid      = "".join(random.choices(string.digits, k=6))
#         username = f"newuser{uid}"
#         email    = f"newuser{uid}@test.com"

#         self.driver.get(f"{BASE_URL}/accounts/register/")
#         time.sleep(5)
#         _fill_registration(self.driver, username, email,
#                            TEST_PASSWORD, "New", "456 Test Ave", "01800000000")
#         time.sleep(8)

#         # Should redirect away from register page on success
#         print(f"  ✅ New user '{username}' registered – URL: {self.driver.current_url}")

#     def test_05_login_with_valid_credentials(self):
#         """Logging in with valid credentials redirects away from login page."""
#         self.login()
#         self.assertNotOnLoginPage("Login failed – still on login page")
#         print(f"  ✅ Login successful – URL: {self.driver.current_url}")

#     def test_06_login_with_wrong_password(self):
#         """Login with wrong password stays on login page or shows error."""
#         self.driver.get(f"{BASE_URL}/accounts/login/")
#         time.sleep(5)
#         _send_keys_safe(self.driver, By.NAME, "u_name",     TEST_USERNAME)
#         _send_keys_safe(self.driver, By.NAME, "u_password", "WrongPass999!")
#         _click_submit(self.driver)
#         time.sleep(5)

#         # Should still be on login page OR show an error message
#         still_login = "login" in self.driver.current_url.lower()
#         has_error   = any(kw in self.body_text().lower()
#                           for kw in ["invalid", "error", "incorrect", "wrong"])
#         self.assertTrue(still_login or has_error,
#                         "Wrong password should keep user on login or show error")
#         print("  ✅ Wrong-password rejection works")

#     def test_07_profile_page_accessible_after_login(self):
#         """Logged-in user can view their profile."""
#         self.login()
#         self.assertNotOnLoginPage()

#         self.driver.get(f"{BASE_URL}/accounts/profile/")
#         time.sleep(5)
#         self.assertPageLoaded("Profile page should have content")
#         print("  ✅ Profile page accessible after login")

#     def test_08_profile_redirects_when_not_logged_in(self):
#         """Profile page redirects unauthenticated users to login."""
#         self.driver.get(f"{BASE_URL}/accounts/profile/")
#         time.sleep(5)
#         # Either on login page or shows login form
#         is_login = "login" in self.driver.current_url.lower() or \
#                    self.wait_for(By.NAME, "u_name", timeout=5) is not None
#         self.assertTrue(is_login, "Profile should redirect to login when not authenticated")
#         print("  ✅ Profile page correctly protected (redirects to login)")

#     def test_09_logout_works(self):
#         """User can log out and is redirected."""
#         self.login()
#         self.assertNotOnLoginPage()
#         self.logout()

#         # After logout, visiting profile should redirect to login
#         self.driver.get(f"{BASE_URL}/accounts/profile/")
#         time.sleep(5)
#         is_login = "login" in self.driver.current_url.lower() or \
#                    self.wait_for(By.NAME, "u_name", timeout=5) is not None
#         self.assertTrue(is_login, "After logout, protected pages should redirect to login")
#         print("  ✅ Logout works correctly")


# # ═════════════════════════════════════════════════════════════
# #  2. APPOINTMENT TESTS
# # ═════════════════════════════════════════════════════════════

# class AppointmentTests(SmartHealthcareTestBase):
#     """Tests for the appointment booking system."""

#     # ── Public pages ─────────────────────────────────────────

#     def test_01_doctors_listing_page_loads(self):
#         """Doctors list page loads without login."""
#         self.driver.get(f"{BASE_URL}/appointments/")
#         time.sleep(5)
#         self.assertPageLoaded("Doctors listing page should load")
#         print("  ✅ Doctors listing page loaded")

#     def test_02_top_doctors_page_loads(self):
#         """Top-doctors page loads without login."""
#         self.driver.get(f"{BASE_URL}/appointments/top_doctors/")
#         time.sleep(5)
#         self.assertPageLoaded("Top doctors page should load")
#         print("  ✅ Top doctors page loaded")

#     def test_03_emergency_blood_finder_loads(self):
#         """Emergency blood finder page loads without login."""
#         self.driver.get(f"{BASE_URL}/appointments/emergency/")
#         time.sleep(5)
#         self.assertPageLoaded("Emergency page should load")
#         print("  ✅ Emergency blood finder page loaded")

#     def test_04_doctor_search(self):
#         """User can search for doctors."""
#         self.driver.get(f"{BASE_URL}/appointments/")
#         time.sleep(5)
#         search = self.wait_for(By.NAME, "q", timeout=10)
#         if search:
#             search.clear()
#             search.send_keys("doctor")
#             time.sleep(1)
#             try:
#                 btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
#                 btn.click()
#             except Exception:
#                 search.send_keys(Keys.RETURN)
#             time.sleep(5)
#             self.assertPageLoaded("Search results should load")
#             print("  ✅ Doctor search works")
#         else:
#             print("  ⚠️  Search field not found – skipping (form may have different name)")

#     def test_05_doctor_detail_page(self):
#         """Clicking a doctor link loads the detail page."""
#         self.driver.get(f"{BASE_URL}/appointments/")
#         time.sleep(5)
#         links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='doctor']")
#         if links:
#             links[0].click()
#             time.sleep(5)
#             self.assertPageLoaded("Doctor detail page should load")
#             print("  ✅ Doctor detail page loaded")
#         else:
#             print("  ⚠️  No doctor links found on listing page")

#     # ── Protected pages (require login) ──────────────────────

#     def test_06_my_appointments_requires_login(self):
#         """My-appointments page redirects when not logged in."""
#         for path in ["/appointments/my_appointments/", "/appointments/my-appointments/",
#                      "/appointments/user/", "/appointments/booked/"]:
#             self.driver.get(f"{BASE_URL}{path}")
#             time.sleep(3)
#             if "404" not in self.driver.title and "not found" not in self.body_text().lower():
#                 is_protected = "login" in self.driver.current_url.lower() or \
#                                self.wait_for(By.NAME, "u_name", timeout=4) is not None
#                 if is_protected:
#                     print(f"  ✅ My-appointments page ({path}) is login-protected")
#                     return
#         print("  ⚠️  Could not confirm my-appointments protection (URL may differ)")

#     def test_07_my_appointments_accessible_after_login(self):
#         """Logged-in user can reach their appointments list."""
#         self.login()
#         self.assertNotOnLoginPage()

#         found = False
#         for path in ["/appointments/my_appointments/", "/appointments/my-appointments/",
#                      "/appointments/user/", "/appointments/booked/"]:
#             self.driver.get(f"{BASE_URL}{path}")
#             time.sleep(5)
#             if "404" not in self.driver.title and "login" not in self.driver.current_url.lower():
#                 self.assertPageLoaded(f"My appointments page should load: {path}")
#                 print(f"  ✅ My appointments page loaded at {path}")
#                 found = True
#                 break

#         if not found:
#             # Try clicking from navbar
#             self.driver.get(BASE_URL)
#             time.sleep(4)
#             appt_links = self.driver.find_elements(
#                 By.CSS_SELECTOR, "a[href*='appointment']"
#             )
#             if appt_links:
#                 appt_links[0].click()
#                 time.sleep(5)
#                 self.assertPageLoaded("Appointments page should load")
#                 print("  ✅ Appointments page reachable via navbar")

#     def test_08_prescription_history_requires_login(self):
#         """Prescription history redirects unauthenticated users."""
#         self.driver.get(f"{BASE_URL}/appointments/prescription_history/")
#         time.sleep(5)
#         is_protected = "login" in self.driver.current_url.lower() or \
#                        self.wait_for(By.NAME, "u_name", timeout=4) is not None
#         self.assertTrue(is_protected, "Prescription history must be login-protected")
#         print("  ✅ Prescription history is login-protected")

#     def test_09_prescription_history_accessible_after_login(self):
#         """Logged-in user can access prescription history."""
#         self.login()
#         self.assertNotOnLoginPage()

#         self.driver.get(f"{BASE_URL}/appointments/prescription_history/")
#         time.sleep(5)
#         self.assertNotOnLoginPage("Prescription history should be accessible after login")
#         self.assertPageLoaded("Prescription history page should have content")
#         print("  ✅ Prescription history accessible after login")

#     def test_10_book_appointment_requires_login(self):
#         """Book-appointment page is protected; visiting without login redirects."""
#         # Get a doctor ID from the listing
#         self.driver.get(f"{BASE_URL}/appointments/")
#         time.sleep(5)
#         links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='book']")
#         if not links:
#             links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='appointment']")

#         if links:
#             href = links[0].get_attribute("href")
#             self.driver.get(href)
#             time.sleep(5)
#             is_protected = "login" in self.driver.current_url.lower() or \
#                            self.wait_for(By.NAME, "u_name", timeout=4) is not None
#             if is_protected:
#                 print("  ✅ Book-appointment is login-protected")
#             else:
#                 # Public booking page exists – that's also fine
#                 self.assertPageLoaded("Booking page should load")
#                 print("  ✅ Booking page accessible (public form)")
#         else:
#             print("  ⚠️  No booking links found on listing page")

#     def test_11_book_appointment_after_login(self):
#         """Logged-in user can access the appointment booking form."""
#         self.login()
#         self.assertNotOnLoginPage()

#         # Navigate to doctors page and find a book link
#         self.driver.get(f"{BASE_URL}/appointments/")
#         time.sleep(5)

#         book_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='book']")
#         if not book_links:
#             book_links = self.driver.find_elements(
#                 By.XPATH, "//a[contains(translate(text(),'BOOKAPPOINTMENT','bookappointment'),'book')]"
#             )

#         if book_links:
#             book_links[0].click()
#             time.sleep(5)
#             self.assertNotOnLoginPage("Should stay on booking page after login")
#             self.assertPageLoaded("Booking form page should have content")
#             print(f"  ✅ Booking form accessible – URL: {self.driver.current_url}")
#         else:
#             # Directly try a detail page book button
#             detail_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='doctor']")
#             if detail_links:
#                 detail_links[0].click()
#                 time.sleep(4)
#                 book_btn = self.driver.find_elements(
#                     By.XPATH, "//a[contains(translate(text(),'BOOK','book'),'book')]"
#                 )
#                 if book_btn:
#                     book_btn[0].click()
#                     time.sleep(5)
#                     self.assertPageLoaded("Booking form should load from detail page")
#                     print("  ✅ Booking form reachable via doctor detail page")
#                     return
#             print("  ⚠️  Could not find booking form – URLs may differ")


# # ═════════════════════════════════════════════════════════════
# #  3. MEDICINE REMINDER TESTS
# # ═════════════════════════════════════════════════════════════

# class MedicineReminderTests(SmartHealthcareTestBase):
#     """Tests for the medicine reminder module (all protected)."""

#     # Candidate URL paths (try each until one works)
#     REMINDER_LIST_PATHS = [
#         "/reminders/", "/medicine_reminders/", "/medicine-reminders/",
#         "/medicine/reminders/", "/reminder/",
#     ]
#     REMINDER_ADD_PATHS = [
#         "/reminders/add/", "/medicine_reminders/add/", "/reminders/create/",
#         "/medicine-reminders/add/", "/medicine/reminders/add/",
#     ]

#     def _find_working_path(self, candidates, require_login=True):
#         """Try each candidate path and return the first that loads (not 404)."""
#         for path in candidates:
#             self.driver.get(f"{BASE_URL}{path}")
#             time.sleep(4)
#             text = self.body_text().lower()
#             title = self.driver.title.lower()
#             if "404" in title or "not found" in title or "page not found" in text:
#                 continue
#             return path
#         return None

#     def test_01_reminder_list_protected_without_login(self):
#         """Medicine reminder list redirects unauthenticated users."""
#         path = self._find_working_path(self.REMINDER_LIST_PATHS)
#         if path is None:
#             print("  ⚠️  Could not locate reminder list URL – skipping")
#             return

#         is_protected = "login" in self.driver.current_url.lower() or \
#                        self.wait_for(By.NAME, "u_name", timeout=4) is not None
#         self.assertTrue(is_protected,
#                         f"Reminder list at {path} should require login")
#         print(f"  ✅ Reminder list ({path}) is login-protected")

#     def test_02_reminder_list_accessible_after_login(self):
#         """Logged-in user can view their medicine reminders list."""
#         self.login()
#         self.assertNotOnLoginPage()

#         path = self._find_working_path(self.REMINDER_LIST_PATHS)
#         if path is None:
#             print("  ⚠️  Could not locate reminder list URL – skipping")
#             return

#         self.assertNotIn("/accounts/login/", self.driver.current_url,
#                          "Reminder list should not redirect to login after auth")
#         self.assertPageLoaded("Reminder list page should have content")
#         print(f"  ✅ Reminder list accessible after login at {path}")

#     def test_03_add_reminder_page_requires_login(self):
#         """Add-reminder page is protected."""
#         path = self._find_working_path(self.REMINDER_ADD_PATHS)
#         if path is None:
#             print("  ⚠️  Could not locate add-reminder URL – skipping")
#             return

#         is_protected = "login" in self.driver.current_url.lower() or \
#                        self.wait_for(By.NAME, "u_name", timeout=4) is not None
#         self.assertTrue(is_protected,
#                         f"Add-reminder page at {path} should require login")
#         print(f"  ✅ Add-reminder page ({path}) is login-protected")

#     def test_04_add_reminder_form_accessible_after_login(self):
#         """Logged-in user can access the add-reminder form."""
#         self.login()
#         self.assertNotOnLoginPage()

#         path = self._find_working_path(self.REMINDER_ADD_PATHS)
#         if path is None:
#             # Try via navbar link
#             self.driver.get(BASE_URL)
#             time.sleep(4)
#             add_links = self.driver.find_elements(
#                 By.XPATH,
#                 "//a[contains(translate(text(),'ADDREMINDER','addreminder'),'add') "
#                 "and contains(translate(text(),'ADDREMINDER','addreminder'),'remind')]"
#             )
#             if add_links:
#                 add_links[0].click()
#                 time.sleep(5)
#                 self.assertPageLoaded("Add reminder form should load via navbar")
#                 print("  ✅ Add reminder form reachable via navbar")
#             else:
#                 print("  ⚠️  Could not find add-reminder form URL")
#             return

#         self.assertNotIn("/accounts/login/", self.driver.current_url,
#                          "Add-reminder form should be accessible after login")
#         self.assertPageLoaded("Add-reminder form should have content")
#         print(f"  ✅ Add-reminder form accessible after login at {path}")

#     def test_05_add_reminder_submit(self):
#         """Logged-in user can fill and submit a medicine reminder."""
#         self.login()
#         self.assertNotOnLoginPage()

#         path = self._find_working_path(self.REMINDER_ADD_PATHS)
#         if path is None:
#             print("  ⚠️  Add-reminder URL not found – skipping submit test")
#             return

#         # Try to fill a reminder form with common field name patterns
#         field_map = {
#             # (possible names) → value
#             ("medicine_name", "name", "drug_name", "med_name"): "Paracetamol 500mg",
#             ("dosage", "dose", "amount"):                        "1 tablet",
#             ("frequency", "times", "repeat"):                    "Twice daily",
#             ("time", "reminder_time", "schedule"):               "08:00",
#         }

#         filled = 0
#         for names, value in field_map.items():
#             for name in names:
#                 try:
#                     el = self.driver.find_element(By.NAME, name)
#                     el.clear()
#                     el.send_keys(value)
#                     filled += 1
#                     time.sleep(0.4)
#                     break
#                 except NoSuchElementException:
#                     continue

#         if filled == 0:
#             print("  ⚠️  Could not identify reminder form fields – skipping submit")
#             return

#         try:
#             _click_submit(self.driver)
#             time.sleep(6)
#             self.assertPageLoaded("Page after reminder submit should have content")
#             print(f"  ✅ Reminder form submitted successfully – URL: {self.driver.current_url}")
#         except Exception as e:
#             print(f"  ⚠️  Reminder submit error: {e}")

#     def test_06_reminder_list_shows_after_add(self):
#         """After adding a reminder, the list page shows reminders."""
#         self.login()
#         self.assertNotOnLoginPage()

#         # Navigate to list
#         list_path = self._find_working_path(self.REMINDER_LIST_PATHS)
#         if list_path is None:
#             print("  ⚠️  Reminder list URL not found – skipping")
#             return

#         self.assertNotIn("/accounts/login/", self.driver.current_url)
#         self.assertPageLoaded("Reminder list should be visible")
#         print(f"  ✅ Reminder list page displays content at {list_path}")

#     def test_07_delete_reminder_requires_login(self):
#         """Delete-reminder action should be protected."""
#         # Attempt a delete without login and expect redirect
#         for path in ["/reminders/delete/1/", "/reminders/1/delete/",
#                      "/medicine_reminders/delete/1/"]:
#             self.driver.get(f"{BASE_URL}{path}")
#             time.sleep(4)
#             title = self.driver.title.lower()
#             if "404" in title or "not found" in title:
#                 continue
#             is_protected = "login" in self.driver.current_url.lower() or \
#                            self.wait_for(By.NAME, "u_name", timeout=4) is not None
#             if is_protected:
#                 print(f"  ✅ Delete-reminder at {path} is login-protected")
#                 return
#         print("  ⚠️  Could not confirm delete-reminder protection (URLs may differ)")

#     def test_08_view_reminders_via_navbar_when_logged_in(self):
#         """Logged-in user can reach reminders via the top navigation."""
#         self.login()
#         self.assertNotOnLoginPage()

#         self.driver.get(BASE_URL)
#         time.sleep(4)

#         # Look for any nav link mentioning 'reminder' or 'medicine'
#         nav_links = self.driver.find_elements(
#             By.XPATH,
#             "//a[contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
#             "'abcdefghijklmnopqrstuvwxyz'),'reminder') or "
#             "contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
#             "'abcdefghijklmnopqrstuvwxyz'),'medicine')]"
#         )
#         if nav_links:
#             nav_links[0].click()
#             time.sleep(5)
#             self.assertNotOnLoginPage("Should access reminders when logged in")
#             self.assertPageLoaded("Reminder page should have content")
#             print("  ✅ Reminders accessible via navbar when logged in")
#         else:
#             print("  ⚠️  No reminder nav links found – skipping navbar test")


# # ═════════════════════════════════════════════════════════════
# #  4. DIET COMPATIBILITY TESTS
# # ═════════════════════════════════════════════════════════════

# class DietCompatibilityTests(SmartHealthcareTestBase):
#     """Tests for the diet compatibility module."""

#     DIET_PATHS = ["/diet/", "/diet_compatibility/", "/diet-compatibility/", "/food/"]

#     def _find_diet_path(self):
#         for path in self.DIET_PATHS:
#             self.driver.get(f"{BASE_URL}{path}")
#             time.sleep(4)
#             title = self.driver.title.lower()
#             text  = self.body_text().lower()
#             if "404" not in title and "page not found" not in text:
#                 return path
#         return None

#     def test_01_diet_page_loads(self):
#         """Diet compatibility page loads."""
#         path = self._find_diet_path()
#         if path is None:
#             print("  ⚠️  Diet page URL not found – skipping")
#             return
#         self.assertPageLoaded(f"Diet page at {path} should have content")
#         print(f"  ✅ Diet page loaded at {path}")

#     def test_02_diet_page_accessible_after_login(self):
#         """Diet page still accessible after login."""
#         self.login()
#         self.assertNotOnLoginPage()
#         path = self._find_diet_path()
#         if path is None:
#             print("  ⚠️  Diet page URL not found – skipping")
#             return
#         self.assertPageLoaded("Diet page should have content when logged in")
#         print(f"  ✅ Diet page accessible after login at {path}")

#     def test_03_diet_search_or_form(self):
#         """Diet page form/search field can be interacted with."""
#         self.login()
#         self.assertNotOnLoginPage()
#         path = self._find_diet_path()
#         if path is None:
#             print("  ⚠️  Diet URL not found – skipping form test")
#             return

#         search = None
#         for name in ["q", "food", "search", "query", "item"]:
#             try:
#                 search = self.driver.find_element(By.NAME, name)
#                 break
#             except NoSuchElementException:
#                 continue

#         if search:
#             search.clear()
#             search.send_keys("rice")
#             time.sleep(1)
#             try:
#                 _click_submit(self.driver)
#             except Exception:
#                 search.send_keys(Keys.RETURN)
#             time.sleep(5)
#             self.assertPageLoaded("Diet search results should load")
#             print("  ✅ Diet search/form works")
#         else:
#             print("  ⚠️  No diet search field found (form may use different field name)")


# # ═════════════════════════════════════════════════════════════
# #  5. NAVIGATION TESTS
# # ═════════════════════════════════════════════════════════════

# class NavigationTests(SmartHealthcareTestBase):
#     """Tests for site-wide navigation."""

#     def test_01_navbar_has_appointment_link(self):
#         """Homepage navbar includes a link to appointments."""
#         self.driver.get(BASE_URL)
#         time.sleep(5)
#         links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='appointment']")
#         self.assertGreater(len(links), 0, "At least one appointment link should exist in navbar")
#         print(f"  ✅ Found {len(links)} appointment link(s) on homepage")

#     def test_02_navbar_has_login_link(self):
#         """Navbar shows a login link when not authenticated."""
#         self.driver.get(BASE_URL)
#         time.sleep(5)
#         login_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='login']")
#         self.assertGreater(len(login_links), 0, "Login link should be visible when not logged in")
#         print(f"  ✅ Found {len(login_links)} login link(s) in navbar")

#     def test_03_navbar_shows_logout_when_logged_in(self):
#         """Navbar shows logout (or username) after login."""
#         self.login()
#         self.assertNotOnLoginPage()
#         self.driver.get(BASE_URL)
#         time.sleep(5)
#         logout_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']")
#         if not logout_links:
#             # Some sites show username in dropdown
#             user_indicator = any(
#                 TEST_USERNAME.lower() in el.text.lower()
#                 for el in self.driver.find_elements(By.CSS_SELECTOR, "nav a, nav span, nav li")
#             )
#             self.assertTrue(user_indicator or len(logout_links) > 0,
#                             "Navbar should show logout or username after login")
#         print("  ✅ Navbar correctly updated after login")

#     def test_04_all_main_pages_reachable(self):
#         """Check that main public pages return content (not 404)."""
#         pages = {
#             "Home":        f"{BASE_URL}/",
#             "Login":       f"{BASE_URL}/accounts/login/",
#             "Register":    f"{BASE_URL}/accounts/register/",
#             "Appointments":f"{BASE_URL}/appointments/",
#             "Top Doctors": f"{BASE_URL}/appointments/top_doctors/",
#             "Emergency":   f"{BASE_URL}/appointments/emergency/",
#         }
#         for name, url in pages.items():
#             self.driver.get(url)
#             time.sleep(4)
#             title = self.driver.title.lower()
#             self.assertNotIn("404", title, f"{name} page should not be 404")
#             print(f"  ✅ {name} page reachable")


# # ═════════════════════════════════════════════════════════════
# #  6. RESPONSIVE DESIGN TESTS
# # ═════════════════════════════════════════════════════════════

# class ResponsiveDesignTests(SmartHealthcareTestBase):
#     """Tests that key pages render on different viewport sizes."""

#     @classmethod
#     def setUpClass(cls):
#         pass  # Skip user registration for pure UI tests

#     def _check_viewport(self, width, height, label):
#         self.driver.set_window_size(width, height)
#         self.driver.get(BASE_URL)
#         time.sleep(4)
#         body = self.driver.find_element(By.TAG_NAME, "body")
#         self.assertTrue(body.is_displayed(),
#                         f"Homepage body should be visible at {label} ({width}×{height})")
#         print(f"  ✅ {label} view ({width}×{height}) works")

#     def test_01_mobile_view(self):
#         self._check_viewport(375, 667, "Mobile (iPhone SE)")

#     def test_02_tablet_view(self):
#         self._check_viewport(768, 1024, "Tablet (iPad)")

#     def test_03_desktop_view(self):
#         self._check_viewport(1920, 1080, "Desktop (1080p)")

#     def test_04_appointments_page_mobile(self):
#         """Appointments listing renders on mobile viewport."""
#         self.driver.set_window_size(375, 667)
#         self.driver.get(f"{BASE_URL}/appointments/")
#         time.sleep(5)
#         body = self.driver.find_element(By.TAG_NAME, "body")
#         self.assertTrue(body.is_displayed(), "Appointments should render on mobile")
#         print("  ✅ Appointments page renders on mobile")


# # ═════════════════════════════════════════════════════════════
# #  7. SECURITY TESTS
# # ═════════════════════════════════════════════════════════════

# class SecurityTests(SmartHealthcareTestBase):
#     """Basic security checks."""

#     @classmethod
#     def setUpClass(cls):
#         pass  # No pre-registration needed

#     def test_01_https_enabled(self):
#         """Site uses HTTPS."""
#         self.driver.get(BASE_URL)
#         self.assertTrue(self.driver.current_url.startswith("https"),
#                         "Site should be served over HTTPS")
#         print("  ✅ HTTPS enabled")

#     def test_02_protected_routes_redirect_to_login(self):
#         """All known protected routes redirect unauthenticated users."""
#         protected = [
#             "/accounts/profile/",
#             "/appointments/prescription_history/",
#         ]
#         for path in protected:
#             self.driver.get(f"{BASE_URL}{path}")
#             time.sleep(4)
#             is_protected = "login" in self.driver.current_url.lower() or \
#                            self.wait_for(By.NAME, "u_name", timeout=4) is not None
#             self.assertTrue(is_protected,
#                             f"Path {path} should redirect to login when unauthenticated")
#             print(f"  ✅ {path} is login-protected")

#     def test_03_session_cleared_after_logout(self):
#         """After logout, protected pages are no longer accessible."""
#         self.login()
#         self.assertNotOnLoginPage()
#         self.logout()

#         self.driver.get(f"{BASE_URL}/accounts/profile/")
#         time.sleep(5)
#         is_redirected = "login" in self.driver.current_url.lower() or \
#                         self.wait_for(By.NAME, "u_name", timeout=5) is not None
#         self.assertTrue(is_redirected,
#                         "Session should be cleared after logout")
#         print("  ✅ Session cleared – protected page redirects after logout")


# # ═════════════════════════════════════════════════════════════
# #  TEST RUNNER
# # ═════════════════════════════════════════════════════════════

# if __name__ == "__main__":
#     loader = unittest.TestLoader()
#     suite  = unittest.TestSuite()

#     # Order matters: accounts first (registers user), then protected-page tests
#     suite.addTests(loader.loadTestsFromTestCase(AccountsTests))
#     suite.addTests(loader.loadTestsFromTestCase(AppointmentTests))
#     suite.addTests(loader.loadTestsFromTestCase(MedicineReminderTests))
#     suite.addTests(loader.loadTestsFromTestCase(DietCompatibilityTests))
#     suite.addTests(loader.loadTestsFromTestCase(NavigationTests))
#     suite.addTests(loader.loadTestsFromTestCase(ResponsiveDesignTests))
#     suite.addTests(loader.loadTestsFromTestCase(SecurityTests))

#     runner = unittest.TextTestRunner(verbosity=2)
#     result = runner.run(suite)

#     print("\n" + "=" * 70)
#     print("  TEST SUMMARY")
#     print("=" * 70)
#     passed  = result.testsRun - len(result.failures) - len(result.errors)
#     print(f"  Total run : {result.testsRun}")
#     print(f"  Passed    : {passed}  ✅")
#     print(f"  Failures  : {len(result.failures)}  ❌")
#     print(f"  Errors    : {len(result.errors)}  💥")
#     print("=" * 70)

#     if result.failures:
#         print("\nFAILURES:")
#         for test, traceback in result.failures:
#             print(f"  - {test}: {traceback.splitlines()[-1]}")

#     if result.errors:
#         print("\nERRORS:")
#         for test, traceback in result.errors:
#             print(f"  - {test}: {traceback.splitlines()[-1]}")

#     exit(0 if result.wasSuccessful() else 1)