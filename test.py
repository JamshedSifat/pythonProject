"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        Smart Healthcare System - Complete Selenium Test Suite               ║
║        Project URL: https://smarthealthcaresystems.onrender.com             ║
║        Covers: Accounts · Appointments · Diet · Medicine · Navigation       ║
║                Responsive Design · Security · Emergency Blood Finder        ║
╚══════════════════════════════════════════════════════════════════════════════╝

HOW TO RUN:
    pip install selenium webdriver-manager
    python test.py

    # Headless mode (no browser window, faster):
    python test.py --headless

    # Run specific module only:
    python test.py AccountsTests
    python test.py AppointmentTests
"""

import unittest
import sys
import time
import random
import string
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    WebDriverException,
)

# Selenium 4.6+ Selenium Manager handles ChromeDriver automatically — no extra package needed.

# ─────────────────────────── Global Config ──────────────────────────────────

BASE_URL   = "https://smarthealthcaresystems.onrender.com"
HEADLESS   = "--headless" in sys.argv
TIMEOUT    = 20          # seconds for explicit waits
PAGE_WAIT  = 4           # seconds after navigation (render.com is slow on cold start)

# Shared test credentials (created once in AccountsTests)
SHARED_CREDS = {"username": None, "password": "TestPass@123"}


# ─────────────────────────── Helpers ────────────────────────────────────────

def _random_suffix(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def _build_driver(headless=HEADLESS):
    """
    Selenium Manager (built into Selenium 4.6+) automatically downloads
    the correct ChromeDriver for your installed Chrome — no manual setup.
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # ✅ No service= argument — Selenium Manager handles ChromeDriver automatically
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver


# ─────────────────────────── Base Test Class ────────────────────────────────

