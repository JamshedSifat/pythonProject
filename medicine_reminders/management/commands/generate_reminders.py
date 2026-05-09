# management/commands/generate_reminders.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from medicine_reminders.models import Medicine, MedicineReminder
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate medicine reminders for all active medicines from start_date to end_date'

    def handle(self, *args, **options):
        today = date.today()
        
        # Get all active medicines
        medicines = Medicine.objects.filter(is_active=True).prefetch_related('reminder_times')
        
        for medicine in medicines:
            # Generate reminders for entire date range
            current_date = medicine.start_date
            
            while current_date <= medicine.end_date:
                # Create reminder for each time
                for reminder_time in medicine.reminder_times.all():
                    MedicineReminder.objects.get_or_create(
                        medicine=medicine,
                        reminder_date=current_date,
                        reminder_time=reminder_time,
                    )
                
                current_date += timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Reminders generated successfully!')
        )