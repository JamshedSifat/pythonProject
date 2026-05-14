from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    ROLE_CHOICES = (
        ('User', 'User'),
        ('Doctor', 'Doctor'),
    )

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='User'
    )

    age = models.IntegerField(default=0, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, default='')
    mobile = models.CharField(max_length=15, blank=True, default='')

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='Male'
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return self.user.username