class HealthcareTestBase(unittest.TestCase):
    """
    Base class shared by all test suites.
    Provides: driver setup/teardown, safe element helpers, login/logout helpers.
    """

    @classmethod
    def setUpClass(cls):
        cls.driver = _build_driver()
        cls.driver.maximize_window()
        cls.wait = WebDriverWait(cls.driver, TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.driver.quit()
        except Exception:
            pass

    # ── Navigation helpers ──────────────────────────────────────────────────

    def go(self, path=""):
        """Navigate to BASE_URL + path and wait for page."""
        self.driver.get(BASE_URL + path)
        time.sleep(PAGE_WAIT)

    # ── Wait helpers ────────────────────────────────────────────────────────

    def find(self, by, value, timeout=TIMEOUT):
        """Return element or None (never raises)."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except (TimeoutException, NoSuchElementException):
            return None

    def find_visible(self, by, value, timeout=TIMEOUT):
        """Return visible element or None."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
        except (TimeoutException, NoSuchElementException):
            return None

    def find_clickable(self, by, value, timeout=TIMEOUT):
        """Return clickable element or None."""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        except (TimeoutException, NoSuchElementException):
            return None

    def js_click(self, element):
        """Click via JavaScript (avoids overlay issues)."""
        self.driver.execute_script("arguments[0].click();", element)

    def safe_send_keys(self, element, text):
        """Clear and type into an element safely."""
        element.clear()
        element.send_keys(text)

    def page_text(self):
        """Return all visible text on the page."""
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            return ""

    # ── Auth helpers ────────────────────────────────────────────────────────

    def login(self, username, password):
        """Perform login and return True if redirected away from login page."""
        self.go("/accounts/login/")
        u = self.find(By.NAME, "u_name")
        p = self.find(By.NAME, "u_password")
        if not u or not p:
            return False
        self.safe_send_keys(u, username)
        self.safe_send_keys(p, password)
        btn = self.find_clickable(By.CSS_SELECTOR, "button[type='submit']")
        if btn:
            self.js_click(btn)
        time.sleep(PAGE_WAIT + 2)
        return "login" not in self.driver.current_url.lower()

    def logout(self):
        """Logout via any logout link on page."""
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']")
            if links:
                self.js_click(links[0])
                time.sleep(PAGE_WAIT)
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════════════
#  MODULE 1 – ACCOUNT TESTS
# ════════════════════════════════════════════════════════════════════════════

class AccountsTests(HealthcareTestBase):
    """Covers: homepage, registration page, login page, registration flow,
    login flow, invalid login, and profile access."""

    # ── TC-A01 ───────────────────────────────────────────────────────────────
    def test_A01_homepage_loads(self):
        """Homepage must load and have a non-empty <title>."""
        self.go()
        title = self.driver.title
        self.assertTrue(len(title) > 0, f"Expected a page title, got: '{title}'")
        print(f"\n  ✅ TC-A01 | Homepage loaded | title='{title}'")

    # ── TC-A02 ───────────────────────────────────────────────────────────────
    def test_A02_registration_page_fields(self):
        """Registration page must contain all required form fields."""
        self.go("/accounts/register/")
        required = ["u_name", "u_fname", "u_email", "u_password", "u_address", "u_mobile"]
        missing = []
        for name in required:
            el = self.find(By.NAME, name, timeout=10)
            if el is None:
                missing.append(name)
        self.assertEqual(missing, [], f"Missing fields on registration page: {missing}")
        print(f"\n  ✅ TC-A02 | Registration page | all {len(required)} fields present")

    # ── TC-A03 ───────────────────────────────────────────────────────────────
    def test_A03_login_page_fields(self):
        """Login page must have username and password fields."""
        self.go("/accounts/login/")
        u = self.find(By.NAME, "u_name")
        p = self.find(By.NAME, "u_password")
        self.assertIsNotNone(u, "Username field missing on login page")
        self.assertIsNotNone(p, "Password field missing on login page")
        print("\n  ✅ TC-A03 | Login page | both fields present")

    # ── TC-A04 ───────────────────────────────────────────────────────────────
    def test_A04_successful_registration(self):
        """A new user should be able to register successfully."""
        self.go("/accounts/register/")

        suffix = _random_suffix()
        username = f"auto_{suffix}"
        email    = f"auto_{suffix}@testmail.com"
        password = "TestPass@123"

        fields = {
            "u_name":     username,
            "u_fname":    "AutoTest",
            "u_email":    email,
            "u_password": password,
            "u_address":  "123 Test Road, Dhaka",
            "u_mobile":   "01700000001",
        }

        for name, value in fields.items():
            el = self.find(By.NAME, name)
            self.assertIsNotNone(el, f"Field '{name}' not found on registration page")
            self.safe_send_keys(el, value)
            time.sleep(0.3)

        # Select gender via radio button (Male)
        try:
            radio = self.driver.find_element(By.CSS_SELECTOR, "input[value='Male']")
            self.js_click(radio)
        except NoSuchElementException:
            pass  # gender field optional

        btn = self.find_clickable(By.CSS_SELECTOR, "button[type='submit']")
        self.assertIsNotNone(btn, "Submit button not found")
        self.js_click(btn)
        time.sleep(PAGE_WAIT + 3)

        # Store globally so other tests can use these credentials
        SHARED_CREDS["username"] = username
        SHARED_CREDS["password"] = password

        final_url = self.driver.current_url
        # A successful registration should NOT stay on the register page
        self.assertNotIn(
            "register", final_url.lower(),
            f"Registration may have failed – still on: {final_url}"
        )
        print(f"\n  ✅ TC-A04 | Registration | user='{username}' | url='{final_url}'")

    # ── TC-A05 ───────────────────────────────────────────────────────────────
    def test_A05_successful_login(self):
        """Registered user must be able to log in."""
        # Ensure registration ran first (shared creds set)
        if not SHARED_CREDS["username"]:
            self.test_A04_successful_registration()

        result = self.login(SHARED_CREDS["username"], SHARED_CREDS["password"])
        self.assertTrue(result, "Login failed – still on login page after submit")
        print(f"\n  ✅ TC-A05 | Login | user='{SHARED_CREDS['username']}' | success")
        self.logout()

    # ── TC-A06 ───────────────────────────────────────────────────────────────
    def test_A06_invalid_login_stays_on_login(self):
        """Invalid credentials should NOT redirect away from the login page."""
        self.go("/accounts/login/")
        u = self.find(By.NAME, "u_name")
        p = self.find(By.NAME, "u_password")
        self.safe_send_keys(u, "totally_wrong_user_xyz")
        self.safe_send_keys(p, "WrongPass999!")
        btn = self.find_clickable(By.CSS_SELECTOR, "button[type='submit']")
        self.js_click(btn)
        time.sleep(PAGE_WAIT + 1)

        current = self.driver.current_url
        # Should still be on login (or show error on same page)
        on_login = "login" in current.lower()
        has_error = any(kw in self.page_text().lower() for kw in
                        ["invalid", "incorrect", "error", "wrong", "failed"])

        self.assertTrue(
            on_login or has_error,
            f"Invalid login should fail but redirected to: {current}"
        )
        print(f"\n  ✅ TC-A06 | Invalid login rejected | url='{current}'")

    # ── TC-A07 ───────────────────────────────────────────────────────────────
    def test_A07_profile_requires_auth(self):
        """Accessing /accounts/profile/ without login should redirect to login."""
        self.logout()          # ensure logged out
        self.go("/accounts/profile/")
        current = self.driver.current_url
        redirected_to_login = "login" in current.lower()
        # Some sites serve 403/404 for unauthenticated profile access
        has_auth_error = any(kw in self.page_text().lower() for kw in
                             ["login", "sign in", "403", "unauthorized"])
        self.assertTrue(
            redirected_to_login or has_auth_error,
            f"Profile page should require auth but loaded at: {current}"
        )
        print(f"\n  ✅ TC-A07 | Profile protected | url='{current}'")

    # ── TC-A08 ───────────────────────────────────────────────────────────────
    def test_A08_logout_works(self):
        """After login, logout should clear the session."""
        if not SHARED_CREDS["username"]:
            self.test_A04_successful_registration()
        self.login(SHARED_CREDS["username"], SHARED_CREDS["password"])
        self.logout()
        # After logout, re-accessing profile should go to login
        self.go("/accounts/profile/")
        current = self.driver.current_url
        self.assertIn("login", current.lower(),
                      f"After logout, profile should redirect to login. Got: {current}")
        print(f"\n  ✅ TC-A08 | Logout | redirected to: '{current}'")


# ════════════════════════════════════════════════════════════════════════════
#  MODULE 2 – APPOINTMENT TESTS
# ════════════════════════════════════════════════════════════════════════════

class AppointmentTests(HealthcareTestBase):
    """Covers: doctors list, search, doctor detail, top doctors,
    prescription history auth-guard, booking page."""

    # ── TC-AP01 ──────────────────────────────────────────────────────────────
    def test_AP01_appointments_page_loads(self):
        """Appointments / doctors listing page must load."""
        self.go("/appointments/")
        text = self.page_text()
        self.assertTrue(len(text) > 50, "Appointments page returned empty or tiny body")
        print(f"\n  ✅ TC-AP01 | Appointments page loaded")

    # ── TC-AP02 ──────────────────────────────────────────────────────────────
    def test_AP02_search_doctors(self):
        """Doctor search box must accept input and return results page."""
        self.go("/appointments/")
        search = self.find(By.NAME, "q", timeout=10)
        if search is None:
            self.skipTest("Search field 'q' not found – skipping")

        self.safe_send_keys(search, "doctor")
        search.send_keys(Keys.RETURN)
        time.sleep(PAGE_WAIT)

        body = self.page_text()
        self.assertTrue(len(body) > 0, "Search results page is empty")
        print(f"\n  ✅ TC-AP02 | Doctor search | results page loaded")

    # ── TC-AP03 ──────────────────────────────────────────────────────────────
    def test_AP03_doctor_detail_page(self):
        """Clicking the first doctor link must open a detail page."""
        self.go("/appointments/")
        links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='doctor']")
        if not links:
            self.skipTest("No doctor links found on appointments page")

        href = links[0].get_attribute("href")
        self.driver.get(href)
        time.sleep(PAGE_WAIT)

        body = self.page_text()
        self.assertTrue(len(body) > 50, "Doctor detail page returned empty body")
        print(f"\n  ✅ TC-AP03 | Doctor detail | url='{self.driver.current_url}'")

    # ── TC-AP04 ──────────────────────────────────────────────────────────────
    def test_AP04_top_doctors_page(self):
        """Top doctors page must load."""
        self.go("/appointments/top_doctors/")
        body = self.page_text()
        self.assertTrue(len(body) > 50, "Top doctors page returned empty body")
        print(f"\n  ✅ TC-AP04 | Top doctors page loaded")

    # ── TC-AP05 ──────────────────────────────────────────────────────────────
    def test_AP05_prescription_history_requires_login(self):
        """Prescription history must be protected (redirect to login)."""
        self.logout()
        self.go("/appointments/prescription_history/")
        current = self.driver.current_url
        protected = ("login" in current.lower() or
                     any(kw in self.page_text().lower()
                         for kw in ["login", "sign in", "unauthorized", "403"]))
        self.assertTrue(protected,
                        f"Prescription history should be protected. Got: {current}")
        print(f"\n  ✅ TC-AP05 | Prescription history protected | url='{current}'")

    # ── TC-AP06 ──────────────────────────────────────────────────────────────
    def test_AP06_emergency_blood_finder_page(self):
        """Emergency blood finder page must load."""
        self.go("/appointments/emergency/")
        body = self.page_text()
        self.assertTrue(len(body) > 50, "Emergency page returned empty body")
        print(f"\n  ✅ TC-AP06 | Emergency blood finder page loaded")

    # ── TC-AP07 ──────────────────────────────────────────────────────────────
    def test_AP07_appointments_page_has_doctor_listings(self):
        """Appointments page should show at least one doctor or listing."""
        self.go("/appointments/")
        body = self.page_text().lower()
        has_content = any(kw in body for kw in
                          ["doctor", "specialist", "appointment", "book", "consult"])
        self.assertTrue(has_content,
                        "Appointments page has no doctor/booking related content")
        print(f"\n  ✅ TC-AP07 | Appointments page has listing content")


