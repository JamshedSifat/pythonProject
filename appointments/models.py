# appointments/models.py

from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)
    image = models.ImageField(upload_to='doctors/')
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    cost = models.IntegerField()
    available_spots = models.PositiveIntegerField()
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

    def get_avg_rating(self):
        reviews = DoctorReview.objects.filter(doctor=self)
        if reviews.exists():
            total = sum([review.rating for review in reviews])
            return round(total / reviews.count(), 1)
        return 0.0


class Medicine(models.Model):
    """Medicine model for easy management"""
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)  # 500mg, 1000mg etc.
    frequency = models.CharField(max_length=100)  # 2x daily, 3x daily etc.
    duration = models.CharField(max_length=100)  # 10 days, 2 weeks etc.
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

    class Meta:
        unique_together = ('doctor', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.doctor.name} ({self.get_day_of_week_display()}: {self.start_time} - {self.end_time})"


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    doctor_time_slot = models.ForeignKey(DoctorTimeSlot, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    appointment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    serial_number = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-appointment_date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.doctor.name} ({self.appointment_date})"


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    medicines = models.ManyToManyField(Medicine, related_name='prescriptions', blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prescription for {self.patient.username} by Dr. {self.doctor.name}"


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