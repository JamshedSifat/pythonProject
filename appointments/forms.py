from django import forms
from django.contrib.auth.models import User
from .models import DoctorReview, Prescription, Medicine

class DoctorMedicalInfoForm(forms.ModelForm):
    class Meta:
        from appointments.models import Doctor
        model = Doctor
        fields = ['specialty', 'cost', 'daily_max_patients', 'experience_years', 'qualification', 'bio', 'image']
        widgets = {
            'specialty': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}),
            'cost': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}),
            'daily_max_patients': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500', 'min': 1, 'max': 50}),
            'experience_years': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}),
            'qualification': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2 rounded-lg border focus:ring-2 focus:ring-blue-500'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border'}),
        }

class DoctorReviewForm(forms.ModelForm):
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

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'dosage', 'frequency', 'duration', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'Medicine name'}),
            'dosage': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'e.g., 500mg'}),
            'frequency': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'e.g., 2x daily'}),
            'duration': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'e.g., 10 days'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500', 'placeholder': 'Additional notes'}),
        }

class PrescriptionForm(forms.ModelForm):
    medicines = forms.ModelMultipleChoiceField(
        queryset=Medicine.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Select Medicines'
    )
    
    class Meta:
        model = Prescription
        fields = ['diagnosis', 'notes', 'prescription_image', 'doctor_signature']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter diagnosis...',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Additional instructions (optional)...',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
            'prescription_image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
            'doctor_signature': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
        }
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
            'diagnosis': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter diagnosis...', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional instructions...', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'}),
        }