from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """User profile model to store additional user information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(default=0, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, default='')
    mobile = models.CharField(max_length=15, blank=True, default='')
    
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']

    def __str__(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name or self.user.username

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
