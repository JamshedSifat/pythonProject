from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    cost = models.IntegerField()
    
    # *** এটাই মূল ফিল্ড - ডাক্তার প্রতিদিন সর্বোচ্চ কতজন পেশেন্ট দেখবেন ***
    daily_max_patients = models.PositiveIntegerField(default=10, help_text="Maximum patients per day")
    
    next_available_appointment_date = models.DateField(null=True, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-average_rating', '-total_reviews']

    def __str__(self):
        return self.name
    
    def get_today_booked_count(self):
        """আজকে কতজন বুক করেছে"""
        today = timezone.now().date()
        return Appointment.objects.filter(
            doctor=self,
            appointment_date=today,
            status__in=['confirmed', 'pending']
        ).count()
    
    def get_available_spots_today(self):
        """আজকে আর কতজন বুক করতে পারবে"""
        booked = self.get_today_booked_count()
        return self.daily_max_patients - booked
    
    def is_available_today(self):
        """আজকে বুকিং নেওয়া যাবে কিনা"""
        return self.get_available_spots_today() > 0 and self.status


class Medicine(models.Model):
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'dosage', 'frequency')

    def __str__(self):
        return f"{self.name} - {self.dosage}"


class DoctorReview(models.Model):
    RATING_CHOICES = (
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('doctor', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.doctor.name} - {self.rating} stars by {self.user.username}"

class DoctorTimeSlot(models.Model):
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_patients = models.PositiveIntegerField(default=10, help_text="Maximum patients for this time slot")
    
    class Meta:
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor.name} ({self.get_day_of_week_display()}: {self.start_time} - {self.end_time}) - Max: {self.max_patients} patients"
    
    def get_booked_count(self, appointment_date):
        """Get number of booked appointments for this slot on a specific date"""
        return Appointment.objects.filter(
            doctor=self.doctor,
            doctor_time_slot=self,
            appointment_date=appointment_date,
            status__in=['confirmed', 'pending']
        ).count()
    
    def get_available_spots(self, appointment_date):
        """Get remaining available spots for this slot"""
        booked = self.get_booked_count(appointment_date)
        return self.max_patients - booked
    
    def is_available(self, appointment_date):
        """Check if slot has available spots"""
        return self.get_available_spots(appointment_date) > 0
    
    def get_booking_status(self, appointment_date):
        """Get detailed booking status"""
        booked = self.get_booked_count(appointment_date)
        return {
            'total': self.max_patients,
            'booked': booked,
            'available': self.max_patients - booked,
            'is_full': booked >= self.max_patients,
            'percentage': (booked / self.max_patients * 100) if self.max_patients > 0 else 0
        }

        
class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    doctor_time_slot = models.ForeignKey(DoctorTimeSlot, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    appointment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    serial_number = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-appointment_date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.doctor.name} ({self.appointment_date})"
    
    def approve(self):
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save()
            return True
        return False
    
    def reject(self):
        if self.status == 'pending':
            self.status = 'rejected'
            self.save()
            return True
        return False


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    medicines = models.ManyToManyField(Medicine, related_name='prescriptions', blank=True)
    notes = models.TextField(blank=True, null=True)
    
    # ইমেজ ফিল্ড যোগ করুন
    prescription_image = models.ImageField(upload_to='prescriptions/', blank=True, null=True, help_text="Upload prescription image")
    doctor_signature = models.ImageField(upload_to='signatures/', blank=True, null=True, help_text="Doctor's digital signature")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription for {self.patient.username} by Dr. {self.doctor.name}"


class PatientMedicalHistory(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='medical_histories')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_histories')
    
    blood_group = models.CharField(max_length=5, blank=True, null=True, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ])
    height = models.FloatField(blank=True, null=True, help_text="Height in cm")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")
    blood_pressure = models.CharField(max_length=20, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    chronic_diseases = models.TextField(blank=True, null=True)
    current_medications = models.TextField(blank=True, null=True)
    smoking = models.BooleanField(default=False)
    alcohol = models.BooleanField(default=False)
    exercise = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('daily', 'Daily'), ('weekly', 'Weekly'), ('rarely', 'Rarely'), ('never', 'Never')
    ])
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('patient', 'doctor')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.patient.username} - History with Dr. {self.doctor.name}"


class VitalSign(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vitals')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='vitals')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='vitals', null=True, blank=True)
    
    temperature = models.FloatField(blank=True, null=True, help_text="°C")
    blood_pressure_systolic = models.IntegerField(blank=True, null=True)
    blood_pressure_diastolic = models.IntegerField(blank=True, null=True)
    heart_rate = models.IntegerField(blank=True, null=True)
    respiratory_rate = models.IntegerField(blank=True, null=True)
    oxygen_saturation = models.IntegerField(blank=True, null=True)
    blood_sugar = models.IntegerField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    bmi = models.FloatField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
    
    def save(self, *args, **kwargs):
        if self.weight and self.height and self.height > 0:
            self.bmi = round(self.weight / ((self.height/100) ** 2), 1)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Vitals for {self.patient.username} on {self.recorded_at.date()}"


class DoctorHoliday(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='holidays')
    date = models.DateField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    is_full_day = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('doctor', 'date')
        ordering = ['date']
    
    def __str__(self):
        return f"{self.doctor.name} - Off on {self.date}"


class Hospital(models.Model):
    hospital_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    capacity = models.IntegerField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    blood_samples = models.ManyToManyField('Blood', related_name='hospitals')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['hospital_name']

    def __str__(self):
        return self.hospital_name


class Blood(models.Model):
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O+', 'O+'),
        ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-'), ('O-', 'O-'),
    )
    
    blood_group = models.CharField(max_length=20, choices=BLOOD_GROUP_CHOICES)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['blood_group']

    def __str__(self):
        return f"{self.blood_group} - {self.quantity} bags"