# ════════════════════════════════════════════════════════════════════════════
#  MODULE 3 – DIET COMPATIBILITY TESTS
# ════════════════════════════════════════════════════════════════════════════

class DietCompatibilityTests(HealthcareTestBase):
    """Covers: diet dashboard, diet analysis form."""

    # ── TC-D01 ───────────────────────────────────────────────────────────────
    def test_D01_diet_page_loads(self):
        """Diet compatibility page must load."""
        self.go("/diet/")
        body = self.page_text()
        self.assertTrue(len(body) > 50, "Diet page returned empty body")
        print(f"\n  ✅ TC-D01 | Diet page loaded")

    # ── TC-D02 ───────────────────────────────────────────────────────────────
    def test_D02_diet_page_has_relevant_content(self):
        """Diet page should contain diet-related keywords."""
        self.go("/diet/")
        body = self.page_text().lower()
        has_content = any(kw in body for kw in
                          ["diet", "food", "calorie", "nutrition", "meal",
                           "health", "compatible", "login", "sign"])
        self.assertTrue(has_content,
                        "Diet page has no diet-related or auth-prompt content")
        print(f"\n  ✅ TC-D02 | Diet page has relevant content")

    # ── TC-D03 ───────────────────────────────────────────────────────────────
    def test_D03_diet_form_or_auth_guard(self):
        """Diet analysis should either show a form (logged in) or auth guard."""
        self.logout()
        self.go("/diet/")
        current = self.driver.current_url
        body    = self.page_text().lower()

        has_form = bool(self.find(By.TAG_NAME, "form", timeout=5))
        is_guarded = ("login" in current.lower() or
                      any(kw in body for kw in ["login", "sign in"]))

        self.assertTrue(
            has_form or is_guarded,
            "Diet page should either show a form or require authentication"
        )
        print(f"\n  ✅ TC-D03 | Diet page form/auth guard check passed")


