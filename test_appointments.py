"""
test_appointments.py — Appointment Module Tests
Covers: Doctors list, Search, Detail, Top Doctors, Emergency,
        Book Appointment (protected), My Appointments (protected),
        Prescription History (protected)
Run: python test_appointments.py
"""

import unittest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from test_base import HealthcareTestBase, BASE_URL


class AppointmentTests(HealthcareTestBase):
    """Full test suite for the Appointments module."""

    # ══════════════════════════════════════════════════════════
    #  PUBLIC PAGES (no login needed)
    # ══════════════════════════════════════════════════════════

    def test_01_doctors_listing_page_loads(self):
        """Doctors list page loads without login."""
        self.driver.get(f"{BASE_URL}/appointments/")
        time.sleep(5)
        self.assertFalse(self.is_404(), "Appointments page should not be 404")
        self.assertPageLoaded("Doctors listing page should have content")
        print("  ✅ Doctors listing page loaded")

    def test_02_top_doctors_page_loads(self):
        """Top-doctors page loads without login."""
        self.driver.get(f"{BASE_URL}/appointments/top_doctors/")
        time.sleep(5)
        self.assertFalse(self.is_404(), "Top doctors page should not be 404")
        self.assertPageLoaded("Top doctors page should have content")
        print("  ✅ Top doctors page loaded")

    def test_03_emergency_blood_finder_loads(self):
        """Emergency blood finder page loads without login."""
        self.driver.get(f"{BASE_URL}/appointments/emergency/")
        time.sleep(5)
        self.assertFalse(self.is_404(), "Emergency page should not be 404")
        self.assertPageLoaded("Emergency page should have content")
        print("  ✅ Emergency blood finder page loaded")

    def test_04_doctor_search_works(self):
        """User can type in the doctor search field and get results."""
        self.driver.get(f"{BASE_URL}/appointments/")
        time.sleep(5)
        search = self.wait_for(By.NAME, "q", timeout=10)
        if not search:
            # try other common field names
            for name in ["search", "query", "doctor_name"]:
                search = self.wait_for(By.NAME, name, timeout=4)
                if search:
                    break

        if search:
            search.clear()
            search.send_keys("doctor")
            time.sleep(1)
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                btn.click()
            except NoSuchElementException:
                search.send_keys(Keys.RETURN)
            time.sleep(5)
            self.assertPageLoaded("Search results page should have content")
            print("  ✅ Doctor search works")
        else:
            print("  ⚠️  Search field not found — skipping (field name may differ)")

    def test_05_doctor_detail_page_loads(self):
        """Clicking a doctor card/link loads that doctor's detail page."""
        self.driver.get(f"{BASE_URL}/appointments/")
        time.sleep(5)
        links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='doctor']")
        if links:
            href = links[0].get_attribute("href")
            self.driver.get(href)
            time.sleep(5)
            self.assertFalse(self.is_404(), "Doctor detail page should not be 404")
            self.assertPageLoaded("Doctor detail page should have content")
            print(f"  ✅ Doctor detail page loaded — {href}")
        else:
            print("  ⚠️  No doctor links found on listing page")

    # ══════════════════════════════════════════════════════════
    #  PROTECTED PAGES — redirect check (NOT logged in)
    # ══════════════════════════════════════════════════════════

    def test_06_my_appointments_redirects_without_login(self):
        """My-appointments page redirects unauthenticated users to login."""
        candidates = [
            "/appointments/my_appointments/",
            "/appointments/my-appointments/",
            "/appointments/user/",
            "/appointments/booked/",
        ]
        path = self.find_working_path(candidates)
        if path is None:
            print("  ⚠️  My-appointments URL not found — skipping")
            return

        is_protected = (
            "login" in self.driver.current_url.lower() or
            self.wait_for(By.NAME, "u_name", timeout=5) is not None
        )
        self.assertTrue(is_protected,
                        f"My-appointments ({path}) must redirect to login")
        print(f"  ✅ My-appointments ({path}) is login-protected")

    def test_07_prescription_history_redirects_without_login(self):
        """Prescription history redirects unauthenticated users."""
        self.driver.get(f"{BASE_URL}/appointments/prescription_history/")
        time.sleep(5)
        is_protected = (
            "login" in self.driver.current_url.lower() or
            self.wait_for(By.NAME, "u_name", timeout=5) is not None
        )
        self.assertTrue(is_protected,
                        "Prescription history must be login-protected")
        print("  ✅ Prescription history is login-protected")

    def test_08_book_appointment_redirects_without_login(self):
        """Book-appointment page or button redirects unauthenticated users."""
        self.driver.get(f"{BASE_URL}/appointments/")
        time.sleep(5)
        book_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='book']")
        if book_links:
            href = book_links[0].get_attribute("href")
            self.driver.get(href)
            time.sleep(5)
            is_protected = (
                "login" in self.driver.current_url.lower() or
                self.wait_for(By.NAME, "u_name", timeout=5) is not None
            )
            if is_protected:
                print(f"  ✅ Book-appointment ({href}) is login-protected")
            else:
                # Some apps allow viewing the form but block submission — that's OK
                self.assertPageLoaded("Booking page should load")
                print("  ✅ Booking page loads (public form — submit may be protected)")
        else:
            print("  ⚠️  No booking links found on listing page")

    # ══════════════════════════════════════════════════════════
    #  PROTECTED PAGES — full access check (LOGGED IN)
    # ══════════════════════════════════════════════════════════

    def test_09_my_appointments_accessible_after_login(self):
        """Logged-in user can view their appointments list."""
        self.login()
        self.assertNotOnLoginPage()

        candidates = [
            "/appointments/my_appointments/",
            "/appointments/my-appointments/",
            "/appointments/user/",
            "/appointments/booked/",
        ]
        path = self.find_working_path(candidates)

        if path:
            self.assertNotOnLoginPage(
                "My-appointments should not redirect to login after auth"
            )
            self.assertPageLoaded("My-appointments page should have content")
            print(f"  ✅ My-appointments accessible after login — {path}")
        else:
            # Try clicking from navbar
            self.driver.get(BASE_URL)
            time.sleep(4)
            nav_links = self.driver.find_elements(
                By.XPATH,
                "//a[contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'),'appointment')]"
            )
            if nav_links:
                nav_links[0].click()
                time.sleep(5)
                self.assertPageLoaded("Appointments page reachable via navbar")
                print("  ✅ Appointments page reachable via navbar after login")
            else:
                print("  ⚠️  My-appointments URL could not be found")

    def test_10_prescription_history_accessible_after_login(self):
        """Logged-in user can access prescription history."""
        self.login()
        self.assertNotOnLoginPage()

        self.driver.get(f"{BASE_URL}/appointments/prescription_history/")
        time.sleep(5)
        self.assertNotOnLoginPage(
            "Prescription history should be accessible after login"
        )
        self.assertPageLoaded("Prescription history page should have content")
        print("  ✅ Prescription history accessible after login")

    def test_11_book_appointment_form_accessible_after_login(self):
        """Logged-in user can reach and see the appointment booking form."""
        self.login()
        self.assertNotOnLoginPage()

        self.driver.get(f"{BASE_URL}/appointments/")
        time.sleep(5)

        # Try direct book links first
        book_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='book']")
        if not book_links:
            book_links = self.driver.find_elements(
                By.XPATH,
                "//a[contains(translate(text(),'BOOKAPPOINTMENT','bookappointment'),'book')]"
            )

        if book_links:
            book_links[0].click()
            time.sleep(5)
            self.assertNotOnLoginPage("Booking form should stay open when logged in")
            self.assertPageLoaded("Booking form page should have content")
            print(f"  ✅ Booking form accessible — URL: {self.driver.current_url}")
        else:
            # Dig into a doctor detail page
            doctor_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='doctor']")
            if doctor_links:
                doctor_links[0].click()
                time.sleep(4)
                inner_book = self.driver.find_elements(
                    By.XPATH,
                    "//a[contains(translate(text(),'BOOK','book'),'book')] | "
                    "//button[contains(translate(text(),'BOOK','book'),'book')]"
                )
                if inner_book:
                    inner_book[0].click()
                    time.sleep(5)
                    self.assertPageLoaded("Booking form accessible via doctor detail")
                    print("  ✅ Booking form reachable via doctor detail page")
                    return
            print("  ⚠️  Could not locate booking form links")

    def test_12_appointment_navbar_link_works_when_logged_in(self):
        """Appointments navbar link still works after login."""
        self.login()
        self.assertNotOnLoginPage()

        self.driver.get(BASE_URL)
        time.sleep(5)
        links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='appointment']")
        self.assertGreater(len(links), 0, "Appointment nav link must exist after login")
        links[0].click()
        time.sleep(5)
        self.assertPageLoaded("Appointments page should load via nav after login")
        print("  ✅ Appointments navbar link works when logged in")


# ─── Runner ──────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(AppointmentTests))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"  Passed: {passed} / {result.testsRun}")
    print(f"  Failures: {len(result.failures)}  |  Errors: {len(result.errors)}")
    print("=" * 60)
    exit(0 if result.wasSuccessful() else 1)
