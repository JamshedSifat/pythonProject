"""
test_home.py — Homepage, Navigation, Responsive Design & Security Tests
Run: python test_home.py
"""

import unittest
import time
from selenium.webdriver.common.by import By
from test_base import HealthcareTestBase, BASE_URL, TEST_USERNAME


# ═══════════════════════════════════════════════════════════════
#  1. HOMEPAGE TESTS
# ═══════════════════════════════════════════════════════════════

class HomepageTests(HealthcareTestBase):
    """Basic homepage checks."""

    @classmethod
    def setUpClass(cls):
        pass  # No user registration needed for homepage tests

    def test_01_homepage_loads(self):
        """Homepage loads and has a non-empty title."""
        self.driver.get(BASE_URL)
        time.sleep(5)
        title = self.driver.title
        self.assertNotEqual(title.strip(), "", "Homepage title should not be empty")
        print(f"  ✅ Homepage loaded — title: {title}")

    def test_02_homepage_has_content(self):
        """Homepage body has visible content."""
        self.driver.get(BASE_URL)
        time.sleep(5)
        self.assertPageLoaded("Homepage body should have content")
        print("  ✅ Homepage has visible content")

    def test_03_homepage_has_appointment_link(self):
        """At least one appointment link exists on homepage."""
        self.driver.get(BASE_URL)
        time.sleep(5)
        links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='appointment']")
        self.assertGreater(len(links), 0, "Appointment link should be in navbar")
        print(f"  ✅ Found {len(links)} appointment link(s) on homepage")

    def test_04_homepage_has_login_link(self):
        """Login link visible when not authenticated."""
        self.driver.get(BASE_URL)
        time.sleep(5)
        login_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='login']")
        self.assertGreater(len(login_links), 0, "Login link should be visible")
        print(f"  ✅ Found {len(login_links)} login link(s) on homepage")

    def test_05_homepage_has_register_link(self):
        """Register link visible when not authenticated."""
        self.driver.get(BASE_URL)
        time.sleep(5)
        reg_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='register']")
        self.assertGreater(len(reg_links), 0, "Register link should be visible")
        print(f"  ✅ Found {len(reg_links)} register link(s) on homepage")

    def test_06_navbar_shows_logout_after_login(self):
        """Navbar updates to show logout / username after login."""
        self.login()
        self.assertNotOnLoginPage()
        self.driver.get(BASE_URL)
        time.sleep(5)
        logout_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']")
        user_text = any(
            TEST_USERNAME.lower() in el.text.lower()
            for el in self.driver.find_elements(By.CSS_SELECTOR, "nav a, nav span, nav li")
        )
        self.assertTrue(len(logout_links) > 0 or user_text,
                        "Navbar should show logout or username after login")
        print("  ✅ Navbar updated correctly after login")


# ═══════════════════════════════════════════════════════════════
#  2. NAVIGATION TESTS
# ═══════════════════════════════════════════════════════════════

class NavigationTests(HealthcareTestBase):
    """All main public pages are reachable."""

    @classmethod
    def setUpClass(cls):
        pass

    PAGES = {
        "Home":          f"{BASE_URL}/",
        "Login":         f"{BASE_URL}/accounts/login/",
        "Register":      f"{BASE_URL}/accounts/register/",
        "Appointments":  f"{BASE_URL}/appointments/",
        "Top Doctors":   f"{BASE_URL}/appointments/top_doctors/",
        "Emergency":     f"{BASE_URL}/appointments/emergency/",
    }

    def test_01_all_public_pages_reachable(self):
        """Each public page loads without a 404."""
        for name, url in self.PAGES.items():
            self.driver.get(url)
            time.sleep(4)
            self.assertFalse(self.is_404(), f"{name} page should not be 404")
            print(f"  ✅ {name} ({url}) — reachable")

    def test_02_clicking_appointment_nav_link(self):
        """Clicking appointments link from homepage navigates correctly."""
        self.driver.get(BASE_URL)
        time.sleep(5)
        links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='appointment']")
        self.assertGreater(len(links), 0, "Appointment nav link must exist")
        links[0].click()
        time.sleep(5)
        self.assertPageLoaded("Appointments page should load via nav link")
        print(f"  ✅ Appointment nav link works — URL: {self.driver.current_url}")

    def test_03_clicking_login_link(self):
        """Clicking login navigates to login page."""
        self.driver.get(BASE_URL)
        time.sleep(5)
        login_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='login']")
        self.assertGreater(len(login_links), 0)
        login_links[0].click()
        time.sleep(4)
        self.assertIn("login", self.driver.current_url.lower(),
                      "Should be on login page")
        print("  ✅ Login nav link works")

    def test_04_clicking_register_link(self):
        """Clicking register navigates to registration page."""
        self.driver.get(BASE_URL)
        time.sleep(5)
        reg_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='register']")
        if reg_links:
            reg_links[0].click()
            time.sleep(4)
            self.assertIn("register", self.driver.current_url.lower(),
                          "Should be on register page")
            print("  ✅ Register nav link works")
        else:
            print("  ⚠️  Register link not found in nav")


