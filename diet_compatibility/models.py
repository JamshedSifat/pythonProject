# diet_compatibility/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============ DISEASE MODEL ============
class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    severity_level = models.CharField(
        max_length=20,
        choices=[('high', 'High'), ('low', 'Low'), ('medium', 'Medium')],
        default='high'
    )
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ============ FOOD MODEL ============
class Food(models.Model):
    CATEGORY_CHOICES = [
        ('carbohydrate','Carbohydrate'),
        ('protein','Protein'),
        ('vegetable', 'Vegetable'),
        ('fruit', 'Fruit'),
        ('meat', 'Meat'),
        ('fastFood','FastFood'),
        ('grain', 'Grain'),
        ('dairy', 'Dairy'),
        ('spice', 'Spice'),
        ('beverage', 'Beverage'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES,
        default='other'
    )
    calories_per_100g = models.IntegerField(default=0)
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)
    fat = models.FloatField(default=0.0)
    fiber = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.calories_per_100g} kcal/100g)"


# ============ DISEASE-FOOD RELATIONSHIP ============
class DiseaseFood(models.Model):
    STATUS_CHOICES = [
        ('recommended', 'Recommended'),
        ('avoid', 'Avoid'),
        ('limited', 'Limited Quantity'),
    ]
    
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='foods')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='recommended'
    )
    reason = models.TextField(default='')
    quantity_limit = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        unique_together = ('disease', 'food')
    
    def __str__(self):
        return f"{self.disease.name} - {self.food.name} ({self.status})"


# ============ MEDICINE MODEL ============
class Medicine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    generic_name = models.CharField(max_length=100, default='')
    purpose = models.CharField(max_length=200, default='')
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ============ MEDICINE-FOOD COMPATIBILITY ============
class MedicineFoodCompatibility(models.Model):
    INTERACTION_LEVEL = [
        ('safe', 'Safe'),
        ('caution', 'Use with Caution'),
        ('avoid', 'Avoid'),
    ]
    
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='food_interactions')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    interaction_level = models.CharField(
        max_length=20, 
        choices=INTERACTION_LEVEL,
        default='safe'
    )
    description = models.TextField(default='')
    recommendation = models.TextField(default='')
    
    class Meta:
        unique_together = ('medicine', 'food')
    
    def __str__(self):
        return f"{self.medicine.name} + {self.food.name} - {self.interaction_level}"


# ============ ALLERGY MODEL (Single Source of Truth) ============
class Allergy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='allergy_profile')
    foods = models.ManyToManyField(Food, related_name='allergic_users', blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Allergies"


# ============ USER HEALTH PROFILE ============
class HealthProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('light', 'Light Activity'),
        ('moderate', 'Moderate Activity'),
        ('active', 'Very Active'),
        ('very_active', 'Extremely Active'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile')
    age = models.IntegerField(default=25)
    height = models.FloatField(default=170.0)  # in cm
    weight = models.FloatField(default=70.0)  # in kg
    gender = models.CharField(
        max_length=20, 
        choices=GENDER_CHOICES,
        default='male'
    )
    blood_group = models.CharField(
        max_length=10, 
        choices=BLOOD_GROUP_CHOICES, 
        blank=True, 
        null=True
    )
    activity_level = models.CharField(
        max_length=20, 
        choices=ACTIVITY_LEVEL_CHOICES,
        default='moderate'
    )
    
    # Relations - Only diseases and medicines
    diseases = models.ManyToManyField(Disease, related_name='health_profiles', blank=True)
    medicines = models.ManyToManyField(Medicine, related_name='health_profiles', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Health Profile"
    
    def calculate_bmi(self):
        """BMI = weight(kg) / height(m)²"""
        height_m = self.height / 100
        if height_m == 0:
            return 0
        bmi = self.weight / (height_m ** 2)
        return round(bmi, 1)
    
    def get_bmi_category(self):
        """BMI category determination"""
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal Weight'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    def calculate_daily_calorie_need(self):
        """Calculate daily calorie requirement based on activity level"""
        # Harris-Benedict Formula
        if self.gender == 'male':
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * self.age)
        
        # Activity multiplier
        multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
        }
        
        tdee = bmr * multipliers.get(self.activity_level, 1.5)
        return int(tdee)
    
    def get_user_allergies(self):
        """Get user's allergies from Allergy model"""
        try:
            return self.user.allergy_profile.foods.all()
        except:
            return Food.objects.none()


# ============ MEAL PLAN ============
class MealPlan(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    meal_type = models.CharField(
        max_length=20, 
        choices=MEAL_TYPE_CHOICES,
        default='breakfast'
    )
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'meal_type', 'date')
        ordering = ['-date', 'meal_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.meal_type} - {self.date}"
    
    def get_total_calories(self):
        """Calculate total calories for this meal"""
        total = 0
        for meal_food in self.mealfood_set.all():
            total += meal_food.get_calories()
        return total
    
    def get_meal_type_display_short(self):
        """Get short display name"""
        return dict(self.MEAL_TYPE_CHOICES).get(self.meal_type, '')


# ============ MEAL-FOOD JUNCTION ============
class MealFood(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity_grams = models.IntegerField(default=100)  # in grams
    
    class Meta:
        ordering = ['meal_plan', 'food']
    
    def __str__(self):
        return f"{self.meal_plan} - {self.food.name} ({self.quantity_grams}g)"
    
    def get_calories(self):
        """Calculate calories for this portion"""
        if self.food.calories_per_100g == 0:
            return 0
        return (self.food.calories_per_100g * self.quantity_grams) / 100


# ============ DAILY LOG ============
class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField(default=timezone.now)
    water_intake_ml = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    def get_total_calories(self):
        """Get total calories for the day"""
        meals = MealPlan.objects.filter(user=self.user, date=self.date)
        return sum(meal.get_total_calories() for meal in meals)