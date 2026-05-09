from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-300'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-300'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-300'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'address', 'mobile', 'gender']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-300'}),
            'address': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-300'}),
            'mobile': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-300'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-300'}),
        }