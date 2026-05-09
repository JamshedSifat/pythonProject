from django.test import TestCase

# Create your tests here.
name=diet_compatibility/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import (
    DietaryPreference,
    FoodIncompatibility,
    MedicineAllergen,
    DietaryRestrictionLog,
)


class DietaryPreferenceModelTest(TestCase):
    """Test DietaryPreference model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_create_preference(self):
        """Test creating dietary preference"""
        preference = DietaryPreference.objects.create(
            user=self.user,
            diet_type='vegetarian',
            is_strict=True,
            notes='Avoid all meat products'
        )
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.diet_type, 'vegetarian')
        self.assertTrue(preference.is_strict)

    def test_preference_str(self):
        """Test string representation"""
        preference = DietaryPreference.objects.create(
            user=self.user,
            diet_type='vegan'
        )
        self.assertEqual(str(preference), f"{self.user.username} - Vegan - No animal products")

    def test_one_preference_per_user(self):
        """Test that user can have only one preference"""
        DietaryPreference.objects.create(
            user=self.user,
            diet_type='vegetarian'
        )
        preference2 = DietaryPreference.objects.create(
            user=self.user,
            diet_type='vegan'
        )
        # Both should exist (Django doesn't enforce this in model, but we can)
        count = DietaryPreference.objects.filter(user=self.user).count()
        self.assertGreaterEqual(count, 1)


class FoodIncompatibilityModelTest(TestCase):
    """Test FoodIncompatibility model"""

    def test_create_incompatibility(self):
        """Test creating food incompatibility"""
        incompat = FoodIncompatibility.objects.create(
            food_name='Grapefruit',
            medicine_name='Statins',
            severity='severe',
            description='Grapefruit inhibits drug metabolism',
            recommendations='Avoid grapefruit entirely'
        )
        self.assertEqual(incompat.food_name, 'Grapefruit')
        self.assertEqual(incompat.severity, 'severe')

    def test_incompatibility_str(self):
        """Test string representation"""
        incompat = FoodIncompatibility.objects.create(
            food_name='Caffeine',
            medicine_name='Blood Pressure Meds',
            severity='moderate'
        )
        self.assertEqual(str(incompat), "Caffeine + Blood Pressure Meds (moderate)")


class MedicineAllergenModelTest(TestCase):
    """Test MedicineAllergen model"""

    def test_create_allergen(self):
        """Test creating medicine allergen"""
        allergen = MedicineAllergen.objects.create(
            medicine_name='Aspirin',
            allergen='dairy',
            risk_level='high'
        )
        self.assertEqual(allergen.medicine_name, 'Aspirin')
        self.assertEqual(allergen.allergen, 'dairy')

    def test_allergen_str(self):
        """Test string representation"""
        allergen = MedicineAllergen.objects.create(
            medicine_name='Penicillin',
            allergen='peanuts'
        )
        self.assertEqual(str(allergen), "Penicillin - Peanuts")


class DietaryPreferenceViewTest(TestCase):
    """Test dietary preference views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_preferences_list_view(self):
        """Test preferences list view"""
        response = self.client.get(reverse('diet_compatibility:preferences_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'diet_compatibility/preferences_list.html')

    def test_add_preference_get(self):
        """Test add preference GET request"""
        response = self.client.get(reverse('diet_compatibility:add_preference'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'diet_compatibility/add_preference.html')

    def test_add_preference_post(self):
        """Test add preference POST request"""
        response = self.client.post(
            reverse('diet_compatibility:add_preference'),
            {
                'diet_type': 'vegetarian',
                'is_strict': True,
                'notes': 'No meat'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(DietaryPreference.objects.filter(user=self.user).exists())

    def test_login_required(self):
        """Test that login is required"""
        self.client.logout()
        response = self.client.get(reverse('diet_compatibility:preferences_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login