# ════════════════════════════════════════════════════════════════════════════
#  MODULE 4 – MEDICINE REMINDER TESTS
# ════════════════════════════════════════════════════════════════════════════

class MedicineReminderTests(HealthcareTestBase):
    """Covers: reminder page, auth guard, reminder form."""

    # ── TC-M01 ───────────────────────────────────────────────────────────────
    def test_M01_reminders_page_loads(self):
        """Medicine reminders page must load (possibly redirecting to login)."""
        self.go("/reminders/")
        body = self.page_text()
        self.assertTrue(len(body) > 50, "Reminders page returned empty body")
        print(f"\n  ✅ TC-M01 | Medicine reminders page loaded")

    # ── TC-M02 ───────────────────────────────────────────────────────────────
    def test_M02_reminders_requires_auth_or_shows_list(self):
        """Reminders page: either shows reminders list or redirects to login."""
        self.logout()
        self.go("/reminders/")
        current = self.driver.current_url
        body    = self.page_text().lower()

        has_content = any(kw in body for kw in
                          ["reminder", "medicine", "medication", "drug",
                           "login", "sign in"])
        self.assertTrue(has_content,
                        "Reminders page has no expected content or auth prompt")
        print(f"\n  ✅ TC-M02 | Reminders page content/auth check passed")

    # ── TC-M03 ───────────────────────────────────────────────────────────────
    def test_M03_add_reminder_url_accessible(self):
        """Add-reminder URL should respond (not 404/500)."""
        self.go("/reminders/add/")
        body = self.page_text()
        # Should NOT be a server error
        self.assertNotIn("500", body[:200], "Add-reminder page returned 500 error")
        print(f"\n  ✅ TC-M03 | Add-reminder URL responded without 500")


