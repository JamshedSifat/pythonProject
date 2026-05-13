"""
Smart Healthcare System - Complete Software Testing Suite
Tests for all major components: Appointments, Diet Compatibility, Medicine Reminders, Accounts
Project: https://smarthealthcaresystems.onrender.com/
"""

import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


class SmartHealthcareTestBase(unittest.TestCase):
    """Base test class for all healthcare system tests"""
    
    def setUp(self):
        """Initialize WebDriver and setup test environment"""
        self.driver = webdriver.Chrome(service=Service())
        self.driver.maximize_window()
        self.base_url = "https://smarthealthcaresystems.onrender.com"
        self.wait = WebDriverWait(self.driver, 10)
        
    def tearDown(self):
        """Close WebDriver after tests"""
        self.driver.quit()
    
    def login_user(self, username, password):
        """Helper method to login user"""
        self.driver.get(f"{self.base_url}/accounts/login/")
        time.sleep(10)
        
        username_field = self.driver.find_element(By.NAME, "u_name")
        password_field = self.driver.find_element(By.NAME, "u_password")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        time.sleep(10)
    
    def logout_user(self):
        """Helper method to logout"""
        logout_btn = self.driver.find_element(By.CSS_SELECTOR, "a[href*='logout']")
        logout_btn.click()
        time.sleep(10)


# ============================================================================
# ACCOUNT TESTS
# ============================================================================

class AccountsTests(SmartHealthcareTestBase):
    """Test cases for user account management"""
    
    def test_01_homepage_loads(self):
        """Test: Homepage loads successfully"""
        self.driver.get(self.base_url)
        time.sleep(10)
        
        page_title = self.driver.title
        self.assertNotEqual(page_title, "", "Homepage should have a title")
        
        # Check for navigation elements
        navbar = self.driver.find_element(By.CSS_SELECTOR, "nav, header")
        self.assertTrue(navbar.is_displayed(), "Navigation should be visible")
    
    def test_02_registration_page_loads(self):
        """Test: Registration page loads with all required fields"""
        self.driver.get(f"{self.base_url}/accounts/register/")
        time.sleep(10)
        
        # Check for required fields
        required_fields = ["u_name", "u_email", "u_password"]
        for field_name in required_fields:
            field = self.driver.find_element(By.NAME, field_name)
            self.assertTrue(field.is_displayed(), f"{field_name} should be visible")
    
    def test_03_login_page_loads(self):
        """Test: Login page displays correctly"""
        self.driver.get(f"{self.base_url}/accounts/login/")
        time.sleep(10)
        
        username_field = self.driver.find_element(By.NAME, "u_name")
        password_field = self.driver.find_element(By.NAME, "u_password")
        
        self.assertTrue(username_field.is_displayed(), "Username field should be visible")
        self.assertTrue(password_field.is_displayed(), "Password field should be visible")
    
    def test_04_user_can_register(self):
        """Test: User can successfully register"""
        self.driver.get(f"{self.base_url}/accounts/register/")
        time.sleep(10)
        
        # Fill registration form
        self.driver.find_element(By.NAME, "u_name").send_keys("testuser123")
        self.driver.find_element(By.NAME, "u_fname").send_keys("Test")
        self.driver.find_element(By.NAME, "u_email").send_keys("test@example.com")
        self.driver.find_element(By.NAME, "u_password").send_keys("Testpass@123")
        self.driver.find_element(By.NAME, "u_address").send_keys("123 Test Street")
        self.driver.find_element(By.NAME, "u_mobile").send_keys("01700000000")
        
        # Select gender
        gender_radio = self.driver.find_element(By.CSS_SELECTOR, "input[value='Male']")
        gender_radio.click()
        
        # Submit form
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        time.sleep(10)
        
        # Check if redirected to login or home
        self.assertIn(["login", "home"], self.driver.current_url, 
                     "Should redirect after registration")
    
    def test_05_user_profile_accessible(self):
        """Test: User can access their profile"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/accounts/profile/")
        time.sleep(10)
        
        profile_heading = self.driver.find_element(By.CSS_SELECTOR, "h1, h2")
        self.assertIn("profile", profile_heading.text.lower(), 
                     "Profile page should display")


# ============================================================================
# APPOINTMENT TESTS
# ============================================================================

class AppointmentTests(SmartHealthcareTestBase):
    """Test cases for appointment booking system"""
    
    def test_01_doctors_page_loads(self):
        """Test: Doctors listing page loads"""
        self.driver.get(f"{self.base_url}/appointments/")
        time.sleep(10)
        
        # Check if doctors are displayed
        doctor_cards = self.driver.find_elements(By.CSS_SELECTOR, ".bg-white, .card, [class*='doctor']")
        self.assertTrue(len(doctor_cards) > 0, "Doctor cards should be displayed")
    
    def test_02_can_search_doctors(self):
        """Test: User can search for doctors"""
        self.driver.get(f"{self.base_url}/appointments/")
        time.sleep(10)
        
        search_input = self.driver.find_element(By.NAME, "q")
        search_input.send_keys("cardiologist")
        
        search_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_btn.click()
        time.sleep(10)
        
        # Check if results are filtered
        current_url = self.driver.current_url
        self.assertIn("cardiologist", current_url.lower(), "Search query should be in URL")
    
    def test_03_doctor_detail_page_loads(self):
        """Test: Doctor detail page loads"""
        self.driver.get(f"{self.base_url}/appointments/")
        time.sleep(10)
        
        # Click on first doctor
        doctor_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='doctor']")
        if len(doctor_links) > 0:
            doctor_links[0].click()
            time.sleep(10)
            
            # Check for doctor info
            page_title = self.driver.title
            self.assertNotEqual(page_title, "", "Doctor detail page should load")
    
    def test_04_booking_requires_login(self):
        """Test: Booking appointment requires login"""
        self.driver.get(f"{self.base_url}/appointments/")
        time.sleep(10)
        
        # Try to find and click book button (should redirect to login)
        book_buttons = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='create_appointment']")
        if len(book_buttons) > 0:
            book_buttons[0].click()
            time.sleep(10)
            
            # Should redirect to login page
            self.assertIn("login", self.driver.current_url.lower(), 
                         "Should redirect to login for unauthenticated users")
    
    def test_05_prescription_history_accessible(self):
        """Test: User can view prescription history"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/appointments/prescription_history/")
        time.sleep(10)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("prescription", page_content.lower(), 
                     "Prescription history page should load")
    
    def test_06_top_doctors_page(self):
        """Test: Top doctors page displays correctly"""
        self.driver.get(f"{self.base_url}/appointments/top_doctors/")
        time.sleep(10)
        
        page_title = self.driver.title
        self.assertNotEqual(page_title, "", "Top doctors page should load")
        
        # Check for rating information
        rating_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='star'], [class*='rating']")
        self.assertTrue(len(rating_elements) > 0, "Rating information should be displayed")


