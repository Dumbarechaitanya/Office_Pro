from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from employee.models import Employee
from attendance.models import Attendance, OvertimeRuleset, OvertimeRule, AttendanceSetting


class Command(BaseCommand):
    help = "Seeds Overtime Rulesets, Attendance Configuration Settings, and Pending Reviews matching screenshots."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Overtime Rulesets and Attendance Settings...")

        # 1. Overtime Ruleset (Screenshot 4)
        ruleset, created = OvertimeRuleset.objects.get_or_create(
            name="Default Ruleset",
            defaults={
                'rate_combination_mode': "Maximum Rate",
                'description': "Provide a description or sources for this ruleset.",
                'country': "India",
                'is_active': True,
            }
        )

        OvertimeRule.objects.filter(ruleset=ruleset).delete()
        OvertimeRule.objects.create(
            ruleset=ruleset,
            name="Employee Schedule Rule",
            based_off="Quantity",
            information="From Employee",
            rate="100%",
            sequence=10
        )
        OvertimeRule.objects.create(
            ruleset=ruleset,
            name="Non Working Days Rule",
            based_off="Timing",
            information="On any non-working day",
            rate="100%",
            sequence=20
        )
        self.stdout.write(f"Overtime Ruleset '{ruleset.name}' configured with 2 rules.")

        # 2. Attendance Configuration Settings (Screenshots 2 & 3)
        setting, _ = AttendanceSetting.objects.get_or_create(
            id=1,
            defaults={
                'attendances_from_backend': False,
                'automatic_checkout': False,
                'absence_management': False,
                'device_location_tracking': False,
                'display_extra_hours': True,
                'extra_hours_validation': "Approved by Manager",
            }
        )
        self.stdout.write("Attendance settings initialized.")

        # 3. Pending Attendance Review Records (Screenshot 1)
        employees = list(Employee.objects.filter(is_active=True).order_by('id')[:6])
        if employees:
            pending_samples = [
                (employees[0], date(2026, 8, 2), "09:30:00", "14:00:00", "Manual", "Biometric"),
                (employees[1], date(2026, 8, 2), "10:15:00", "19:45:00", "Manual", "Biometric"),
                (employees[2], date(2026, 8, 3), "09:00:00", "13:30:00", "Manual", "Biometric"),
                (employees[3], date(2026, 8, 3), "10:30:00", "20:00:00", "Manual", "Biometric"),
            ]
            for emp, dt, t_in, t_out, m_in, m_out in pending_samples:
                dt_in = timezone.make_aware(datetime.combine(dt, datetime.strptime(t_in, "%H:%M:%S").time()))
                dt_out = timezone.make_aware(datetime.combine(dt, datetime.strptime(t_out, "%H:%M:%S").time()))
                Attendance.objects.update_or_create(
                    employee=emp,
                    date=dt,
                    defaults={
                        'check_in': dt_in,
                        'check_out': dt_out,
                        'status': 'Present',
                        'input_mode_in': m_in,
                        'input_mode_out': m_out,
                        'is_active': True,
                    }
                )
            self.stdout.write(f"Seeded {len(pending_samples)} pending review records matching Screenshot 1.")

        self.stdout.write(self.style.SUCCESS("Overtime rulesets, settings, and pending reviews seeded successfully!"))
