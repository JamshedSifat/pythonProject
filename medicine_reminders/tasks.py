# tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta, datetime
import logging

from .models import Medicine, ReminderTime, NotificationLog, DoseTaken

logger = logging.getLogger(__name__)


@shared_task
def check_and_send_scheduled_reminders():
    """Check for scheduled reminders every minute"""
    now = timezone.now()
    today = date.today()
    current_time = now.time()
    
    # Get all active medicines that are within their date range
    medicines = Medicine.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).prefetch_related('reminder_times')
    
    for medicine in medicines:
        for reminder_time in medicine.reminder_times.all():
            # Calculate time difference
            reminder_datetime = datetime.combine(today, reminder_time.time)
            current_datetime = datetime.combine(today, current_time)
            time_diff = abs((reminder_datetime - current_datetime).total_seconds())
            
            # If within 60 seconds of reminder time
            if time_diff < 60:
                logger.info(f"Reminder for {medicine.name} at {reminder_time.time}")
                
                # Check if dose already taken today
                already_taken = DoseTaken.objects.filter(
                    medicine=medicine,
                    reminder_time=reminder_time,
                    date_taken=today
                ).exists()
                
                if not already_taken:
                    # Log notification
                    NotificationLog.objects.create(
                        user=medicine.user,
                        medicine=medicine,
                        notification_type='reminder',
                        status='sent',
                        message=f"⏰ Time to take {medicine.name} - {medicine.dosage_amount} {medicine.get_dosage_unit_display()}",
                        sent_at=now
                    )
                    
                    # Send email notification (optional)
                    try:
                        send_medicine_reminder_email.delay(medicine.id, reminder_time.id)
                    except Exception as e:
                        logger.error(f"Failed to send reminder email: {str(e)}")


@shared_task
def send_medicine_reminder_email(medicine_id, reminder_time_id):
    """Send email reminder to user"""
    try:
        from django.core.mail import send_mail
        from .models import Medicine, ReminderTime
        
        medicine = Medicine.objects.get(id=medicine_id)
        reminder_time = ReminderTime.objects.get(id=reminder_time_id)
        
        subject = f"💊 Medicine Reminder: {medicine.name}"
        message = f"""
        Hi {medicine.user.first_name},
        
        It's time to take your medicine!
        
        Medicine: {medicine.name}
        Dosage: {medicine.dosage_amount} {medicine.get_dosage_unit_display()}
        Time: {reminder_time.time.strftime('%I:%M %p')}
        
        {f'Instructions: {medicine.instructions}' if medicine.instructions else ''}
        
        Stay healthy!
        """
        
        send_mail(
            subject,
            message,
            'InnovativeHealthCare@gmail.com',
            [medicine.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email sent to {medicine.user.email} for {medicine.name}")
        
    except Exception as e:
        logger.error(f"Error sending medicine reminder email: {str(e)}")


@shared_task
def check_missed_doses():
    """Check for missed doses at the end of day"""
    today = date.today()
    
    # Get all medicines that should have been taken today
    medicines = Medicine.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).prefetch_related('reminder_times')
    
    for medicine in medicines:
        for reminder_time in medicine.reminder_times.all():
            # Check if dose was NOT taken today
            dose_taken = DoseTaken.objects.filter(
                medicine=medicine,
                reminder_time=reminder_time,
                date_taken=today
            ).exists()
            
            if not dose_taken:
                # Log missed dose notification
                NotificationLog.objects.create(
                    user=medicine.user,
                    medicine=medicine,
                    notification_type='missed_dose',
                    status='sent',
                    message=f"⚠️ You missed taking {medicine.name} at {reminder_time.time.strftime('%I:%M %p')}"
                )