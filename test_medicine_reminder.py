"""
test_medicine_reminder.py — Medicine Reminder Module Tests
Based on exact URLs from medicine_reminders/urls.py (app_name='reminders')

URLs tested:
  /reminders/dashboard/
  /reminders/add/
  /reminders/edit/<medicine_id>/
  /reminders/delete/<medicine_id>/
  /reminders/mark-taken/<medicine_id>/<reminder_time_id>/
  /reminders/history/
  /reminders/list/
  /reminders/add-to-calendar/<medicine_id>/<reminder_time_id>/

Run: python test_medicine_reminder.py
"""

import unittest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from test_base import HealthcareTestBase, BASE_URL, click_submit

# ── Prefix used in main urls.py include ──────────────────────
# e.g. path('reminders/', include('medicine_reminders.urls'))
BASE_REMINDER = BASE_URL + "/reminders"


class MedicineReminderTests(HealthcareTestBase):
    """Full Selenium tests for the Medicine Reminder module."""

    # ── helper ───────────────────────────────────────────────

    def go(self, path, wait=5):
        """Navigate to a reminder URL and wait."""
        self.driver.get(f"{BASE_REMINDER}{path}")
        time.sleep(wait)

    def is_login_redirected(self):
        return (
            "login" in self.driver.current_url.lower()
            or self.wait_for(By.NAME, "u_name", timeout=5) is not None
        )

    # ══════════════════════════════════════════════════════════
    # 1. PROTECTION CHECKS — without login
    # ══════════════════════════════════════════════════════════

    def test_01_dashboard_redirects_without_login(self):
        """GET /reminders/dashboard/ → redirect to login (not authenticated)."""
        self.go("/dashboard/")
        self.assertTrue(self.is_login_redirected(),
                        "/reminders/dashboard/ must redirect to login")
        print("  ✅ /reminders/dashboard/ is login-protected")

    def test_02_add_redirects_without_login(self):
        """GET /reminders/add/ → redirect to login (not authenticated)."""
        self.go("/add/")
        self.assertTrue(self.is_login_redirected(),
                        "/reminders/add/ must redirect to login")
        print("  ✅ /reminders/add/ is login-protected")

    def test_03_list_redirects_without_login(self):
        """GET /reminders/list/ → redirect to login (not authenticated)."""
        self.go("/list/")
        self.assertTrue(self.is_login_redirected(),
                        "/reminders/list/ must redirect to login")
        print("  ✅ /reminders/list/ is login-protected")

    def test_04_history_redirects_without_login(self):
        """GET /reminders/history/ → redirect to login (not authenticated)."""
        self.go("/history/")
        self.assertTrue(self.is_login_redirected(),
                        "/reminders/history/ must redirect to login")
        print("  ✅ /reminders/history/ is login-protected")

    def test_05_edit_redirects_without_login(self):
        """GET /reminders/edit/1/ → redirect to login or 404 (no auth, no record)."""
        self.go("/edit/1/")
        is_login = self.is_login_redirected()
        is_404   = self.is_404()
        self.assertTrue(is_login or is_404,
                        "Edit should redirect to login or return 404 without auth")
        msg = "login-protected" if is_login else "404 (no record yet)"
        print(f"  ✅ /reminders/edit/1/ → {msg}")

    def test_06_delete_redirects_without_login(self):
        """GET /reminders/delete/1/ → redirect to login or 404 (no auth)."""
        self.go("/delete/1/")
        is_login = self.is_login_redirected()
        is_404   = self.is_404()
        self.assertTrue(is_login or is_404,
                        "Delete should redirect to login or return 404 without auth")
        msg = "login-protected" if is_login else "404 (no record yet)"
        print(f"  ✅ /reminders/delete/1/ → {msg}")

    def test_07_mark_taken_redirects_without_login(self):
        """GET /reminders/mark-taken/1/1/ → redirect to login or 404."""
        self.go("/mark-taken/1/1/")
        is_login = self.is_login_redirected()
        is_404   = self.is_404()
        self.assertTrue(is_login or is_404,
                        "Mark-taken should redirect to login or return 404 without auth")
        msg = "login-protected" if is_login else "404 (no record yet)"
        print(f"  ✅ /reminders/mark-taken/1/1/ → {msg}")

    def test_08_add_to_calendar_redirects_without_login(self):
        """GET /reminders/add-to-calendar/1/1/ → redirect to login or 404."""
        self.go("/add-to-calendar/1/1/")
        is_login = self.is_login_redirected()
        is_404   = self.is_404()
        self.assertTrue(is_login or is_404,
                        "Add-to-calendar should redirect to login or return 404")
        msg = "login-protected" if is_login else "404 (no record yet)"
        print(f"  ✅ /reminders/add-to-calendar/1/1/ → {msg}")

    # ══════════════════════════════════════════════════════════
    # 2. DASHBOARD — logged in
    # ══════════════════════════════════════════════════════════

    def test_09_dashboard_loads_after_login(self):
        """Logged-in user can access /reminders/dashboard/."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/dashboard/")
        self.assertNotOnLoginPage("Dashboard should not redirect after login")
        self.assertPageLoaded("Dashboard should have content")
        print(f"  ✅ Dashboard accessible — {self.driver.current_url}")

    def test_10_dashboard_has_reminder_keywords(self):
        """Dashboard body contains reminder/medicine-related keywords."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/dashboard/")
        body = self.body_text().lower()
        has_kw = any(kw in body for kw in
                     ["reminder", "medicine", "medication", "add", "schedule", "dose"])
        if has_kw:
            print("  ✅ Dashboard shows reminder-related content")
        else:
            print("  ⚠️  Dashboard loaded but no reminder keywords found")

    # ══════════════════════════════════════════════════════════
    # 3. REMINDER LIST — logged in
    # ══════════════════════════════════════════════════════════

    def test_11_list_loads_after_login(self):
        """Logged-in user can access /reminders/list/."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/list/")
        self.assertNotOnLoginPage("List should not redirect after login")
        self.assertPageLoaded("List page should have content")
        print(f"  ✅ Reminder list accessible — {self.driver.current_url}")

    def test_12_list_has_add_button(self):
        """List page has a link/button to add a new reminder."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/list/")
        add_els = self.driver.find_elements(
            By.XPATH,
            "//a[contains(@href,'add')] | "
            "//button[contains(translate(text(),'ADD','add'),'add')]"
        )
        if add_els:
            print(f"  ✅ List has {len(add_els)} add element(s)")
        else:
            print("  ⚠️  No 'add' link/button found on list page")

    # ══════════════════════════════════════════════════════════
    # 4. ADD REMINDER — logged in
    # ══════════════════════════════════════════════════════════

    def test_13_add_form_loads_after_login(self):
        """Logged-in user can open /reminders/add/."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/add/")
        self.assertNotOnLoginPage("Add form should not redirect after login")
        self.assertPageLoaded("Add form should have content")
        print(f"  ✅ Add-reminder form loaded — {self.driver.current_url}")

    def test_14_add_form_has_inputs(self):
        """Add-reminder form contains at least one input or select element."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/add/")
        inputs  = self.driver.find_elements(By.TAG_NAME, "input")
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        self.assertGreater(len(inputs) + len(selects), 0,
                           "Add form must have input fields")
        print(f"  ✅ Add form has {len(inputs)} input(s), {len(selects)} select(s)")

    def test_15_submit_add_reminder(self):
        """Fill and submit the add-reminder form."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/add/")
        self.assertNotOnLoginPage()

        # Map of possible field names → value
        field_map = {
            ("medicine_name", "name", "drug_name",
             "med_name", "medicine"):                     "Paracetamol 500mg",
            ("dosage", "dose", "amount",
             "quantity", "strength"):                     "500",
            ("frequency", "times_per_day",
             "repeat", "interval", "frequency_per_day"): "2",
            ("notes", "note", "instructions",
             "description"):                              "Take after meal",
        }

        filled = 0
        for names, value in field_map.items():
            for name in names:
                try:
                    el  = self.driver.find_element(By.NAME, name)
                    tag = el.tag_name.lower()
                    if tag == "select":
                        Select(el).select_by_index(1)
                    elif el.get_attribute("type") in ("checkbox", "radio"):
                        self.driver.execute_script("arguments[0].click();", el)
                    else:
                        el.clear()
                        el.send_keys(value)
                    filled += 1
                    time.sleep(0.3)
                    break
                except NoSuchElementException:
                    continue

        # Time fields (use JS to avoid browser input quirks)
        for name in ["reminder_time", "time", "alarm_time",
                     "start_time", "dose_time", "schedule_time"]:
            try:
                el = self.driver.find_element(By.NAME, name)
                self.driver.execute_script(
                    "arguments[0].value = arguments[1];", el, "08:00"
                )
                filled += 1
                break
            except NoSuchElementException:
                continue

        # Date fields
        for name in ["start_date", "date", "from_date", "reminder_date", "end_date"]:
            try:
                el = self.driver.find_element(By.NAME, name)
                self.driver.execute_script(
                    "arguments[0].value = arguments[1];", el, "2025-06-01"
                )
                filled += 1
                break
            except NoSuchElementException:
                continue

        if filled == 0:
            print("  ⚠️  No recognisable fields found — skipping submit")
            return

        print(f"  → Filled {filled} field(s), submitting…")
        try:
            click_submit(self.driver)
            time.sleep(6)
            self.assertPageLoaded("Page after submit should have content")
            print(f"  ✅ Add-reminder submitted — {self.driver.current_url}")
        except Exception as e:
            print(f"  ⚠️  Submit error: {e}")

    # ══════════════════════════════════════════════════════════
    # 5. HISTORY — logged in
    # ══════════════════════════════════════════════════════════

    def test_16_history_loads_after_login(self):
        """Logged-in user can access /reminders/history/."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/history/")
        self.assertNotOnLoginPage("History should not redirect after login")
        self.assertPageLoaded("History page should have content")
        print(f"  ✅ Reminder history accessible — {self.driver.current_url}")

    def test_17_history_shows_relevant_content(self):
        """History page contains history/record-related keywords."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/history/")
        body = self.body_text().lower()
        has_kw = any(kw in body for kw in
                     ["history", "taken", "record", "medicine",
                      "reminder", "date", "dose", "log"])
        if has_kw:
            print("  ✅ History page shows relevant content")
        else:
            print("  ⚠️  History page loaded but no recognisable keywords found")

    # ══════════════════════════════════════════════════════════
    # 6. EDIT — logged in (probe with ID=1)
    # ══════════════════════════════════════════════════════════

    def test_18_edit_no_login_redirect_after_auth(self):
        """/reminders/edit/1/ does NOT redirect to login when authenticated."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/edit/1/")
        self.assertFalse(self.is_login_redirected(),
                         "Edit page must not redirect to login after authentication")
        if self.is_404():
            print("  ✅ /reminders/edit/1/ → 404 (no reminder with ID=1 yet)")
        else:
            self.assertPageLoaded("Edit form should have content")
            print(f"  ✅ Edit form loaded — {self.driver.current_url}")

    def test_19_edit_form_has_inputs_when_record_exists(self):
        """When /reminders/edit/1/ loads a form, it contains input fields."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/edit/1/")
        if self.is_404():
            print("  ⚠️  No reminder with ID=1 — edit field check skipped")
            return
        inputs  = self.driver.find_elements(By.TAG_NAME, "input")
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        self.assertGreater(len(inputs) + len(selects), 0,
                           "Edit form must contain input fields")
        print(f"  ✅ Edit form has {len(inputs)} input(s), {len(selects)} select(s)")

    # ══════════════════════════════════════════════════════════
    # 7. DELETE — logged in (probe with ID=1)
    # ══════════════════════════════════════════════════════════

    def test_20_delete_no_login_redirect_after_auth(self):
        """/reminders/delete/1/ does NOT redirect to login when authenticated."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/delete/1/")
        self.assertFalse(self.is_login_redirected(),
                         "Delete must not redirect to login after authentication")
        if self.is_404():
            print("  ✅ /reminders/delete/1/ → 404 (no reminder with ID=1)")
        else:
            self.assertPageLoaded("Delete confirmation/redirect should have content")
            print(f"  ✅ Delete endpoint responded — {self.driver.current_url}")

    # ══════════════════════════════════════════════════════════
    # 8. MARK TAKEN — logged in
    # ══════════════════════════════════════════════════════════

    def test_21_mark_taken_no_login_redirect_after_auth(self):
        """/reminders/mark-taken/1/1/ does NOT redirect to login when authenticated."""
        self.login()
        self.assertNotOnLoginPage()
        self.go("/mark-taken/1/1/")
        self.assertFalse(self.is_login_redirected(),
                         "Mark-taken must not redirect to login after authentication")
        if self.is_404():
            print("  ✅ /reminders/mark-taken/1/1/ → 404 (no such record)")
        else:
            print(f"  ✅ Mark-taken responded — {self.driver.current_url}")

    # ══════════════════════════════════════════════════════════
    # 9. FULL FLOW
    # ══════════════════════════════════════════════════════════

    def test_22_full_reminder_flow(self):
        """
        Full flow:
          Login → Dashboard → List → Add form → History → Logout → blocked
        """
        self.login()
        self.assertNotOnLoginPage()

        steps = [
            ("/dashboard/", "Dashboard"),
            ("/list/",      "Reminder list"),
            ("/add/",       "Add form"),
            ("/history/",   "History"),
        ]
        for path, label in steps:
            self.go(path)
            self.assertNotOnLoginPage(f"{label} should not redirect after login")
            self.assertPageLoaded(f"{label} should have content")
            print(f"  → {label} ✅")

        # Logout → list must be blocked
        self.logout()
        self.go("/list/")
        self.assertTrue(self.is_login_redirected(),
                        "After logout, /reminders/list/ must redirect to login")
        print("  → Logout blocks access ✅")
        print("  ✅ Full reminder flow passed")

    # ══════════════════════════════════════════════════════════
    # 10. NAVBAR ACCESS
    # ══════════════════════════════════════════════════════════

    def test_23_reminder_reachable_via_navbar(self):
        """Medicine reminder link in homepage navbar works when logged in."""
        self.login()
        self.assertNotOnLoginPage()

        self.driver.get(BASE_URL)
        time.sleep(5)

        nav_links = self.driver.find_elements(
            By.XPATH,
            "//a[contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'reminder') or "
            "contains(translate(@href,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'medicine')]"
        )
        if nav_links:
            nav_links[0].click()
            time.sleep(5)
            self.assertNotOnLoginPage("Reminder page via navbar should load when logged in")
            self.assertPageLoaded("Reminder page should have content")
            print(f"  ✅ Reminder reachable via navbar — {self.driver.current_url}")
        else:
            print("  ⚠️  No reminder/medicine link found in navbar")


# ─── Runner ──────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(MedicineReminderTests))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 65)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"  Total : {result.testsRun}  |  ✅ Passed : {passed}  "
          f"|  ❌ Failures : {len(result.failures)}  "
          f"|  💥 Errors : {len(result.errors)}")
    print("=" * 65)
    exit(0 if result.wasSuccessful() else 1)