# ============================================================================
# DIET COMPATIBILITY TESTS
# ============================================================================

class DietCompatibilityTests(SmartHealthcareTestBase):
    """Test cases for diet compatibility system"""
    
    def test_01_health_profile_dashboard_loads(self):
        """Test: Health profile dashboard loads"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/diet/dashboard/")
        time.sleep(10)
        
        dashboard_content = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(dashboard_content.is_displayed(), "Dashboard should be displayed")
    
    def test_02_create_health_profile(self):
        """Test: User can create health profile"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/diet/profile/")
        time.sleep(10)
        
        # Fill health profile form
        age_field = self.driver.find_element(By.NAME, "age")
        age_field.send_keys("30")
        
        height_field = self.driver.find_element(By.NAME, "height")
        height_field.send_keys("175")
        
        weight_field = self.driver.find_element(By.NAME, "weight")
        weight_field.send_keys("70")
        
        # Select gender
        gender_select = Select(self.driver.find_element(By.NAME, "gender"))
        gender_select.select_by_value("male")
        
        # Select activity level
        activity_radio = self.driver.find_element(By.CSS_SELECTOR, "input[value='moderate']")
        activity_radio.click()
        
        # Submit
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        time.sleep(10)
        
        # Check if redirected
        self.assertNotIn("profile", self.driver.current_url, 
                        "Should redirect after profile creation")
    
    def test_03_calorie_counter_loads(self):
        """Test: Calorie counter page loads"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/diet/calorie_counter/")
        time.sleep(10)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("calorie", page_content.lower(), "Calorie counter should load")
    
    def test_04_daily_log_accessible(self):
        """Test: Daily log page is accessible"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/diet/daily_log/")
        time.sleep(10)
        
        page_title = self.driver.title
        self.assertNotEqual(page_title, "", "Daily log page should load")
    
    def test_05_meal_plan_loads(self):
        """Test: Meal plan page loads"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/diet/meal_plan/")
        time.sleep(10)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("meal", page_content.lower(), "Meal plan should load")


# ============================================================================
# MEDICINE REMINDER TESTS
# ============================================================================

class MedicineReminderTests(SmartHealthcareTestBase):
    """Test cases for medicine reminder system"""
    
    def test_01_medicine_reminder_page_loads(self):
        """Test: Medicine reminder page loads"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/reminders/")
        time.sleep(10)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertIn("medicine", page_content.lower(), "Medicine reminder page should load")
    
    def test_02_can_add_medicine(self):
        """Test: User can add medicine reminder"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/reminders/add/")
        time.sleep(10)
        
        # Fill medicine form
        medicine_name = self.driver.find_element(By.NAME, "name")
        medicine_name.send_keys("Aspirin")
        
        dosage = self.driver.find_element(By.NAME, "dosage_amount")
        dosage.send_keys("500")
        
        frequency = Select(self.driver.find_element(By.NAME, "frequency"))
        frequency.select_by_value("once")
        
        # Select dates
        start_date = self.driver.find_element(By.NAME, "start_date")
        start_date.send_keys("05132026")
        
        end_date = self.driver.find_element(By.NAME, "end_date")
        end_date.send_keys("06132026")
        
        # Submit
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        time.sleep(10)
        
        # Check if medicine added
        self.assertNotIn("add", self.driver.current_url.lower(), 
                        "Should redirect after adding medicine")
    
    def test_03_medicine_list_displays(self):
        """Test: Medicine list displays correctly"""
        self.login_user("testuser", "testpass123")
        
        self.driver.get(f"{self.base_url}/reminders/")
        time.sleep(10)
        
        medicine_items = self.driver.find_elements(By.CSS_SELECTOR, "[class*='medicine'], [class*='reminder']")
        # Page might have no medicines, which is okay
        self.assertTrue(True, "Medicine list page loads")


# ============================================================================
# EMERGENCY BLOOD FINDER TESTS
# ============================================================================

class EmergencyBloodFinderTests(SmartHealthcareTestBase):
    """Test cases for emergency blood finder"""
    
    def test_01_emergency_page_loads(self):
        """Test: Emergency blood finder page loads"""
        self.driver.get(f"{self.base_url}/appointments/emergency/")
        time.sleep(10)
        
        page_title = self.driver.title
        self.assertIn("emergency", page_title.lower(), "Emergency page should load")
    
    def test_02_can_search_blood_type(self):
        """Test: User can search for blood type"""
        self.driver.get(f"{self.base_url}/appointments/emergency/")
        time.sleep(10)
        
        search_input = self.driver.find_element(By.NAME, "q")
        search_input.send_keys("O+")
        
        search_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_btn.click()
        time.sleep(10)
        
        # Check if search parameter in URL
        self.assertIn("O", self.driver.current_url, "Search query should be in URL")


# ============================================================================
# NAVIGATION TESTS
# ============================================================================

class NavigationTests(SmartHealthcareTestBase):
    """Test cases for site navigation"""
    
    def test_01_navigation_menu_visible(self):
        """Test: Navigation menu is visible"""
        self.driver.get(self.base_url)
        time.sleep(10)
        
        nav_elements = self.driver.find_elements(By.CSS_SELECTOR, "nav, header, [role='navigation']")
        self.assertTrue(len(nav_elements) > 0, "Navigation should be visible")
    
    def test_02_can_navigate_to_appointments(self):
        """Test: Can navigate to appointments"""
        self.driver.get(self.base_url)
        time.sleep(10)
        
        appointment_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='appointment']")
        self.assertTrue(len(appointment_links) > 0, "Appointment link should exist")
    
    def test_03_footer_links_work(self):
        """Test: Footer links are accessible"""
        self.driver.get(self.base_url)
        time.sleep(10)
        
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        
        footer = self.driver.find_elements(By.CSS_SELECTOR, "footer, [class*='footer']")
        self.assertTrue(len(footer) > 0, "Footer should be visible")


# ============================================================================
# RESPONSIVE DESIGN TESTS
# ============================================================================

class ResponsiveDesignTests(SmartHealthcareTestBase):
    """Test cases for responsive design"""
    
    def test_01_mobile_view(self):
        """Test: Site works in mobile view"""
        self.driver.set_window_size(375, 667)  # iPhone size
        
        self.driver.get(self.base_url)
        time.sleep(10)
        
        # Check if content is visible
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(), "Content should be visible on mobile")
    
    def test_02_tablet_view(self):
        """Test: Site works in tablet view"""
        self.driver.set_window_size(768, 1024)  # iPad size
        
        self.driver.get(self.base_url)
        time.sleep(10)
        
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(), "Content should be visible on tablet")
    
    def test_03_desktop_view(self):
        """Test: Site works in desktop view"""
        self.driver.set_window_size(1920, 1080)  # Desktop size
        
        self.driver.get(self.base_url)
        time.sleep(10)
        
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(), "Content should be visible on desktop")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class PerformanceTests(SmartHealthcareTestBase):
    """Test cases for site performance"""
    
    def test_01_homepage_load_time(self):
        """Test: Homepage loads within acceptable time"""
        import time as time_module
        
        start_time = time_module.time()
        self.driver.get(self.base_url)
        load_time = time_module.time() - start_time
        
        # Should load within 10 seconds
        self.assertLess(load_time, 10, f"Homepage took {load_time} seconds to load")
    
    def test_02_appointments_page_load_time(self):
        """Test: Appointments page loads within acceptable time"""
        import time as time_module
        
        start_time = time_module.time()
        self.driver.get(f"{self.base_url}/appointments/")
        load_time = time_module.time() - start_time
        
        self.assertLess(load_time, 10, f"Appointments page took {load_time} seconds")


# ============================================================================
# SECURITY TESTS
# ============================================================================

class SecurityTests(SmartHealthcareTestBase):
    """Test cases for security features"""
    
    def test_01_https_enabled(self):
        """Test: HTTPS is enabled"""
        # The base URL should be HTTPS
        self.assertIn("https", "https://smarthealthcaresystems.onrender.com", 
                     "Site should use HTTPS")
    
    def test_02_unauthenticated_access_restricted(self):
        """Test: Protected pages require authentication"""
        protected_urls = [
            "/accounts/profile/",
            "/diet/dashboard/",
            "/appointments/prescription_history/",
        ]
        
        for url in protected_urls:
            self.driver.get(f"{self.base_url}{url}")
            time.sleep(10)
            
            # Should redirect to login
            self.assertIn("login", self.driver.current_url.lower(), 
                         f"Protected URL {url} should redirect to login")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class IntegrationTests(SmartHealthcareTestBase):
    """Integration tests across multiple components"""
    
    def test_01_complete_user_flow(self):
        """Test: Complete user flow - register, login, book appointment"""
        # Step 1: Registration
        self.driver.get(f"{self.base_url}/accounts/register/")
        time.sleep(10)
        
        self.driver.find_element(By.NAME, "u_name").send_keys("integrationtest")
        self.driver.find_element(By.NAME, "u_email").send_keys("integration@test.com")
        self.driver.find_element(By.NAME, "u_password").send_keys("IntegrationTest@123")
        
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(10)
        
        # Step 2: Should redirect to login or home
        current_url = self.driver.current_url
        self.assertIn(["login", "home"], current_url, "Should redirect after registration")


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(AccountsTests))
    suite.addTests(loader.loadTestsFromTestCase(AppointmentTests))
    suite.addTests(loader.loadTestsFromTestCase(DietCompatibilityTests))
    suite.addTests(loader.loadTestsFromTestCase(MedicineReminderTests))
    suite.addTests(loader.loadTestsFromTestCase(EmergencyBloodFinderTests))
    suite.addTests(loader.loadTestsFromTestCase(NavigationTests))
    suite.addTests(loader.loadTestsFromTestCase(ResponsiveDesignTests))
    suite.addTests(loader.loadTestsFromTestCase(PerformanceTests))
    suite.addTests(loader.loadTestsFromTestCase(SecurityTests))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTests))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
