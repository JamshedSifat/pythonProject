from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from .models import UserProfile
from .forms import DoctorMedicalInfoForm


def login(request):
    if request.method == "POST":
        username = request.POST.get("u_name")
        password = request.POST.get("u_password")
        authenticated_user = authenticate(request, username=username, password=password)

        if authenticated_user is not None:
            auth_login(request, authenticated_user)
            if authenticated_user.is_superuser:
                return redirect('/admin/')
            elif hasattr(authenticated_user, 'profile') and authenticated_user.profile.role == "Doctor":
                return redirect('accounts:doctor_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "accounts/login.html")


def register(request):
    if request.method == "POST":
        u_name = request.POST.get("u_name")
        u_fname = request.POST.get("u_fname", "")
        u_lname = request.POST.get("u_lname", "")
        u_email = request.POST.get("u_email")
        u_password = request.POST.get("u_password")
        u_age = request.POST.get("u_age", "0")
        u_address = request.POST.get("u_address", "")
        u_mobile = request.POST.get("u_mobile", "")
        u_gender = request.POST.get("u_gender")
        u_role = request.POST.get("u_role", "User")

        if not u_name or not u_email or not u_password:
            messages.error(request, "Username, email and password are required")
            return redirect('accounts:register')

        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Username already exists")
            return redirect('accounts:register')

        if User.objects.filter(email=u_email).exists():
            messages.error(request, "Email already exists")
            return redirect('accounts:register')

        try:
            age_int = int(u_age) if u_age and u_age.strip() else 0
        except (ValueError, TypeError):
            age_int = 0

        if not u_gender:
            u_gender = 'Male'

        if u_role not in ['User', 'Doctor']:
            u_role = 'User'

        try:
            user = User.objects.create_user(
                username=u_name,
                first_name=u_fname,
                last_name=u_lname,
                email=u_email,
                password=u_password
            )
            
            # পরিবর্তন: get_or_create ব্যবহার করুন
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': u_role,
                    'age': age_int,
                    'address': u_address,
                    'mobile': u_mobile,
                    'gender': u_gender
                }
            )
            
            if not created:
                # যদি প্রোফাইল আগে থেকে থাকে, আপডেট করুন
                profile.role = u_role
                profile.age = age_int
                profile.address = u_address
                profile.mobile = u_mobile
                profile.gender = u_gender
                profile.save()
            
            messages.success(request, "Account Created Successfully")
            return redirect('accounts:login')
            
        except IntegrityError as e:
            messages.error(request, f"Database error: {str(e)}")
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            
    return render(request, "accounts/register.html")

@login_required
def user_profile(request):
    if request.method == "POST":
        if "delete_account" in request.POST:
            user = request.user
            auth_logout(request)
            user.delete()
            messages.success(request, "Account deleted successfully")
            return redirect('home')
        else:
            user = request.user
            profile = user.profile
            user.first_name = request.POST.get("first_name", "")
            user.last_name = request.POST.get("last_name", "")
            user.email = request.POST.get("email", "")
            user.save()
            try:
                age = int(request.POST.get("age", 0)) if request.POST.get("age") else 0
            except ValueError:
                age = 0
            profile.age = age
            profile.address = request.POST.get("address", "")
            profile.mobile = request.POST.get("mobile", "")
            profile.gender = request.POST.get("gender", "Male")
            profile.save()
            messages.success(request, "Profile updated successfully")
            return redirect('accounts:user_profile')
    user_profile = request.user.profile
    return render(request, 'accounts/user_profile.html', {'user_profile': user_profile})


@login_required
def doctor_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        messages.error(request, "You are not authorized to access this page")
        return redirect('home')
    
    from appointments.models import Doctor, Appointment, DoctorTimeSlot
    
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    doctor, created = Doctor.objects.get_or_create(
        user=request.user,
        defaults={
            'name': f"Dr. {request.user.get_full_name() or request.user.username}",
            'specialty': 'General Medicine',
            'cost': 500,
            'daily_max_patients': 10,
            'status': True,
            'experience_years': 0
        }
    )
    
    # আজকের বুকিং স্ট্যাটাস
    today_booked = doctor.get_today_booked_count()
    today_available = doctor.get_available_spots_today()
    
    # অন্যান্য স্ট্যাটাস
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    completed_appointments = Appointment.objects.filter(doctor=doctor, status='completed').count()
    pending_appointments = Appointment.objects.filter(doctor=doctor, status='confirmed').count()
    cancelled_appointments = Appointment.objects.filter(doctor=doctor, status='cancelled').count()
    pending_requests = Appointment.objects.filter(doctor=doctor, status='pending').count()
    
    # আজকের অ্যাপয়েন্টমেন্ট
    today_appointments = Appointment.objects.filter(
        doctor=doctor, appointment_date=today
    ).select_related('user', 'doctor_time_slot').order_by('serial_number')
    
    # সব অ্যাপয়েন্টমেন্ট
    all_appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('user', 'doctor_time_slot').order_by('-appointment_date')
    
    # টাইম স্লট
    time_slots = DoctorTimeSlot.objects.filter(doctor=doctor).order_by('day_of_week', 'start_time')
    
    context = {
        'doctor': doctor,
        'daily_max_patients': doctor.daily_max_patients,
        'today_booked': today_booked,
        'today_available': today_available,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
        'cancelled_appointments': cancelled_appointments,
        'pending_requests': pending_requests,
        'today_appointments': today_appointments,
        'all_appointments': all_appointments,
        'time_slots': time_slots,
        'time_slots_count': time_slots.count(),
        'today': today,
    }
    return render(request, 'accounts/doctor_dashboard.html', context)

@login_required
def doctor_edit_profile(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != "Doctor":
        messages.error(request, "Access denied")
        return redirect('home')
    
    from appointments.models import Doctor
    
    doctor, created = Doctor.objects.get_or_create(
        user=request.user,
        defaults={
            'name': f"Dr. {request.user.get_full_name() or request.user.username}",
            'specialty': 'General Medicine',
            'cost': 500,          # ডিফল্ট
            'available_spots': 10, # ডিফল্ট
            'status': True,
            'experience_years': 0
        }
    )
    
    if request.method == 'POST':
        form = DoctorMedicalInfoForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            doctor = form.save(commit=False)
            doctor.name = f"Dr. {request.user.get_full_name() or request.user.username}"
            doctor.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:doctor_dashboard')
    else:
        form = DoctorMedicalInfoForm(instance=doctor)
    
    return render(request, 'accounts/doctor_edit_profile.html', {'form': form, 'doctor': doctor})

@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')