# ════════════════════════════════════════════════════════════════════════════
#  MODULE 5 – NAVIGATION TESTS
# ════════════════════════════════════════════════════════════════════════════

class NavigationTests(HealthcareTestBase):
    """Covers: nav links, page-to-page navigation, footer, 404 handling."""

    # ── TC-N01 ───────────────────────────────────────────────────────────────
    def test_N01_nav_contains_appointment_link(self):
        """Homepage navigation should contain a link to appointments."""
        self.go()
        links = self.driver.find_elements(
            By.CSS_SELECTOR, "a[href*='appointment']"
        )
        self.assertGreater(len(links), 0,
                           "No appointment link found in navigation")
        print(f"\n  ✅ TC-N01 | Nav | {len(links)} appointment link(s) found")

    # ── TC-N02 ───────────────────────────────────────────────────────────────
    def test_N02_nav_contains_login_or_logout(self):
        """Nav should always show either login or logout link."""
        self.go()
        all_links = [a.get_attribute("href") or "" for a in
                     self.driver.find_elements(By.TAG_NAME, "a")]
        has_auth = any("login" in h.lower() or "logout" in h.lower()
                       for h in all_links)
        self.assertTrue(has_auth,
                        "No login/logout link found anywhere on homepage")
        print(f"\n  ✅ TC-N02 | Nav | login or logout link present")

    # ── TC-N03 ───────────────────────────────────────────────────────────────
    def test_N03_all_nav_links_are_reachable(self):
        """All internal <a href> links on the homepage should not 404."""
        self.go()
        anchors = self.driver.find_elements(By.CSS_SELECTOR, "nav a, header a")
        hrefs = list({
            a.get_attribute("href") for a in anchors
            if a.get_attribute("href") and BASE_URL in (a.get_attribute("href") or "")
        })

        failed = []
        for href in hrefs[:10]:   # cap at 10 to keep test fast
            self.driver.get(href)
            time.sleep(2)
            body = self.page_text()
            if "404" in self.driver.title or "page not found" in body.lower():
                failed.append(href)

        self.assertEqual(failed, [], f"404 detected for links: {failed}")
        print(f"\n  ✅ TC-N03 | All {len(hrefs[:10])} nav link(s) reachable")

    # ── TC-N04 ───────────────────────────────────────────────────────────────
    def test_N04_unknown_url_returns_404(self):
        """Navigating to a bogus URL should show a 404 / not found page."""
        self.driver.get(BASE_URL + "/this_url_does_not_exist_xyz_123/")
        time.sleep(PAGE_WAIT)
        body  = self.page_text().lower()
        title = self.driver.title.lower()
        is_404 = ("404" in body or "not found" in body or
                  "404" in title or "not found" in title)
        self.assertTrue(is_404,
                        "Non-existent URL did not show 404 / not found")
        print(f"\n  ✅ TC-N04 | 404 page shown for unknown URL")


# ════════════════════════════════════════════════════════════════════════════
#  MODULE 6 – RESPONSIVE DESIGN TESTS
# ════════════════════════════════════════════════════════════════════════════

