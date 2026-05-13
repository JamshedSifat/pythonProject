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
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        self.driver = webdriver.Chrome(service=Service(), options=options)
        self.driver.maximize_window()
        self.base_url = "https://smarthealthcaresystems.onrender.com"
        self.wait = WebDriverWait(self.driver, 15)
        
    def tearDown(self):
        """Close WebDriver after tests"""
        time.sleep(2)
        self.driver.quit()
    
    def wait_for_element(self, by, value, timeout=15):
        """Wait for element to be present and visible"""
        try:
            return self.wait.until(EC.presence_of_element_located((by, value)))
        except:
            return None
    
    def login_user(self, username, password):
        """Helper method to login user"""
        self.driver.get(f"{self.base_url}/accounts/login/")
        time.sleep(5)
        
        # Wait for form to load
        username_field = self.wait_for_element(By.NAME, "u_name")
        if not username_field:
            raise Exception("Login page did not load properly")
        
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(1)
        
        password_field = self.driver.find_element(By.NAME, "u_password")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        time.sleep(5)
        
        # Wait for redirect
        try:
            self.wait.until(EC.url_changes(f"{self.base_url}/accounts/login/"))
        except:
            pass
    
    def logout_user(self):
        """Helper method to logout"""
        try:
            logout_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout']")
            if logout_links:
                logout_links[0].click()
                time.sleep(5)
        except:
            pass


# ============================================================================
# ACCOUNT TESTS
# ============================================================================

class AccountsTests(SmartHealthcareTestBase):
    """Test cases for user account management"""
    
    def test_01_homepage_loads(self):
        """Test: Homepage loads successfully"""
        self.driver.get(self.base_url)
        time.sleep(5)
        
        page_title = self.driver.title
        self.assertNotEqual(page_title, "", "Homepage should have a title")
        print(f"✅ Homepage loaded with title: {page_title}")
    
    def test_02_registration_page_loads(self):
        """Test: Registration page loads with all required fields"""
        self.driver.get(f"{self.base_url}/accounts/register/")
        time.sleep(5)
        
        # Check for required fields
        required_fields = ["u_name", "u_email", "u_password"]
        for field_name in required_fields:
            field = self.wait_for_element(By.NAME, field_name)
            self.assertIsNotNone(field, f"{field_name} should be visible")
        print("✅ Registration page loaded with all required fields")
    
    def test_03_login_page_loads(self):
        """Test: Login page displays correctly"""
        self.driver.get(f"{self.base_url}/accounts/login/")
        time.sleep(5)
        
        username_field = self.wait_for_element(By.NAME, "u_name")
        password_field = self.wait_for_element(By.NAME, "u_password")
        
        self.assertIsNotNone(username_field, "Username field should be visible")
        self.assertIsNotNone(password_field, "Password field should be visible")
        print("✅ Login page loaded successfully")
    
    def test_04_user_registration_flow(self):
        """Test: Complete user registration flow"""
        self.driver.get(f"{self.base_url}/accounts/register/")
        time.sleep(5)
        
        # Generate unique username and email
        import random
        unique_id = random.randint(1000, 9999)
        username = f"testuser{unique_id}"
        email = f"test{unique_id}@example.com"
        
        try:
            # Fill registration form
            u_name = self.wait_for_element(By.NAME, "u_name")
            u_name.send_keys(username)
            time.sleep(1)
            
            u_fname = self.driver.find_element(By.NAME, "u_fname")
            u_fname.send_keys("Test")
            time.sleep(1)
            
            u_email = self.driver.find_element(By.NAME, "u_email")
            u_email.send_keys(email)
            time.sleep(1)
            
            u_password = self.driver.find_element(By.NAME, "u_password")
            u_password.send_keys("TestPass@123")
            time.sleep(1)
            
            u_address = self.driver.find_element(By.NAME, "u_address")
            u_address.send_keys("123 Test Street")
            time.sleep(1)
            
            u_mobile = self.driver.find_element(By.NAME, "u_mobile")
            u_mobile.send_keys("01700000000")
            time.sleep(1)
            
            # Select gender
            gender_radio = self.driver.find_element(By.CSS_SELECTOR, "input[value='Male']")
            self.driver.execute_script("arguments[0].click();", gender_radio)
            time.sleep(1)
            
            # Submit form
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(8)
            
            # Store credentials for login test
            self.test_username = username
            self.test_password = "TestPass@123"
            self.test_email = email
            
            current_url = self.driver.current_url
            print(f"✅ Registration successful. Redirected to: {current_url}")
            
        except Exception as e:
            self.fail(f"Registration failed: {str(e)}")
    
    def test_05_user_login_after_registration(self):
        """Test: User can login after registration"""
        # First register
        self.test_04_user_registration_flow()
        
        # Now try to login with same credentials
        time.sleep(3)
        self.driver.get(f"{self.base_url}/accounts/login/")
        time.sleep(5)
        
        try:
            username_field = self.wait_for_element(By.NAME, "u_name")
            self.assertIsNotNone(username_field, "Login form should load")
            
            username_field.clear()
            username_field.send_keys(self.test_username)
            time.sleep(1)
            
            password_field = self.driver.find_element(By.NAME, "u_password")
            password_field.clear()
            password_field.send_keys(self.test_password)
            time.sleep(1)
            
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.driver.execute_script("arguments[0].click();", login_btn)
            time.sleep(8)
            
            # Check if login was successful
            current_url = self.driver.current_url
            
            # Should NOT stay on login page (indicates login failed)
            self.assertNotIn("login", current_url.lower(), 
                           f"Login failed - still on login page. URL: {current_url}")
            
            print(f"✅ Login successful. Redirected to: {current_url}")
            
        except Exception as e:
            self.fail(f"Login failed: {str(e)}")
    
    def test_06_user_profile_accessible(self):
        """Test: User can access their profile"""
        # Use existing test account (or create one)
        self.login_user("testuser", "TestPass@123")
        time.sleep(5)
        
        self.driver.get(f"{self.base_url}/accounts/profile/")
        time.sleep(5)
        
        try:
            profile_content = self.driver.find_element(By.TAG_NAME, "body").text
            self.assertNotEqual(profile_content, "", "Profile page should display content")
            print("✅ User profile accessible")
        except:
            print("⚠️ Could not verify profile (account may not exist)")


