from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'role',
        'age',
        'mobile',
        'gender'
    )

    list_filter = (
        'role',
        'gender'
    )

    search_fields = (
        'user__username',
        'user__email'
    )