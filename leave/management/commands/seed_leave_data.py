import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from leave.models import LeaveType, LeaveAllocation, LeaveRequest, MandatoryDay
from employee.models import Employee


class Command(BaseCommand):
    help = "Seed realistic sample Leave data matching Odoo 17 Time Off screen recording"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Leave Types...")
        types_data = [
            {'name': 'Paid Time Off', 'code': 'PTO', 'color': '#10b981', 'max_days_per_year': 18, 'requires_allocation': True, 'take_time_off_in': 'day'},
            {'name': 'Compensatory Days', 'code': 'COMP', 'color': '#0284c7', 'max_days_per_year': 5, 'requires_allocation': True, 'take_time_off_in': 'day'},
            {'name': 'Sick Time Off', 'code': 'SICK', 'color': '#f59e0b', 'max_days_per_year': 10, 'requires_allocation': False, 'take_time_off_in': 'day'},
            {'name': 'Unpaid Indicator', 'code': 'UNPAID', 'color': '#ef4444', 'max_days_per_year': 30, 'requires_allocation': False, 'take_time_off_in': 'day'},
        ]

        types_map = {}
        for t_data in types_data:
            lt, created = LeaveType.objects.update_or_create(
                name=t_data['name'],
                defaults=t_data
            )
            types_map[lt.code] = lt
            self.stdout.write(f"  - {lt.name} (Code: {lt.code})")

        self.stdout.write("Seeding Mandatory Days / Public Holidays...")
        holidays_data = [
            {'name': 'Republic Day', 'start_date': date(2026, 1, 26), 'end_date': date(2026, 1, 26), 'color': '#0284c7'},
            {'name': 'Independence Day', 'start_date': date(2026, 8, 15), 'end_date': date(2026, 8, 15), 'color': '#10b981'},
            {'name': 'Gandhi Jayanti', 'start_date': date(2026, 10, 2), 'end_date': date(2026, 10, 2), 'color': '#8b5cf6'},
            {'name': 'Diwali Festival', 'start_date': date(2026, 10, 29), 'end_date': date(2026, 10, 31), 'color': '#f59e0b'},
            {'name': 'Christmas Day', 'start_date': date(2026, 12, 25), 'end_date': date(2026, 12, 25), 'color': '#ef4444'},
        ]
        for h in holidays_data:
            MandatoryDay.objects.update_or_create(
                name=h['name'],
                start_date=h['start_date'],
                defaults=h
            )
            self.stdout.write(f"  - {h['name']} ({h['start_date']})")

        employees = list(Employee.objects.filter(is_active=True)[:15])
        if not employees:
            self.stdout.write(self.style.WARNING("No employees found to assign leave data."))
            return

        approver = employees[0]

        self.stdout.write("Seeding Allocations...")
        for emp in employees:
            # Paid Time Off allocation
            LeaveAllocation.objects.update_or_create(
                employee=emp,
                leave_type=types_map['PTO'],
                name=f"Annual Leave Allocation 2026 - {emp.name}",
                defaults={
                    'allocated_days': 18.00,
                    'valid_from': date(2026, 1, 1),
                    'valid_to': date(2026, 12, 31),
                    'status': 'validate',
                    'notes': 'Standard annual PTO balance granted.',
                    'approver': approver,
                }
            )
            # Compensatory Days allocation
            LeaveAllocation.objects.update_or_create(
                employee=emp,
                leave_type=types_map['COMP'],
                name=f"Compensatory Credit - {emp.name}",
                defaults={
                    'allocated_days': 2.00,
                    'valid_from': date(2026, 1, 1),
                    'valid_to': date(2026, 12, 31),
                    'status': 'validate',
                    'notes': 'Weekend sprint delivery credit.',
                    'approver': approver,
                }
            )

        self.stdout.write("Seeding Leave Requests...")
        # A few requests in 'confirm' (To Approve)
        if len(employees) >= 4:
            e1, e2, e3, e4 = employees[0], employees[1], employees[2], employees[3]

            # Pending / To Approve
            LeaveRequest.objects.update_or_create(
                employee=e2,
                start_date=date(2026, 10, 26),
                end_date=date(2026, 10, 27),
                defaults={
                    'leave_type': types_map['PTO'],
                    'duration_days': 2.0,
                    'reason': 'Family gathering out of town',
                    'status': 'confirm',
                    'approved_by': None,
                }
            )
            LeaveRequest.objects.update_or_create(
                employee=e3,
                start_date=date(2026, 10, 27),
                end_date=date(2026, 10, 27),
                defaults={
                    'leave_type': types_map['COMP'],
                    'duration_days': 1.0,
                    'reason': 'Compensatory off for deployment support',
                    'status': 'confirm',
                    'approved_by': None,
                }
            )
            LeaveRequest.objects.update_or_create(
                employee=e4,
                start_date=date(2026, 10, 28),
                end_date=date(2026, 10, 28),
                defaults={
                    'leave_type': types_map['SICK'],
                    'duration_days': 1.0,
                    'reason': 'Doctor consultation and rest',
                    'status': 'confirm',
                    'approved_by': None,
                }
            )

            # Approved requests (on calendar)
            LeaveRequest.objects.update_or_create(
                employee=e1,
                start_date=date(2026, 10, 19),
                end_date=date(2026, 10, 20),
                defaults={
                    'leave_type': types_map['PTO'],
                    'duration_days': 2.0,
                    'reason': 'Personal errands',
                    'status': 'validate',
                    'approved_by': approver,
                }
            )
            LeaveRequest.objects.update_or_create(
                employee=e2,
                start_date=date(2026, 10, 12),
                end_date=date(2026, 10, 12),
                defaults={
                    'leave_type': types_map['SICK'],
                    'duration_days': 1.0,
                    'reason': 'Viral fever recovery',
                    'status': 'validate',
                    'approved_by': approver,
                }
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded sample Leave data!"))
