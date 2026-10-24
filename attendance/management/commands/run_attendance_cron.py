from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, datetime, time
from attendance.models import Attendance
from base.models import IrCron, ResUsers


class Command(BaseCommand):
    help = "Runs Attendance Daily Cron Jobs: Auto punch-out for missing check-outs (sets Half Day till 15:00 IST), Late marks, and Early going flags."

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, help='Target date in YYYY-MM-DD format (default: today)')

    def handle(self, *args, **options):
        date_str = options.get('date')
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.localdate()

        self.stdout.write(f"Executing attendance daily cron for date: {target_date}...")

        # 1. Missing punch-out cron job (Audio 1 directive):
        # If punch-in is present, but punch-out is missing/null, auto check-out at 15:00 IST and mark as 'Half Day' (5 hours worked from 10:00 AM)
        missing_punch_outs = Attendance.objects.filter(
            date=target_date,
            check_in__isnull=False,
            check_out__isnull=True,
            is_active=True
        )

        half_day_count = 0
        for att in missing_punch_outs:
            auto_checkout_dt = datetime.combine(target_date, time(15, 0))  # 3:00 PM IST
            if timezone.is_aware(att.check_in):
                auto_checkout_dt = timezone.make_aware(auto_checkout_dt, timezone.get_current_timezone())
            att.check_out = auto_checkout_dt
            att.status = 'Half Day'
            att.input_mode_out = 'Manual'
            att.save(update_fields=['check_out', 'status', 'input_mode_out', 'updated_at'])
            half_day_count += 1
            self.stdout.write(f"  -> Employee {att.employee.name if att.employee else 'Unknown'}: auto checked-out at 15:00 (Half Day).")

        # 2. Late Marks Evaluation:
        # Standard shift starts at 10:00 AM with 15 mins grace period (10:15 AM)
        late_cutoff = time(10, 15)
        punches_today = Attendance.objects.filter(
            date=target_date,
            check_in__isnull=False,
            is_active=True
        )

        late_count = 0
        for att in punches_today:
            if att.check_in.time() > late_cutoff and att.status == 'Present':
                att.status = 'Late'
                att.save(update_fields=['status', 'updated_at'])
                late_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Attendance cron completed successfully! Processed {half_day_count} missing punch-outs to Half Day (15:00 IST), {late_count} late marks."
        ))
