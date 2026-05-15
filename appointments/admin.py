# appointments/admin.py

from django.contrib import admin
from .models import Doctor, DoctorReview, DoctorTimeSlot, Appointment, Prescription, Hospital, Blood, Medicine, PatientMedicalHistory, VitalSign, DoctorHoliday


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialty', 'daily_max_patients', 'cost', 'status', 'average_rating']  # available_spots -> daily_max_patients
    list_filter = ['specialty', 'status', 'created_at']
    search_fields = ['name', 'specialty', 'qualification']
    list_editable = ['daily_max_patients', 'cost', 'status']  # available_spots -> daily_max_patients
    readonly_fields = ['average_rating', 'total_reviews', 'created_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'name', 'specialty', 'experience_years', 'qualification', 'bio', 'image')
        }),
        ('Practice Settings', {
            'fields': ('cost', 'daily_max_patients', 'status'),  # available_spots -> daily_max_patients
            'description': 'Set your consultation fee and daily patient capacity'
        }),
        ('Ratings', {
            'fields': ('average_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['name', 'dosage', 'frequency', 'duration', 'created_at']
    list_filter = ['created_at', 'frequency']
    search_fields = ['name', 'dosage']


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'user', 'rating', 'created_at']
    list_filter = ['doctor', 'rating', 'created_at']
    search_fields = ['doctor__name', 'user__username', 'comment']


@admin.register(DoctorTimeSlot)
class DoctorTimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'get_day_display', 'start_time', 'end_time', 'max_patients']
    list_filter = ['doctor', 'day_of_week']
    list_editable = ['max_patients']
    list_per_page = 20
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Day'
    
    fieldsets = (
        ('Doctor Information', {
            'fields': ('doctor',)
        }),
        ('Schedule', {
            'fields': ('day_of_week', 'start_time', 'end_time')
        }),
        ('Capacity', {
            'fields': ('max_patients',),
            'description': 'Maximum number of patients allowed for this time slot'
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'doctor', 'appointment_date', 'status', 'serial_number', 'created_at']
    list_filter = ['appointment_date', 'doctor', 'status', 'created_at']
    search_fields = ['user__username', 'doctor__name']
    readonly_fields = ['created_at', 'updated_at', 'serial_number']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment', 'created_at']
    list_filter = ['doctor', 'created_at']
    search_fields = ['patient__username', 'doctor__name', 'diagnosis']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['medicines']


@admin.register(PatientMedicalHistory)
class PatientMedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'blood_group', 'updated_at']
    list_filter = ['blood_group', 'smoking', 'alcohol']
    search_fields = ['patient__username', 'patient__email']


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'recorded_at', 'heart_rate', 'blood_pressure_systolic']
    list_filter = ['recorded_at']
    search_fields = ['patient__username']


@admin.register(DoctorHoliday)
class DoctorHolidayAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'reason', 'is_full_day']
    list_filter = ['date', 'is_full_day']
    search_fields = ['doctor__name']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['hospital_name', 'location', 'capacity', 'phone']
    list_filter = ['created_at']
    search_fields = ['hospital_name', 'location']
    filter_horizontal = ['blood_samples']


@admin.register(Blood)
class BloodAdmin(admin.ModelAdmin):
    list_display = ['blood_group', 'quantity', 'expiry_date']
    list_filter = ['blood_group', 'expiry_date']
    search_fields = ['blood_group']