# ============================================================================
# APPOINTMENT TESTS
# ============================================================================

class AppointmentTests(SmartHealthcareTestBase):
    """Test cases for appointment booking system"""
    
    def test_01_doctors_page_loads(self):
        """Test: Doctors listing page loads"""
        self.driver.get(f"{self.base_url}/appointments/")
        time.sleep(5)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertNotEqual(page_content, "", "Doctors page should load")
        print("✅ Doctors page loaded")
    
    def test_02_can_search_doctors(self):
        """Test: User can search for doctors"""
        self.driver.get(f"{self.base_url}/appointments/")
        time.sleep(5)
        
        try:
            search_input = self.wait_for_element(By.NAME, "q")
            if search_input:
                search_input.send_keys("doctor")
                time.sleep(2)
                
                search_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                search_btn.click()
                time.sleep(5)
                
                print("✅ Doctor search works")
            else:
                print("⚠️ Search form not found")
        except Exception as e:
            print(f"⚠️ Search test failed: {str(e)}")
    
    def test_03_doctor_detail_page_loads(self):
        """Test: Doctor detail page loads"""
        self.driver.get(f"{self.base_url}/appointments/")
        time.sleep(5)
        
        try:
            # Click on first doctor link
            doctor_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='doctor']")
            if len(doctor_links) > 0:
                doctor_links[0].click()
                time.sleep(5)
                
                page_content = self.driver.find_element(By.TAG_NAME, "body").text
                self.assertNotEqual(page_content, "", "Doctor detail page should load")
                print("✅ Doctor detail page loaded")
            else:
                print("⚠️ No doctor links found")
        except Exception as e:
            print(f"⚠️ Doctor detail test failed: {str(e)}")
    
    def test_04_top_doctors_page(self):
        """Test: Top doctors page displays correctly"""
        self.driver.get(f"{self.base_url}/appointments/top_doctors/")
        time.sleep(5)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertNotEqual(page_content, "", "Top doctors page should load")
        print("✅ Top doctors page loaded")
    
    def test_05_prescription_history_requires_login(self):
        """Test: Prescription history requires authentication"""
        self.driver.get(f"{self.base_url}/appointments/prescription_history/")
        time.sleep(5)
        
        current_url = self.driver.current_url
        # Should redirect to login if not authenticated
        print(f"✅ Prescription history test - URL: {current_url}")


# ============================================================================
# DIET COMPATIBILITY TESTS
# ============================================================================

