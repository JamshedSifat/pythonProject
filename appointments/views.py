from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.db import models
from django.http import JsonResponse, FileResponse, HttpResponse
import json
from datetime import timedelta, datetime
from io import BytesIO
from django.http import JsonResponse

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors

from .models import (
    Doctor, DoctorReview, DoctorTimeSlot, Appointment, 
    Prescription, Hospital, Blood, Medicine, PatientMedicalHistory, VitalSign, DoctorHoliday
)
from .forms import (
    DoctorReviewForm, PrescriptionForm, MedicineForm
)




def appointment(request):
    from django.utils import timezone
    today = timezone.now().date()
    
    doctors = Doctor.objects.filter(status=True)  # শুধু available ডাক্তার দেখান
    
    for doctor in doctors:
        today_booked = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=today,
            status__in=['confirmed', 'pending']
        ).count()
        
        doctor.today_booked = today_booked
        doctor.available_today = doctor.daily_max_patients - today_booked
        
        # Debug print
        print(f"Doctor: {doctor.name}, Max: {doctor.daily_max_patients}, Booked: {today_booked}, Available: {doctor.available_today}")
    
    return render(request, "appointments/appointment.html", {
        'doctors': doctors,
        'total_doctors': doctors.count(),
        'today': today,
        'search_query': ''
    })


def doctor_search(request):
    query_d = request.GET.get('q', '')
    if query_d:
        words = query_d.split()
        doctors = Doctor.objects.none()
        for word in words:
            if word.lower() == "available":
                doctors = doctors | Doctor.objects.filter(status=True)
            elif word.lower() == "unavailable":
                doctors = doctors | Doctor.objects.filter(status=False)
            else:
                doctors = doctors | Doctor.objects.filter(name__icontains=word) | Doctor.objects.filter(specialty__icontains=word)
    else:
        messages.error(request, "Search bar was empty")
        return redirect('appointments:appointment')
    if not doctors:
        messages.error(request, "No doctors found.")
        return redirect('appointments:appointment')
    return render(request, 'appointments/appointment.html', {
        'doctors': doctors,
        'search_query': query_d,
        'total_doctors': doctors.count()
    })




@login_required
def create_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        description = request.POST.get('description')
        appointment_time_id = request.POST.get('appointment_time')
        
        selected_date = timezone.datetime.strptime(appointment_date, '%Y-%m-%d').date()
        today = timezone.now().date()
        
        if selected_date < today:
            messages.error(request, "Please select an upcoming date.")
            return redirect(reverse('appointments:create_appointment', args=[doctor_id]))
        
        # Check doctor's daily limit for the selected date
        today_booked_count = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=selected_date,
            status__in=['confirmed', 'pending']
        ).count()
        
        # যদি ডাক্তারের দৈনিক সীমা পূর্ণ হয়ে যায়
        if today_booked_count >= doctor.daily_max_patients:
            messages.error(request, f"Sorry! Dr. {doctor.name} is fully booked for {selected_date}. Maximum {doctor.daily_max_patients} patients per day.")
            return redirect(reverse('appointments:create_appointment', args=[doctor_id]))
        
        # Time slot check (যদি টাইম স্লট সিস্টেম ব্যবহার করেন)
        if appointment_time_id:
            try:
                time_slot = DoctorTimeSlot.objects.get(id=appointment_time_id, doctor=doctor)
            except DoctorTimeSlot.DoesNotExist:
                messages.error(request, "Time slot not found.")
                return redirect(reverse('appointments:create_appointment', args=[doctor_id]))
        else:
            time_slot = None
        
        # Serial number
        serial_number = Appointment.objects.filter(doctor=doctor, appointment_date=selected_date).count() + 1
        
        # Create appointment
        appointment = Appointment(
            user=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            description=description,
            doctor_time_slot=time_slot,
            serial_number=serial_number,
            status='pending'
        )
        appointment.save()
        
        # Calculate remaining spots
        remaining_spots = doctor.daily_max_patients - (today_booked_count + 1)
        
        messages.success(request, f"Appointment request sent successfully! {remaining_spots} spots remaining for {selected_date}")
        return redirect(reverse('appointments:appointment'))
    
    # GET request - show booking form
    return render(request, 'appointments/create_appointment.html', {
        'doctor': doctor,
        'today_booked': Appointment.objects.filter(
            doctor=doctor,
            appointment_date=timezone.now().date(),
            status__in=['confirmed', 'pending']
        ).count(),
        'remaining_spots': doctor.daily_max_patients - Appointment.objects.filter(
            doctor=doctor,
            appointment_date=timezone.now().date(),
            status__in=['confirmed', 'pending']
        ).count()
    })