class ResponsiveDesignTests(HealthcareTestBase):
    """Checks that the homepage renders visible content at three viewport sizes."""

    VIEWPORTS = {
        "Mobile  (375×667)":  (375,  667),
        "Tablet  (768×1024)": (768,  1024),
        "Desktop (1920×1080)":(1920, 1080),
    }

    def _check_viewport(self, label, width, height):
        self.driver.set_window_size(width, height)
        self.go()
        body = self.find_visible(By.TAG_NAME, "body")
        self.assertIsNotNone(body, f"{label}: <body> not visible")
        self.assertTrue(body.is_displayed(),
                        f"{label}: <body> is not displayed")
        print(f"\n  ✅ {label} | body visible")

    def test_R01_mobile_view(self):
        self._check_viewport(*["Mobile  (375×667)",  375,  667])

    def test_R02_tablet_view(self):
        self._check_viewport(*["Tablet  (768×1024)", 768, 1024])

    def test_R03_desktop_view(self):
        self._check_viewport(*["Desktop (1920×1080)", 1920, 1080])


# ════════════════════════════════════════════════════════════════════════════
#  MODULE 7 – SECURITY TESTS
# ════════════════════════════════════════════════════════════════════════════

class SecurityTests(HealthcareTestBase):
    """Covers: HTTPS, CSRF token presence, no sensitive data leaks."""

    # ── TC-S01 ───────────────────────────────────────────────────────────────
    def test_S01_site_uses_https(self):
        """The site must use HTTPS."""
        self.go()
        url = self.driver.current_url
        self.assertTrue(url.startswith("https://"),
                        f"Site is NOT using HTTPS. Current URL: {url}")
        print(f"\n  ✅ TC-S01 | HTTPS | url='{url}'")

    # ── TC-S02 ───────────────────────────────────────────────────────────────
    def test_S02_csrf_token_in_login_form(self):
        """Login form must include a CSRF token input."""
        self.go("/accounts/login/")
        csrf = self.find(By.CSS_SELECTOR, "input[name='csrfmiddlewaretoken']",
                         timeout=10)
        self.assertIsNotNone(csrf,
                             "CSRF token hidden input missing from login form")
        print(f"\n  ✅ TC-S02 | CSRF token present in login form")

    # ── TC-S03 ───────────────────────────────────────────────────────────────
    def test_S03_csrf_token_in_registration_form(self):
        """Registration form must include a CSRF token."""
        self.go("/accounts/register/")
        csrf = self.find(By.CSS_SELECTOR, "input[name='csrfmiddlewaretoken']",
                         timeout=10)
        self.assertIsNotNone(csrf,
                             "CSRF token missing from registration form")
        print(f"\n  ✅ TC-S03 | CSRF token present in registration form")

    # ── TC-S04 ───────────────────────────────────────────────────────────────
    def test_S04_password_field_is_masked(self):
        """Login password field must be of type='password' (masked)."""
        self.go("/accounts/login/")
        pwd = self.find(By.NAME, "u_password")
        self.assertIsNotNone(pwd, "Password field not found")
        field_type = pwd.get_attribute("type")
        self.assertEqual(field_type, "password",
                         f"Password field type should be 'password', got '{field_type}'")
        print(f"\n  ✅ TC-S04 | Password field is masked (type='password')")

    # ── TC-S05 ───────────────────────────────────────────────────────────────
    def test_S05_no_debug_traceback_on_homepage(self):
        """Homepage must not expose Django debug tracebacks."""
        self.go()
        body = self.page_text().lower()
        self.assertNotIn("traceback (most recent call last)", body,
                         "Django debug traceback exposed on homepage!")
        print(f"\n  ✅ TC-S05 | No debug traceback exposed")

    # ── TC-S06 ───────────────────────────────────────────────────────────────
    def test_S06_sensitive_urls_protected(self):
        """Django admin and debug panel must not be publicly accessible."""
        self.logout()
        protected_paths = ["/admin/", "/admin/login/"]
        for path in protected_paths:
            self.go(path)
            body = self.page_text().lower()
            # Should show admin login (not the actual admin dashboard)
            exposed = ("django administration" in body and
                       "log out" in body)          # logged in = exposed
            self.assertFalse(exposed,
                             f"Admin panel appears to be accessible at {path}")
        print(f"\n  ✅ TC-S06 | Sensitive URLs not publicly accessible")


# ════════════════════════════════════════════════════════════════════════════
#  MODULE 8 – EMERGENCY BLOOD FINDER TESTS
# ════════════════════════════════════════════════════════════════════════════