# ═══════════════════════════════════════════════════════════════
#  3. RESPONSIVE DESIGN TESTS
# ═══════════════════════════════════════════════════════════════

class ResponsiveDesignTests(HealthcareTestBase):
    """Pages render properly on different viewport sizes."""

    @classmethod
    def setUpClass(cls):
        pass

    def _check_viewport(self, width, height, label, url=None):
        self.driver.set_window_size(width, height)
        self.driver.get(url or BASE_URL)
        time.sleep(4)
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(),
                        f"Body should be visible at {label} ({width}×{height})")
        print(f"  ✅ {label} ({width}×{height}) — page visible")

    def test_01_homepage_mobile(self):
        self._check_viewport(375, 667, "Mobile iPhone SE")

    def test_02_homepage_tablet(self):
        self._check_viewport(768, 1024, "Tablet iPad")

    def test_03_homepage_desktop(self):
        self._check_viewport(1920, 1080, "Desktop 1080p")

    def test_04_appointments_mobile(self):
        self._check_viewport(375, 667, "Mobile",
                             url=f"{BASE_URL}/appointments/")

    def test_05_appointments_tablet(self):
        self._check_viewport(768, 1024, "Tablet",
                             url=f"{BASE_URL}/appointments/")

    def test_06_login_page_mobile(self):
        self._check_viewport(375, 667, "Mobile",
                             url=f"{BASE_URL}/accounts/login/")



#  4. SECURITY TESTS


class SecurityTests(HealthcareTestBase):
    """Basic security checks."""

    @classmethod
    def setUpClass(cls):
        pass

    def test_01_https_enabled(self):
        """Site is served over HTTPS."""
        self.driver.get(BASE_URL)
        time.sleep(3)
        self.assertTrue(self.driver.current_url.startswith("https"),
                        "Site must use HTTPS")
        print("  ✅ HTTPS enabled")

    def test_02_profile_protected(self):
        """Profile page redirects unauthenticated users to login."""
        self.driver.get(f"{BASE_URL}/accounts/profile/")
        time.sleep(5)
        is_protected = (
            "login" in self.driver.current_url.lower() or
            self.wait_for(By.NAME, "u_name", timeout=5) is not None
        )
        self.assertTrue(is_protected, "Profile must be login-protected")
        print("  ✅ Profile page is login-protected")

    def test_03_prescription_history_protected(self):
        """Prescription history redirects unauthenticated users."""
        self.driver.get(f"{BASE_URL}/appointments/prescription_history/")
        time.sleep(5)
        is_protected = (
            "login" in self.driver.current_url.lower() or
            self.wait_for(By.NAME, "u_name", timeout=5) is not None
        )
        self.assertTrue(is_protected, "Prescription history must be login-protected")
        print("  ✅ Prescription history is login-protected")

    def test_04_session_cleared_after_logout(self):
        """Protected pages are inaccessible after logout."""
        self.login()
        self.assertNotOnLoginPage()
        self.logout()

        self.driver.get(f"{BASE_URL}/accounts/profile/")
        time.sleep(5)
        is_redirected = (
            "login" in self.driver.current_url.lower() or
            self.wait_for(By.NAME, "u_name", timeout=5) is not None
        )
        self.assertTrue(is_redirected, "Session should be cleared after logout")
        print("  ✅ Session cleared — profile redirects after logout")


# Runner 

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(HomepageTests))
    suite.addTests(loader.loadTestsFromTestCase(NavigationTests))
    suite.addTests(loader.loadTestsFromTestCase(ResponsiveDesignTests))
    suite.addTests(loader.loadTestsFromTestCase(SecurityTests))

    import unittest
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"  Passed: {passed} / {result.testsRun}")
    print(f"  Failures: {len(result.failures)}  |  Errors: {len(result.errors)}")
    print("=" * 60)
    exit(0 if result.wasSuccessful() else 1)
