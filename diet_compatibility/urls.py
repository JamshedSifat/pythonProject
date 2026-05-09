# diet_compatibility/urls.py

from django.urls import path
from . import views

app_name = 'diet_compatibility'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.health_dashboard, name='health_profile_dashboard'),
    
    # Profile
    path('profile/create/', views.create_health_profile, name='create_health_profile'),
    path('profile/edit/', views.edit_health_profile, name='edit_health_profile'),
    
    # Disease-based diet
    path('disease-diet/', views.disease_diet_suggestion, name='disease_diet'),
    path('disease-diet/<int:disease_id>/', views.disease_detail, name='disease_detail'),
    
    # Medicine-food compatibility
    path('medicine-compatibility/', views.medicine_compatibility, name='medicine_compatibility'),
    path('medicine-compatibility/<int:medicine_id>/', views.medicine_detail, name='medicine_detail'),
    
    # Meal Planning
    path('meal-plan/', views.meal_plan, name='meal_plan'),
    path('meal-plan/create/', views.create_meal, name='create_meal'),
    path('meal-plan/delete/<int:meal_id>/', views.delete_meal, name='delete_meal'),
    
    # Daily Log
    path('daily-log/', views.daily_log, name='daily_log'),
    path('daily-log/update/', views.update_daily_log, name='update_daily_log'),
    
    # Calorie Counter
    path('calorie-counter/', views.calorie_counter, name='calorie_counter'),
    
    # Diet Compatibility
    path('diet-compatibility/', views.diet_compatibility, name='diet_compatibility'),
    
    # Allergy Management
    path('allergies/', views.manage_allergies, name='manage_allergies'),
    
    # Health Recommendations
    path('recommendations/', views.get_recommendations, name='recommendations'),
]