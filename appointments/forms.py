# appointments/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import DoctorReview, Prescription, Medicine
import json


class DoctorReviewForm(forms.ModelForm):
    """Doctor review form"""
    rating = forms.ChoiceField(
        choices=[(i, f'{i} - {"⭐" * i}') for i in range(1, 6)],
        widget=forms.RadioSelect,
        label='Rating'
    )
    
    class Meta:
        model = DoctorReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'maxlength': 1000,
                'placeholder': 'Share your experience...',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].required = False


class RescheduleForm(forms.Form):
    """Reschedule form"""
    new_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
        }),
        label='New Date'
    )
    
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'maxlength': 500,
            'placeholder': 'Reason for rescheduling (optional)',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
        }),
        label='Reason',
        required=False
    )


class MedicineForm(forms.ModelForm):
    """Medicine form"""
    class Meta:
        model = Medicine
        fields = ['name', 'dosage', 'frequency', 'duration', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Medicine name (e.g., Paracetamol)'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'e.g., 500mg'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'e.g., 2x daily'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'e.g., 10 days'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg',
                'placeholder': 'Additional notes (optional)'
            })
        }


class PrescriptionForm(forms.ModelForm):
    """Prescription form (Doctor only)"""
    medicines = forms.ModelMultipleChoiceField(
        queryset=Medicine.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Select Medicines'
    )
    
    class Meta:
        model = Prescription
        fields = ['diagnosis', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter diagnosis...',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Additional instructions (optional)...',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
            })
        }


class AppointmentForm(forms.Form):
    """Appointment form"""
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
        }),
        label='Appointment Date'
    )
    
    appointment_time = forms.IntegerField(
        widget=forms.Select(),
        label='Appointment Time'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'maxlength': 1000,
            'placeholder': 'Describe your problem...',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
        }),
        label='Problem Description'
    )
    
    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if doctor:
            self.fields['appointment_time'].widget = forms.Select(
                choices=[(slot.id, f"{slot.start_time} - {slot.end_time}")
                        for slot in doctor.time_slots.all()]
            )