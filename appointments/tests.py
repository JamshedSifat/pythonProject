from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import (
    Doctor, DoctorTimeSlot, Appointment, DoctorReview,
    Prescription
)


class DoctorModelTest(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            name='Dr. Ahmed Ali',
            specialty='Cardiology',
            cost=500,
            available_spots=10,
            status=True,
            experience_years=10
        )
    
    def test_doctor_creation(self):
        self.assertEqual(self.doctor.name, 'Dr. Ahmed Ali')
        self.assertEqual(self.doctor.specialty, 'Cardiology')
        self.assertEqual(self.doctor.average_rating, 0)
        self.assertTrue(self.doctor.status)


class DoctorReviewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='patient1', password='pass123')
        self.doctor = Doctor.objects.create(
            name='Dr. Test',
            specialty='General',
            cost=300,
            available_spots=10,
            status=True
        )
        self.time_slot = DoctorTimeSlot.objects.create(
            doctor=self.doctor,
            day_of_week=0,
            start_time='10:00',
            end_time='11:00'
        )
        self.appointment = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            description='Checkup',
            appointment_date=timezone.now().date() - timedelta(days=1),
            doctor_time_slot=self.time_slot
        )
    
    def test_review_creation(self):
        review = DoctorReview.objects.create(
            doctor=self.doctor,
            user=self.user,
            rating=5,
            comment='Excellent doctor'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.doctor, self.doctor)


class SmartSchedulingTest(TestCase):
    def setUp(self):
        self.doctor = Doctor.objects.create(
            name='Dr. Schedule',
            specialty='Pediatrics',
            cost=400,
            available_spots=5,
            status=True
        )
        self.slot = DoctorTimeSlot.objects.create(
            doctor=self.doctor,
            start_time='09:00',
            end_time='10:00',
            day_of_week=0
        )
        self.appointment_date = timezone.now().date() + timedelta(days=1)
    
    def test_appointment_creation(self):
        user = User.objects.create_user(username='patient2', password='pass123')
        
        appointment = Appointment.objects.create(
            user=user,
            doctor=self.doctor,
            description='Visit 1',
            appointment_date=self.appointment_date,
            doctor_time_slot=self.slot,
            status='confirmed'
        )
        
        self.assertEqual(appointment.status, 'confirmed')
        self.assertEqual(appointment.doctor, self.doctor)


class PrescriptionTest(TestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(username='doctor1', password='pass123')
        self.patient_user = User.objects.create_user(username='patient3', password='pass123')
        
        self.doctor = Doctor.objects.create(
            name='Dr. Prescription',
            specialty='General',
            cost=300,
            available_spots=10,
            status=True,
            user=self.doctor_user
        )
        
        self.time_slot = DoctorTimeSlot.objects.create(
            doctor=self.doctor,
            day_of_week=0,
            start_time='14:00',
            end_time='15:00'
        )
        
        self.appointment = Appointment.objects.create(
            user=self.patient_user,
            doctor=self.doctor,
            description='Medical checkup',
            appointment_date=timezone.now().date(),
            doctor_time_slot=self.time_slot
        )
    
    def test_prescription_creation(self):
        medicines = [
            {
                'name': 'Aspirin',
                'dosage': '500mg',
                'frequency': '2x daily',
                'duration': '10 days'
            }
        ]
        
        prescription = Prescription.objects.create(
            appointment=self.appointment,
            doctor=self.doctor,
            patient=self.patient_user,
            diagnosis='Flu',
            notes='Rest well',
            medicines=medicines
        )
        
        self.assertEqual(len(prescription.medicines), 1)
        self.assertEqual(prescription.medicines[0]['name'], 'Aspirin')