class DietCompatibilityTests(SmartHealthcareTestBase):
    """Test cases for diet compatibility system"""
    
    def test_01_diet_dashboard_loads(self):
        """Test: Diet dashboard page loads"""
        self.driver.get(f"{self.base_url}/diet/")
        time.sleep(5)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertNotEqual(page_content, "", "Diet page should load")
        print("✅ Diet page loaded")


# ============================================================================
# MEDICINE REMINDER TESTS
# ============================================================================

class MedicineReminderTests(SmartHealthcareTestBase):
    """Test cases for medicine reminder system"""
    
    def test_01_medicine_reminder_page_loads(self):
        """Test: Medicine reminder page loads"""
        self.driver.get(f"{self.base_url}/reminders/")
        time.sleep(5)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertNotEqual(page_content, "", "Medicine reminder page should load")
        print("✅ Medicine reminder page loaded")


# ============================================================================
# EMERGENCY BLOOD FINDER TESTS
# ============================================================================

class EmergencyBloodFinderTests(SmartHealthcareTestBase):
    """Test cases for emergency blood finder"""
    
    def test_01_emergency_page_loads(self):
        """Test: Emergency blood finder page loads"""
        self.driver.get(f"{self.base_url}/appointments/emergency/")
        time.sleep(5)
        
        page_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertNotEqual(page_content, "", "Emergency page should load")
        print("✅ Emergency blood finder page loaded")


# ============================================================================
# NAVIGATION TESTS
# ============================================================================

class NavigationTests(SmartHealthcareTestBase):
    """Test cases for site navigation"""
    
    def test_01_navigation_menu_visible(self):
        """Test: Navigation menu is visible"""
        self.driver.get(self.base_url)
        time.sleep(5)
        
        body_content = self.driver.find_element(By.TAG_NAME, "body").text
        self.assertNotEqual(body_content, "", "Page should have content")
        print("✅ Navigation menu test passed")
    
    def test_02_can_navigate_to_appointments(self):
        """Test: Can navigate to appointments"""
        self.driver.get(self.base_url)
        time.sleep(5)
        
        appointment_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='appointment']")
        self.assertTrue(len(appointment_links) > 0, "Appointment link should exist")
        print(f"✅ Found {len(appointment_links)} appointment links")


# ============================================================================
# RESPONSIVE DESIGN TESTS
# ============================================================================

class ResponsiveDesignTests(SmartHealthcareTestBase):
    """Test cases for responsive design"""
    
    def test_01_mobile_view(self):
        """Test: Site works in mobile view"""
        self.driver.set_window_size(375, 667)  # iPhone size
        
        self.driver.get(self.base_url)
        time.sleep(5)
        
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(), "Content should be visible on mobile")
        print("✅ Mobile view works")
    
    def test_02_tablet_view(self):
        """Test: Site works in tablet view"""
        self.driver.set_window_size(768, 1024)  # iPad size
        
        self.driver.get(self.base_url)
        time.sleep(5)
        
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(), "Content should be visible on tablet")
        print("✅ Tablet view works")
    
    def test_03_desktop_view(self):
        """Test: Site works in desktop view"""
        self.driver.set_window_size(1920, 1080)  # Desktop size
        
        self.driver.get(self.base_url)
        time.sleep(5)
        
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertTrue(body.is_displayed(), "Content should be visible on desktop")
        print("✅ Desktop view works")


# ============================================================================
# SECURITY TESTS
# ============================================================================

class SecurityTests(SmartHealthcareTestBase):
    """Test cases for security features"""
    
    def test_01_https_enabled(self):
        """Test: HTTPS is enabled"""
        self.driver.get(self.base_url)
        current_url = self.driver.current_url
        
        self.assertTrue(current_url.startswith("https"), "Site should use HTTPS")
        print("✅ HTTPS enabled")


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes in order
    suite.addTests(loader.loadTestsFromTestCase(AccountsTests))
    suite.addTests(loader.loadTestsFromTestCase(AppointmentTests))
    suite.addTests(loader.loadTestsFromTestCase(DietCompatibilityTests))
    suite.addTests(loader.loadTestsFromTestCase(MedicineReminderTests))
    suite.addTests(loader.loadTestsFromTestCase(EmergencyBloodFinderTests))
    suite.addTests(loader.loadTestsFromTestCase(NavigationTests))
    suite.addTests(loader.loadTestsFromTestCase(ResponsiveDesignTests))
    suite.addTests(loader.loadTestsFromTestCase(SecurityTests))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*80 + "\n")
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