@login_required
def check_availability(request, doctor_id):
    """Check if doctor is available on a specific date"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date required'}, status=400)
    
    try:
        selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date'}, status=400)
    
    today = timezone.now().date()
    
    if selected_date < today:
        return JsonResponse({'available': False, 'message': 'Please select future date'})
    
    # Count booked appointments for this date
    booked_count = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=selected_date,
        status__in=['confirmed', 'pending']
    ).count()
    
    remaining = doctor.daily_max_patients - booked_count
    
    return JsonResponse({
        'available': remaining > 0 and doctor.status,
        'remaining_spots': remaining,
        'max_patients': doctor.daily_max_patients,
        'booked_count': booked_count
    })

def cancel_appointment(request, appointment_id, doctor_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if appointment.user == request.user:
        doctor.available_spots += 1
        doctor.save()
        appointment.delete()
        messages.success(request, "Appointment cancelled successfully.")
    else:
        messages.error(request, "You are not authorized to cancel this appointment.")
    return redirect('accounts:user_profile')


def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = DoctorReview.objects.filter(doctor=doctor)
    time_slots = DoctorTimeSlot.objects.filter(doctor=doctor)
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    return render(request, 'appointments/doctor_detail.html', {
        'doctor': doctor,
        'reviews': reviews,
        'time_slots': time_slots,
        'user_review': user_review,
        'total_reviews': reviews.count(),
        'average_rating': doctor.average_rating,
    })


@login_required
def create_review(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    existing_review = DoctorReview.objects.filter(doctor=doctor, user=request.user).first()
    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '')
        if existing_review:
            existing_review.rating = int(rating)
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Review updated successfully.")
        else:
            DoctorReview.objects.create(doctor=doctor, user=request.user, rating=int(rating), comment=comment)
            doctor.total_reviews += 1
            doctor.average_rating = doctor.get_avg_rating()
            doctor.save()
            messages.success(request, "Your review has been saved.")
        return redirect('appointments:doctor_detail', doctor_id=doctor_id)
    return render(request, 'appointments/create_review.html', {'doctor': doctor, 'existing_review': existing_review})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(DoctorReview, id=review_id, user=request.user)
    doctor = review.doctor
    doctor_id = doctor.id
    doctor.total_reviews -= 1
    review.delete()
    doctor.average_rating = doctor.get_avg_rating()
    doctor.save()
    messages.success(request, "Review deleted successfully.")
    return redirect('appointments:doctor_detail', doctor_id=doctor_id)


def top_doctors(request):
    doctors = Doctor.objects.filter(average_rating__gte=4.0).order_by('-average_rating', '-total_reviews')[:10]
    return render(request, 'appointments/top_doctors.html', {'doctors': doctors, 'total_doctors': doctors.count()})


@login_required
def reschedule(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    doctor = appointment.doctor
    time_slots = DoctorTimeSlot.objects.filter(doctor=doctor)
    if request.method == 'POST':
        new_date = request.POST.get('appointment_date')
        new_time_id = request.POST.get('appointment_time')
        try:
            new_time_slot = DoctorTimeSlot.objects.get(id=new_time_id, doctor=doctor)
        except DoctorTimeSlot.DoesNotExist:
            messages.error(request, "Time slot not found.")
            return redirect('appointments:reschedule', appointment_id=appointment_id)
        new_selected_date = timezone.datetime.strptime(new_date, '%Y-%m-%d').date()
        today = timezone.now().date()
        if new_selected_date < today:
            messages.error(request, "Please select an upcoming date.")
            return redirect('appointments:reschedule', appointment_id=appointment_id)
        appointment.appointment_date = new_date
        appointment.doctor_time_slot = new_time_slot
        appointment.status = 'pending'
        appointment.save()
        messages.success(request, "Reschedule request sent. Doctor will confirm.")
        return redirect('accounts:user_profile')
    return render(request, 'appointments/reschedule.html', {'appointment': appointment, 'doctor': doctor, 'time_slots': time_slots})


@login_required
def alternatives(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    doctor = appointment.doctor
    alternative_slots = DoctorTimeSlot.objects.filter(doctor=doctor).exclude(id=appointment.doctor_time_slot.id)
    return render(request, 'appointments/alternatives.html', {
        'appointment': appointment, 'doctor': doctor, 'alternative_slots': alternative_slots
    })


@login_required
def add_medicine(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('appointments:appointment')
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine added successfully.")
            return redirect('appointments:add_medicine')
    else:
        form = MedicineForm()
    medicines = Medicine.objects.all()
    return render(request, 'appointments/add_medicine.html', {'form': form, 'medicines': medicines})


@login_required
def edit_medicine(request, medicine_id):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('appointments:appointment')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine updated successfully!")
            return redirect('appointments:add_medicine')
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'appointments/edit_medicine.html', {
        'form': form,
        'medicine': medicine
    })


@login_required
def delete_medicine(request, medicine_id):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('appointments:appointment')
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, "Medicine deleted successfully!")
        return redirect('appointments:add_medicine')
    
    return render(request, 'appointments/delete_medicine.html', {'medicine': medicine})


@login_required
def upload_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = appointment.doctor
    if request.user != doctor.user:
        messages.error(request, "You do not have permission.")
        return redirect('appointments:appointment')
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription, created = Prescription.objects.update_or_create(
                appointment=appointment,
                defaults={
                    'doctor': doctor,
                    'patient': appointment.user,
                    'diagnosis': form.cleaned_data['diagnosis'],
                    'notes': form.cleaned_data['notes']
                }
            )
            prescription.medicines.set(form.cleaned_data['medicines'])
            prescription.save()
            appointment.status = 'completed'
            appointment.save()
            messages.success(request, "Prescription saved successfully.")
            return redirect('appointments:doctor_appointments')
    else:
        form = PrescriptionForm()
    return render(request, 'appointments/upload_prescription.html', {
        'appointment': appointment,
        'doctor': doctor,
        'form': form
    })


def prescription_history(request):
    if not request.user.is_authenticated:
        return redirect('login')
    prescriptions = Prescription.objects.filter(patient=request.user)
    return render(request, 'appointments/prescription_history.html', {
        'prescriptions': prescriptions,
        'total_prescriptions': prescriptions.count()
    })


def view_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if request.user != prescription.patient and request.user != prescription.doctor.user:
        messages.error(request, "You do not have permission.")
        return redirect('appointments:appointment')
    return render(request, 'appointments/view_prescription.html', {'prescription': prescription})


@login_required
def edit_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        messages.error(request, "Access denied. Only doctors can edit prescriptions.")
        return redirect('home')
    
    doctor = Doctor.objects.get(user=request.user)
    
    if prescription.doctor != doctor:
        messages.error(request, "You can only edit your own prescriptions")
        return redirect('appointments:doctor_prescriptions_list')
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, instance=prescription)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.save()
            prescription.medicines.set(form.cleaned_data['medicines'])
            messages.success(request, "Prescription updated successfully!")
            return redirect('appointments:doctor_prescriptions_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PrescriptionForm(instance=prescription)
        form.fields['medicines'].initial = prescription.medicines.all()
    
    return render(request, 'appointments/edit_prescription.html', {
        'form': form,
        'prescription': prescription,
        'appointment': prescription.appointment,
        'doctor': doctor
    })


@login_required
def download_prescription_pdf(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    if request.user != prescription.patient and request.user != prescription.doctor.user:
        messages.error(request, "You don't have permission to download this prescription")
        return redirect('appointments:prescription_history')
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        alignment=1,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    story = []
    
    story.append(Paragraph("MEDICAL PRESCRIPTION", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Doctor Info
    doctor_name = prescription.doctor.name if prescription.doctor.name else f"Dr. {prescription.doctor.user.get_full_name() or prescription.doctor.user.username}"
    doctor_specialty = prescription.doctor.specialty if prescription.doctor.specialty else "General Medicine"
    doctor_experience = prescription.doctor.experience_years if prescription.doctor.experience_years else 0
    
    story.append(Paragraph(f"<b>Dr. {doctor_name}</b>", heading_style))
    story.append(Paragraph(f"Specialty: {doctor_specialty}", normal_style))
    story.append(Paragraph(f"Experience: {doctor_experience} years", normal_style))
    
    if prescription.doctor.user.email:
        story.append(Paragraph(f"Email: {prescription.doctor.user.email}", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Patient Info
    patient_name = prescription.patient.get_full_name() or prescription.patient.username
    patient_email = prescription.patient.email
    
    patient_data = [
        ['Patient Name:', patient_name],
        ['Patient Email:', patient_email],
        ['Appointment Date:', prescription.appointment.appointment_date.strftime('%d-%m-%Y')],
        ['Prescription Date:', prescription.created_at.strftime('%d-%m-%Y')],
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 3.5*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Diagnosis
    story.append(Paragraph("DIAGNOSIS", heading_style))
    story.append(Paragraph(prescription.diagnosis, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Medicines
    if prescription.medicines.exists():
        story.append(Paragraph("PRESCRIBED MEDICINES", heading_style))
        
        medicines_data = [['#', 'Medicine Name', 'Dosage', 'Frequency', 'Duration']]
        for idx, medicine in enumerate(prescription.medicines.all(), 1):
            medicines_data.append([
                str(idx),
                medicine.name,
                medicine.dosage,
                medicine.frequency,
                medicine.duration
            ])
        
        medicines_table = Table(medicines_data, colWidths=[0.5*inch, 2*inch, 1.2*inch, 1.3*inch, 1.2*inch])
        medicines_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(medicines_table)
        story.append(Spacer(1, 0.2*inch))
    else:
        story.append(Paragraph("No medicines prescribed", normal_style))
    
    if prescription.notes:
        story.append(Paragraph("ADDITIONAL NOTES", heading_style))
        story.append(Paragraph(prescription.notes, normal_style))
        story.append(Spacer(1, 0.2*inch))
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("_" * 80, normal_style))
    story.append(Paragraph(f"Dr. {doctor_name}", ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        alignment=1,
        spaceAfter=5
    )))
    story.append(Paragraph(f"Date: {prescription.created_at.strftime('%d-%m-%Y')}", ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,
        textColor=colors.grey
    )))
    
    doc.build(story)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_{prescription.id}_{patient_name}.pdf"'
    return response


def doctor_prescriptions_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not a doctor.")
        return redirect('appointments:appointment')
    prescriptions = Prescription.objects.filter(doctor=doctor)
    return render(request, 'appointments/doctor_prescriptions_list.html', {
        'prescriptions': prescriptions,
        'total_prescriptions': prescriptions.count()
    })


def medicine_reminder(request):
    if not request.user.is_authenticated:
        return redirect('login')
    prescriptions = Prescription.objects.filter(patient=request.user)
    all_medicines = []
    for prescription in prescriptions:
        for medicine in prescription.medicines.all():
            all_medicines.append({
                'name': medicine.name,
                'dosage': medicine.dosage,
                'frequency': medicine.frequency,
                'duration': medicine.duration,
                'doctor': prescription.doctor.name
            })
    return render(request, 'appointments/medicine_reminder.html', {
        'medicines': all_medicines,
        'total_medicines': len(all_medicines),
        'current_date': timezone.now()
    })


def emergency(request):
    hospitals = Hospital.objects.all()
    return render(request, "appointments/emergency.html", {'hospitals': hospitals, 'search_query': ''})


def blood_search(request):
    query = request.GET.get('q', '')
    hospitals = Hospital.objects.all()
    if query:
        hospitals = hospitals.filter(Q(hospital_name__icontains=query) | Q(location__icontains=query) | Q(blood_samples__blood_group__iexact=query))
        hospitals = hospitals.distinct()
    else:
        messages.error(request, "Search bar was empty")
        return redirect('appointments:emergency')
    if not hospitals:
        messages.error(request, "No hospitals found.")
        return redirect('appointments:emergency')
    return render(request, 'appointments/emergency.html', {'hospitals': hospitals, 'search_query': query})


@login_required
def doctor_appointments(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not registered as a doctor.")
        return redirect('home')
    appointments = Appointment.objects.filter(doctor=doctor).select_related('user', 'doctor_time_slot').order_by('-appointment_date')
    today = timezone.now().date()
    today_appointments = appointments.filter(appointment_date=today)
    pending_prescriptions = appointments.filter(prescription__isnull=True, status='completed').count()
    completed_appointments = appointments.filter(status='completed').count()
    return render(request, 'appointments/doctor_appointments.html', {
        'appointments': appointments,
        'today_appointments': today_appointments,
        'pending_prescriptions': pending_prescriptions,
        'completed_appointments': completed_appointments,
    })


@login_required
def approve_or_reject_appointment(request, appointment_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = appointment.doctor
    if doctor.user != request.user:
        return JsonResponse({'success': False, 'error': 'This appointment does not belong to you'}, status=403)
    data = json.loads(request.body)
    action = data.get('action')
    if action == 'approve':
        if appointment.approve():
            doctor.available_spots -= 1
            if doctor.available_spots == 0:
                doctor.status = False
            doctor.save()
            return JsonResponse({'success': True, 'message': 'Appointment approved'})
    elif action == 'reject':
        if appointment.reject():
            return JsonResponse({'success': True, 'message': 'Appointment rejected'})
    return JsonResponse({'success': False, 'error': 'Invalid action'})


@login_required
def update_appointment_status(request, appointment_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = appointment.doctor
    if doctor.user != request.user:
        return JsonResponse({'success': False, 'error': 'This appointment does not belong to you'}, status=403)
    data = json.loads(request.body)
    new_status = data.get('status')
    if new_status not in ['confirmed', 'completed', 'cancelled']:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    old_status = appointment.status
    appointment.status = new_status
    appointment.save()
    if new_status == 'cancelled' and old_status != 'cancelled':
        doctor.available_spots += 1
        if doctor.available_spots > 0 and not doctor.status:
            doctor.status = True
        doctor.save()
    elif old_status == 'cancelled' and new_status != 'cancelled':
        doctor.available_spots -= 1
        if doctor.available_spots == 0:
            doctor.status = False
        doctor.save()
    return JsonResponse({'success': True, 'message': 'Status updated successfully', 'new_status': new_status})


@login_required
def patient_medical_history(request, patient_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        messages.error(request, "Access denied")
        return redirect('home')
    
    doctor = Doctor.objects.get(user=request.user)
    patient = get_object_or_404(User, id=patient_id)
    
    medical_history, created = PatientMedicalHistory.objects.get_or_create(patient=patient, doctor=doctor)
    
    prescriptions = Prescription.objects.filter(patient=patient, doctor=doctor).select_related('appointment').order_by('-created_at')
    appointments = Appointment.objects.filter(user=patient, doctor=doctor).select_related('doctor_time_slot').order_by('-appointment_date')
    vitals = VitalSign.objects.filter(patient=patient, doctor=doctor).order_by('-recorded_at')
    
    if request.method == 'POST':
        medical_history.blood_group = request.POST.get('blood_group')
        medical_history.height = request.POST.get('height') or None
        medical_history.weight = request.POST.get('weight') or None
        medical_history.blood_pressure = request.POST.get('blood_pressure')
        medical_history.allergies = request.POST.get('allergies')
        medical_history.chronic_diseases = request.POST.get('chronic_diseases')
        medical_history.current_medications = request.POST.get('current_medications')
        medical_history.smoking = request.POST.get('smoking') == 'on'
        medical_history.alcohol = request.POST.get('alcohol') == 'on'
        medical_history.exercise = request.POST.get('exercise')
        medical_history.emergency_contact_name = request.POST.get('emergency_contact_name')
        medical_history.emergency_contact_number = request.POST.get('emergency_contact_number')
        medical_history.emergency_contact_relation = request.POST.get('emergency_contact_relation')
        medical_history.notes = request.POST.get('notes')
        medical_history.save()
        
        messages.success(request, "Medical history updated successfully!")
        return redirect('appointments:patient_medical_history', patient_id=patient_id)
    
    context = {
        'patient': patient,
        'doctor': doctor,
        'medical_history': medical_history,
        'prescriptions': prescriptions,
        'appointments': appointments,
        'vitals': vitals,
        'total_prescriptions': prescriptions.count(),
        'total_appointments': appointments.count(),
    }
    return render(request, 'appointments/patient_medical_history.html', context)


@login_required
def patient_list(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        messages.error(request, "Access denied")
        return redirect('home')
    
    doctor = Doctor.objects.get(user=request.user)
    patients = User.objects.filter(
        appointment__doctor=doctor
    ).distinct().annotate(
        last_visit=models.Max('appointment__appointment_date')
    ).order_by('-last_visit')
    
    return render(request, 'appointments/patient_list.html', {
        'doctor': doctor,
        'patients': patients,
        'total_patients': patients.count(),
    })


@login_required
def search_patients(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        return JsonResponse({'patients': []})
    doctor = Doctor.objects.get(user=request.user)
    query = request.GET.get('q', '')
    patients = User.objects.filter(appointment__doctor=doctor).distinct()
    if query:
        patients = patients.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query) | Q(profile__mobile__icontains=query))
    patient_list = []
    for patient in patients[:20]:
        last_appointment = patient.appointment_set.filter(doctor=doctor).order_by('-appointment_date').first()
        patient_list.append({
            'id': patient.id,
            'name': patient.get_full_name() or patient.username,
            'email': patient.email,
            'mobile': patient.profile.mobile if hasattr(patient, 'profile') else '',
            'last_visit': last_appointment.appointment_date.strftime('%Y-%m-%d') if last_appointment else 'Never'
        })
    return JsonResponse({'patients': patient_list})


@login_required
def manage_time_slots(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        messages.error(request, "Access denied")
        return redirect('home')
    
    doctor = Doctor.objects.get(user=request.user)
    time_slots = DoctorTimeSlot.objects.filter(doctor=doctor).order_by('day_of_week', 'start_time')
    
    context = {
        'doctor': doctor,
        'time_slots': time_slots,
        'today_weekday': timezone.now().weekday(),
    }
    return render(request, 'appointments/manage_time_slots.html', context)

@login_required
def add_time_slot(request):
    if request.method != 'POST':
        return redirect('appointments:manage_time_slots')
    
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        messages.error(request, "Access denied")
        return redirect('home')
    
    doctor = Doctor.objects.get(user=request.user)
    day_of_week = request.POST.get('day_of_week')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    max_patients = request.POST.get('max_patients', 5)  # ডিফল্ট 5
    
    # Debug - print করে দেখুন কি আসছে
    print(f"Day: {day_of_week}")
    print(f"Start: {start_time}")
    print(f"End: {end_time}")
    print(f"Max Patients from form: {max_patients}")
    
    if not day_of_week or not start_time or not end_time:
        messages.error(request, "Please fill all fields")
        return redirect('appointments:manage_time_slots')
    
    # max_patients কে integer এ কনভার্ট করুন
    try:
        max_patients = int(max_patients)
        if max_patients < 1:
            max_patients = 5
        if max_patients > 50:
            max_patients = 50
    except (ValueError, TypeError):
        max_patients = 5
    
    print(f"After conversion: {max_patients}")
    
    # ডুপ্লিকেট চেক
    existing = DoctorTimeSlot.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time
    ).first()
    
    if existing:
        messages.error(request, "This time slot already exists!")
        return redirect('appointments:manage_time_slots')
    
    # স্লট তৈরি করুন
    slot = DoctorTimeSlot.objects.create(
        doctor=doctor,
        day_of_week=int(day_of_week),
        start_time=start_time,
        end_time=end_time,
        max_patients=max_patients
    )
    
    print(f"Created slot - Max Patients: {slot.max_patients}")
    
    messages.success(request, f"Time slot added successfully! (Max {max_patients} patients per slot)")
    return redirect('appointments:manage_time_slots')

@login_required
def delete_time_slot(request, slot_id):
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        messages.error(request, "Access denied")
        return redirect('home')
    
    doctor = Doctor.objects.get(user=request.user)
    slot = get_object_or_404(DoctorTimeSlot, id=slot_id, doctor=doctor)
    
    upcoming_appointments = Appointment.objects.filter(
        doctor_time_slot=slot,
        appointment_date__gte=timezone.now().date(),
        status__in=['pending', 'confirmed']
    ).count()
    
    if upcoming_appointments > 0:
        messages.error(request, f"Cannot delete! {upcoming_appointments} upcoming appointments use this slot.")
        return redirect('appointments:manage_time_slots')
    
    slot.delete()
    messages.success(request, "Time slot deleted successfully!")
    return redirect('appointments:manage_time_slots')