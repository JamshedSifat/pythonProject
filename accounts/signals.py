# accounts/signals.py - সম্পূর্ণ ফাইল প্রতিস্থাপন করুন

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """When a new user is created, create a UserProfile"""
    if created:
        # Check if profile already exists before creating
        if not UserProfile.objects.filter(user=instance).exists():
            UserProfile.objects.create(user=instance)
        else:
            print(f"Profile already exists for {instance.username}")


@receiver(post_save, sender=UserProfile)
def create_doctor_profile(sender, instance, created, **kwargs):
    """When a UserProfile with role='Doctor' is created, create a Doctor record"""
    if created and instance.role == 'Doctor':
        from appointments.models import Doctor
        # Check if doctor already exists
        if not Doctor.objects.filter(user=instance.user).exists():
            Doctor.objects.create(
                user=instance.user,
                name=f"Dr. {instance.user.get_full_name() or instance.user.username}",
                specialty='General Medicine',
                cost=500,
                available_spots=10,
                status=True,
                experience_years=0,
            )
        else:
            print(f"Doctor profile already exists for {instance.user.username}")