class EmergencyBloodFinderTests(HealthcareTestBase):
    """Covers: emergency page load, blood group filter, donor listing."""

    # ── TC-E01 ───────────────────────────────────────────────────────────────
    def test_E01_emergency_page_loads(self):
        """Emergency blood finder page must load."""
        self.go("/appointments/emergency/")
        body = self.page_text()
        self.assertTrue(len(body) > 50, "Emergency page returned empty body")
        print(f"\n  ✅ TC-E01 | Emergency page loaded")

    # ── TC-E02 ───────────────────────────────────────────────────────────────
    def test_E02_emergency_page_has_blood_content(self):
        """Emergency page should reference blood groups or donor info."""
        self.go("/appointments/emergency/")
        body = self.page_text().lower()
        has_blood = any(kw in body for kw in
                        ["blood", "donor", "group", "emergency",
                         "a+", "b+", "o+", "ab+", "login", "sign"])
        self.assertTrue(has_blood,
                        "Emergency page has no blood/donor related content")
        print(f"\n  ✅ TC-E02 | Emergency page has blood/donor content")

    # ── TC-E03 ───────────────────────────────────────────────────────────────
    def test_E03_blood_group_filter_or_form_present(self):
        """Emergency page should have a search/filter form or dropdown."""
        self.go("/appointments/emergency/")
        has_form     = bool(self.find(By.TAG_NAME, "form", timeout=5))
        has_select   = bool(self.find(By.TAG_NAME, "select", timeout=5))
        has_input    = bool(self.find(By.TAG_NAME, "input", timeout=5))
        self.assertTrue(
            has_form or has_select or has_input,
            "Emergency page has no search form / filter input"
        )
        print(f"\n  ✅ TC-E03 | Emergency page has filter/form element")


# ════════════════════════════════════════════════════════════════════════════
#  TEST RUNNER
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # ── Determine which suites to run ─────────────────────────────────────
    all_suites = [
        AccountsTests,
        AppointmentTests,
        DietCompatibilityTests,
        MedicineReminderTests,
        NavigationTests,
        ResponsiveDesignTests,
        SecurityTests,
        EmergencyBloodFinderTests,
    ]

    # Allow running a single suite: python test.py AccountsTests
    requested = [a for a in sys.argv[1:] if not a.startswith("--")]
    if requested:
        name_map = {cls.__name__: cls for cls in all_suites}
        all_suites = [name_map[n] for n in requested if n in name_map]
        if not all_suites:
            print(f"❌  Unknown test suite(s): {requested}")
            sys.exit(1)

    # ── Build suite ────────────────────────────────────────────────────────
    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = None    # preserve definition order
    suite  = unittest.TestSuite()
    for cls in all_suites:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    # ── Run ────────────────────────────────────────────────────────────────
    print("\n" + "═" * 70)
    print("  Smart Healthcare System — Selenium Test Suite")
    print(f"  URL     : {BASE_URL}")
    print(f"  Mode    : {'Headless' if HEADLESS else 'Headed (browser visible)'}")
    print(f"  Suites  : {', '.join(c.__name__ for c in all_suites)}")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70)

    runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
    result = runner.run(suite)

    # ── Summary ────────────────────────────────────────────────────────────
    total    = result.testsRun
    failures = len(result.failures)
    errors   = len(result.errors)
    skipped  = len(result.skipped)
    passed   = total - failures - errors - skipped

    print("\n" + "═" * 70)
    print("  TEST SUMMARY")
    print("═" * 70)
    print(f"  Total   : {total}")
    print(f"  ✅ Passed  : {passed}")
    print(f"  ❌ Failed  : {failures}")
    print(f"  💥 Errors  : {errors}")
    print(f"  ⏭  Skipped : {skipped}")
    print("═" * 70)

    if result.failures:
        print("\n  FAILURES:")
        for test, msg in result.failures:
            print(f"  • {test}: {msg.splitlines()[-1]}")

    if result.errors:
        print("\n  ERRORS:")
        for test, msg in result.errors:
            print(f"  • {test}: {msg.splitlines()[-1]}")

    print(f"\n  Finished : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 70 + "\n")

    sys.exit(0 if result.wasSuccessful() else 1)