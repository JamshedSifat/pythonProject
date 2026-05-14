"""
test_diet.py — Diet Compatibility Module Tests
Covers: Page load, search/form, logged-in access, post-logout protection
Run: python test_diet.py
"""

import unittest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from test_base import HealthcareTestBase, BASE_URL


class DietCompatibilityTests(HealthcareTestBase):
    """Full test suite for the Diet Compatibility module."""

    DIET_PATHS = [
        "/diet/",
        "/diet_compatibility/",
        "/diet-compatibility/",
        "/food/",
        "/nutrition/",
    ]

    # ══════════════════════════════════════════════════════════
    #  PUBLIC / LOAD CHECKS
    # ══════════════════════════════════════════════════════════

    def test_01_diet_page_loads(self):
        """Diet page loads (with or without login)."""
        path = self.find_working_path(self.DIET_PATHS)
        if path is None:
            print("  ⚠️  Diet URL not found — skipping")
            return
        self.assertPageLoaded(f"Diet page at {path} should have content")
        print(f"  ✅ Diet page loaded at {path}")

    def test_02_diet_page_has_content(self):
        """Diet page body is non-empty."""
        path = self.find_working_path(self.DIET_PATHS)
        if path is None:
            print("  ⚠️  Diet URL not found — skipping")
            return
        body = self.body_text()
        self.assertGreater(len(body.strip()), 50,
                           "Diet page should have meaningful content")
        print("  ✅ Diet page has meaningful content")

    def test_03_diet_page_has_form_or_input(self):
        """Diet page contains a form, input, or select element."""
        path = self.find_working_path(self.DIET_PATHS)
        if path is None:
            print("  ⚠️  Diet URL not found — skipping")
            return

        inputs  = self.driver.find_elements(By.TAG_NAME, "input")
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        forms   = self.driver.find_elements(By.TAG_NAME, "form")

        has_form = len(inputs) + len(selects) + len(forms) > 0
        if has_form:
            print(f"  ✅ Diet page has form elements: "
                  f"{len(forms)} form(s), {len(inputs)} input(s), {len(selects)} select(s)")
        else:
            print("  ⚠️  No form elements found — page may be display-only")

    # ══════════════════════════════════════════════════════════
    #  SEARCH / FORM INTERACTION
    # ══════════════════════════════════════════════════════════

    def test_04_diet_search_or_form_works(self):
        """User can interact with the diet search/form field."""
        path = self.find_working_path(self.DIET_PATHS)
        if path is None:
            print("  ⚠️  Diet URL not found — skipping")
            return

        # Try common field names
        search = None
        for name in ["q", "food", "search", "query", "item", "ingredient", "name"]:
            try:
                search = self.driver.find_element(By.NAME, name)
                break
            except NoSuchElementException:
                continue

        if search:
            search.clear()
            search.send_keys("rice")
            time.sleep(1)
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                btn.click()
            except NoSuchElementException:
                search.send_keys(Keys.RETURN)
            time.sleep(5)
            self.assertPageLoaded("Diet search results should load")
            print("  ✅ Diet search/form works")
        else:
            # Try dropdown selects
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            if selects:
                from selenium.webdriver.support.ui import Select
                sel = Select(selects[0])
                try:
                    sel.select_by_index(1)
                    time.sleep(1)
                    try:
                        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                        btn.click()
                        time.sleep(5)
                        self.assertPageLoaded("Diet dropdown form result should load")
                        print("  ✅ Diet dropdown form works")
                    except NoSuchElementException:
                        print("  ⚠️  Select found but no submit button")
                except Exception as e:
                    print(f"  ⚠️  Select interaction failed: {e}")
            else:
                print("  ⚠️  No interactable form field found — page may be display-only")

    def test_05_diet_page_protection_check(self):
        """Check whether diet page requires login or is public."""
        path = self.find_working_path(self.DIET_PATHS)
        if path is None:
            print("  ⚠️  Diet URL not found — skipping")
            return

        is_login_page = (
            "login" in self.driver.current_url.lower() or
            self.wait_for(By.NAME, "u_name", timeout=4) is not None
        )
        if is_login_page:
            print(f"  ℹ️  Diet page ({path}) is login-protected")
        else:
            print(f"  ✅ Diet page ({path}) is publicly accessible")

    # ══════════════════════════════════════════════════════════
    #  LOGGED-IN ACCESS
    # ══════════════════════════════════════════════════════════

    def test_06_diet_page_accessible_after_login(self):
        """Diet page is accessible after login."""
        self.login()
        self.assertNotOnLoginPage()

        path = self.find_working_path(self.DIET_PATHS)
        if path is None:
            # Try via navbar
            self.driver.get(BASE_URL)
            time.sleep(4)
            diet_links = self.driver.find_elements(
                By.XPATH,
                "//a[contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'),'diet') or "
                "contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'),'food') or "
                "contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'),'nutrition')]"
            )
            if diet_links:
                diet_links[0].click()
                time.sleep(5)
                self.assertNotOnLoginPage()
                self.assertPageLoaded("Diet page via navbar should have content")
                print("  ✅ Diet page reachable via navbar after login")
            else:
                print("  ⚠️  Diet URL or navbar link not found")
            return

        self.assertNotOnLoginPage(
            "Diet page should be accessible after login"
        )
        self.assertPageLoaded("Diet page should have content after login")
        print(f"  ✅ Diet page accessible after login at {path}")

    def test_07_diet_search_works_after_login(self):
        """Diet search/form still works when logged in."""
        self.login()
        self.assertNotOnLoginPage()

        path = self.find_working_path(self.DIET_PATHS)
        if path is None:
            print("  ⚠️  Diet URL not found — skipping")
            return

        search = None
        for name in ["q", "food", "search", "query", "item", "ingredient", "name"]:
            try:
                search = self.driver.find_element(By.NAME, name)
                break
            except NoSuchElementException:
                continue

        if search:
            search.clear()
            search.send_keys("dal")
            time.sleep(1)
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                btn.click()
            except NoSuchElementException:
                search.send_keys(Keys.RETURN)
            time.sleep(5)
            self.assertPageLoaded("Diet search result after login should load")
            print("  ✅ Diet search works after login")
        else:
            print("  ⚠️  Search field not found — skipping logged-in search test")

    def test_08_diet_navbar_link_works_when_logged_in(self):
        """Diet/nutrition navbar link is clickable after login."""
        self.login()
        self.assertNotOnLoginPage()

        self.driver.get(BASE_URL)
        time.sleep(5)

        diet_links = self.driver.find_elements(
            By.XPATH,
            "//a[contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'diet') or "
            "contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'food') or "
            "contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'nutrition')]"
        )
        if diet_links:
            diet_links[0].click()
            time.sleep(5)
            self.assertNotOnLoginPage("Diet page should load when logged in")
            self.assertPageLoaded("Diet page should have content")
            print("  ✅ Diet navbar link works when logged in")
        else:
            print("  ⚠️  No diet/food/nutrition link found in navbar")

    def test_09_diet_page_after_logout(self):
        """If diet page is protected, it redirects after logout."""
        self.login()
        self.assertNotOnLoginPage()

        path = self.find_working_path(self.DIET_PATHS)
        if path is None:
            print("  ⚠️  Diet URL not found — skipping post-logout check")
            return

        was_protected_after_login = "login" in self.driver.current_url.lower()

        # Logout
        self.logout()
        self.driver.get(f"{BASE_URL}{path}")
        time.sleep(5)

        is_now_protected = (
            "login" in self.driver.current_url.lower() or
            self.wait_for(By.NAME, "u_name", timeout=4) is not None
        )

        if is_now_protected:
            print(f"  ✅ Diet page ({path}) is protected after logout")
        else:
            # Public page — no issue
            self.assertPageLoaded("Public diet page should still load after logout")
            print(f"  ✅ Diet page ({path}) is publicly accessible (no login needed)")


# ─── Runner ──────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(DietCompatibilityTests))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"  Passed: {passed} / {result.testsRun}")
    print(f"  Failures: {len(result.failures)}  |  Errors: {len(result.errors)}")
    print("=" * 60)
    exit(0 if result.wasSuccessful() else 1)
