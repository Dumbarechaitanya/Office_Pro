import os
from datetime import datetime, date, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from base.models import ResCompany
from employee.models import Employee
from attendance.models import (
    BiometricDevice,
    BiometricStatusCode,
    BiometricDeviceUser,
    BiometricAttendanceLog
)


class Command(BaseCommand):
    help = "Seeds ADMS Biometric Device, Status Codes, Device Users, and Attendance Raw Push Logs matching screenshots."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Biometric ADMS Device and Device Users...")

        company = ResCompany.objects.filter(name__icontains="NexusWave").first() or ResCompany.objects.first()

        device, created = BiometricDevice.objects.update_or_create(
            serial_number="NW7252300146",
            defaults={
                'name': "ADMS Device NW-PUN-725201",
                'adms_enabled': True,
                'status': "Push Active",
                'last_push': timezone.make_aware(datetime(2026, 10, 23, 20, 58)),
                'company': company,
                'timezone': "Asia/Kolkata",
                'used_for': "Attendance",
                'status_code_based': False,
                'min_checkout_gap': 4.00,
                'push_url': "http://connect.nexuswave.in/iclock/cdata",
                'device_menu_info': "Device menu: Comm -> ADMS -> Server Address / Port",
                'is_active': True,
            }
        )
        self.stdout.write(f"Device: {device.name} ({device.serial_number})")

        # Status Codes (Screenshot 3)
        status_codes = [
            ("0", "Check-In / Punch In", "Check In"),
            ("1", "Check-Out / Punch Out", "Check Out"),
            ("2", "Break Out", "Break"),
            ("3", "Break In", "Break"),
            ("4", "Overtime In", "Overtime"),
            ("5", "Overtime Out", "Overtime"),
        ]
        BiometricStatusCode.objects.filter(device=device).delete()
        for code, desc, ptype in status_codes:
            BiometricStatusCode.objects.create(
                device=device,
                code=code,
                description=desc,
                punch_type=ptype
            )
        self.stdout.write(f"Created {len(status_codes)} status codes.")

        # Device Users (Screenshot 5)
        employees = list(Employee.objects.filter(is_active=True).order_by('id'))
        BiometricDeviceUser.objects.filter(device=device).delete()

        # Seed device users mapped to employees
        created_users = []
        for idx, emp in enumerate(employees, start=1):
            short_name = emp.name.split()[0]
            dev_user = BiometricDeviceUser.objects.create(
                device=device,
                device_pin=idx,
                name_on_device=short_name,
                employee=emp,
                is_mapped=True
            )
            created_users.append(dev_user)

        # Add 1 unmapped user to match Screenshot 5 (Total 46, Mapped 45, Unmapped 1)
        BiometricDeviceUser.objects.create(
            device=device,
            device_pin=99,
            name_on_device="Consultant",
            employee=None,
            is_mapped=False
        )
        self.stdout.write(f"Created {len(created_users) + 1} device users (1 unmapped).")

        # Attendance Push Logs (Screenshot 4)
        BiometricAttendanceLog.objects.filter(device=device).delete()
        log_specs = [
            (20, "20:58:51", "09:20:55", "10:58", "Check-out recorded"),
            (1,  "20:58:13", "09:20:35", "10:58", "Check-out recorded"),
            (33, "20:47:00", "10:07:36", "09:59", "Check-out recorded"),
            (19, "20:19:34", "10:25:13", "09:14", "Check-out recorded"),
            (7,  "20:15:06", "10:14:00", "09:21", "Check-out recorded"),
            (2,  "20:09:20", "11:32:12", "07:57", "Check-out recorded"),
            (4,  "19:50:15", "10:29:10", "08:41", "Check-out recorded"),
            (5,  "19:08:42", "10:28:04", "08:00", "Check-out recorded"),
            (6,  "19:25:30", "10:25:00", "08:20", "Check-out recorded"),
            (10, "20:19:00", "10:25:00", "09:14", "Check-out recorded"),
            (11, "19:29:45", "10:19:12", "08:30", "Check-out recorded"),
            (12, "19:29:10", "10:16:05", "08:34", "Check-out recorded"),
            (13, "19:15:20", "10:12:00", "08:23", "Check-out recorded"),
            (14, "19:05:00", "10:10:00", "08:15", "Check-out recorded"),
            (15, "18:55:00", "10:05:00", "08:10", "Check-out recorded"),
            (16, "19:02:00", "10:00:00", "08:22", "Check-out recorded"),
            (17, "18:45:00", "09:58:00", "08:07", "Check-out recorded"),
            (19, "18:30:00", "09:50:00", "08:00", "Check-out recorded"),
            (20, "18:20:00", "09:45:00", "07:55", "Check-out recorded"),
            (21, "18:15:00", "09:40:00", "07:55", "Check-out recorded"),
            (22, "18:05:00", "09:35:00", "07:50", "Check-out recorded"),
            (23, "18:00:00", "09:30:00", "07:50", "Check-out recorded"),
        ]

        today = date(2026, 10, 23)
        created_logs = []
        for pin, out_str, in_str, duration, note in log_specs:
            emp = employees[(pin - 1) % len(employees)]
            t_out = datetime.strptime(out_str, "%H:%M:%S").time()
            dt_out = timezone.make_aware(datetime.combine(today, t_out))

            t_in_dt = datetime.strptime(in_str, "%H:%M:%S")
            t_out_dt = datetime.strptime(out_str, "%H:%M:%S")
            in_ampm = t_in_dt.strftime("%I:%M:%S %p")
            out_ampm = t_out_dt.strftime("%I:%M:%S %p")
            att_rec = f"{duration} ({in_ampm}-{out_ampm})"

            log = BiometricAttendanceLog(
                device=device,
                device_pin=pin,
                employee=emp,
                punch_time=dt_out,
                raw_status="1",
                is_processed=True,
                attendance_record=att_rec,
                note=note
            )
            created_logs.append(log)

        BiometricAttendanceLog.objects.bulk_create(created_logs)
        self.stdout.write(f"Created {len(created_logs)} live biometric push logs.")
        self.stdout.write(self.style.SUCCESS("Biometric Device seeding completed successfully!"))
