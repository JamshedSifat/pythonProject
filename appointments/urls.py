from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment, name='appointment'),
    path('search/', views.doctor_search, name='doctor_search'),
    path('create/<int:doctor_id>/', views.create_appointment, name='create_appointment'),
    path('cancel/<int:appointment_id>/<int:doctor_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('doctor/<int:doctor_id>/review/', views.create_review, name='create_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('top-doctors/', views.top_doctors, name='top_doctors'),
    path('appointment/<int:appointment_id>/reschedule/', views.reschedule, name='reschedule'),
    path('appointment/<int:appointment_id>/alternatives/', views.alternatives, name='alternatives'),
    
    # Medicine URLs
    path('medicine/add/', views.add_medicine, name='add_medicine'),
    path('medicine/edit/<int:medicine_id>/', views.edit_medicine, name='edit_medicine'),
    path('medicine/delete/<int:medicine_id>/', views.delete_medicine, name='delete_medicine'),
    
    # Prescription URLs
    path('prescription/upload/<int:appointment_id>/', views.upload_prescription, name='upload_prescription'),
    path('prescriptions/', views.prescription_history, name='prescription_history'),
    path('prescription/<int:prescription_id>/', views.view_prescription, name='view_prescription'),
    path('prescription/<int:prescription_id>/download-pdf/', views.download_prescription_pdf, name='download_prescription_pdf'),
    path('prescriptions/doctor/', views.doctor_prescriptions_list, name='doctor_prescriptions_list'),
    path('prescription/edit/<int:prescription_id>/', views.edit_prescription, name='edit_prescription'),
    
    # Other URLs
    path('medicine-reminder/', views.medicine_reminder, name='medicine_reminder'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('emergency/', views.emergency, name='emergency'),
    path('blood-search/', views.blood_search, name='blood_search'),
    
    # Appointment Management
    path('approve/<int:appointment_id>/', views.approve_or_reject_appointment, name='approve_appointment'),
    path('update-status/<int:appointment_id>/', views.update_appointment_status, name='update_appointment_status'),
    
    # Patient Management
    path('patient/<int:patient_id>/medical-history/', views.patient_medical_history, name='patient_medical_history'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/search/', views.search_patients, name='search_patients'),
    
    # Time Slot Management
    path('doctor/time-slots/', views.manage_time_slots, name='manage_time_slots'),
    path('doctor/time-slots/add/', views.add_time_slot, name='add_time_slot'),
    path('doctor/time-slots/delete/<int:slot_id>/', views.delete_time_slot, name='delete_time_slot'),


     path('check-availability/<int:doctor_id>/', views.check_availability, name='check_availability'),
]