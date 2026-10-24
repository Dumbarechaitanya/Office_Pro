from django.db import models
from django.utils import timezone
from datetime import timedelta
from employee.models import Employee


class Attendance(models.Model):
    _name = 'hr.attendance'
    _description = 'Attendance'

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Half Day', 'Half Day'),
        ('Late', 'Late'),
    ]

    INPUT_MODES = [
        ('Biometric', 'Biometric'),
        ('Kiosk', 'Kiosk'),
        ('Manual', 'Manual'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        db_column='employee_id',
        null=True,
        blank=True,
        related_name='attendances'
    )
    date = models.DateField(default=timezone.now)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    input_mode_in = models.CharField(max_length=50, choices=INPUT_MODES, default='Biometric')
    input_mode_out = models.CharField(max_length=50, choices=INPUT_MODES, default='Biometric')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'attendance'
        ordering = ['-date', '-check_in']

    def __str__(self):
        emp_name = self.employee.name if self.employee else 'Unknown'
        return f"{emp_name} ({self.date}): {self.status}"

    @property
    def is_currently_checked_in(self):
        """True if the employee is checked in and has not yet checked out."""
        return bool(self.check_in and not self.check_out)

    @property
    def worked_duration(self):
        """Calculates total timedelta worked."""
        if self.check_in and self.check_out:
            if self.check_out > self.check_in:
                return self.check_out - self.check_in
        return timedelta(0)

    @property
    def worked_hours_str(self):
        """Returns HH:MM string matching Odoo reference (e.g. '07:57')."""
        if not self.check_in or not self.check_out:
            return "00:00"
        total_seconds = int(self.worked_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    @property
    def worked_extra_hours_str(self):
        """Returns extra hours worked beyond standard 8h shift (e.g. '00:21')."""
        standard_seconds = 8 * 3600
        total_seconds = int(self.worked_duration.total_seconds())
        if total_seconds > standard_seconds:
            extra_seconds = total_seconds - standard_seconds
            hours = extra_seconds // 3600
            minutes = (extra_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        return "00:00"

    @property
    def expected_hours_str(self):
        """Standard expected workday shift length (08:20 with breaks)."""
        return "08:20"

    @property
    def difference_str(self):
        """Difference between worked hours and expected 08:20 shift."""
        expected_seconds = 8 * 3600 + 20 * 60  # 8h 20m
        total_seconds = int(self.worked_duration.total_seconds())
        diff_seconds = total_seconds - expected_seconds
        sign = "-" if diff_seconds < 0 else "+"
        diff_abs = abs(diff_seconds)
        hours = diff_abs // 3600
        minutes = (diff_abs % 3600) // 60
        return f"{sign}{hours:02d}:{minutes:02d}"

    @property
    def is_negative_difference(self):
        expected_seconds = 8 * 3600 + 20 * 60
        total_seconds = int(self.worked_duration.total_seconds())
        return total_seconds < expected_seconds


class BiometricDevice(models.Model):
    _name = 'biometric.device'
    _description = 'Biometric ADMS Device'

    name = models.CharField(max_length=150, default='ADMS Device NW-PUN-725201')
    serial_number = models.CharField(max_length=100, unique=True, default='NW7252300146')
    adms_enabled = models.BooleanField(default=True)
    status = models.CharField(max_length=50, default='Push Active')
    last_push = models.DateTimeField(null=True, blank=True)
    company = models.ForeignKey('base.ResCompany', on_delete=models.SET_NULL, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    used_for = models.CharField(max_length=50, default='Attendance')
    status_code_based = models.BooleanField(default=False)
    min_checkout_gap = models.DecimalField(max_digits=5, decimal_places=2, default=4.00)
    push_url = models.CharField(max_length=255, default='http://connect.nexuswave.in/iclock/cdata')
    device_menu_info = models.CharField(max_length=255, default='Device menu: Comm -> ADMS -> Server Address / Port')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'biometric_device'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    @property
    def total_users_count(self):
        return self.device_users.count()

    @property
    def mapped_users_count(self):
        return self.device_users.filter(is_mapped=True).count()

    @property
    def unmapped_users_count(self):
        return self.device_users.filter(is_mapped=False).count()


class BiometricStatusCode(models.Model):
    _name = 'biometric.status.code'
    _description = 'Device Status Code'

    device = models.ForeignKey(BiometricDevice, on_delete=models.CASCADE, related_name='status_codes')
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=150)
    punch_type = models.CharField(max_length=50, choices=[('Check In', 'Check In'), ('Check Out', 'Check Out'), ('Break', 'Break'), ('Overtime', 'Overtime')])

    class Meta:
        db_table = 'biometric_status_code'
        ordering = ['code']

    def __str__(self):
        return f"Code {self.code}: {self.description}"


class BiometricDeviceUser(models.Model):
    _name = 'biometric.device.user'
    _description = 'Biometric Device User'

    device = models.ForeignKey(BiometricDevice, on_delete=models.CASCADE, related_name='device_users')
    device_pin = models.IntegerField()
    name_on_device = models.CharField(max_length=150)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='biometric_mappings')
    is_mapped = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'biometric_device_user'
        ordering = ['device_pin']
        unique_together = [('device', 'device_pin')]

    def __str__(self):
        return f"PIN {self.device_pin} - {self.name_on_device}"


class BiometricAttendanceLog(models.Model):
    _name = 'biometric.attendance.log'
    _description = 'Biometric Attendance Raw Push Log'

    device = models.ForeignKey(BiometricDevice, on_delete=models.CASCADE, related_name='attendance_logs')
    device_pin = models.IntegerField()
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='biometric_logs')
    punch_time = models.DateTimeField()
    raw_status = models.CharField(max_length=10, default='1')
    is_processed = models.BooleanField(default=True)
    attendance_record = models.CharField(max_length=200, blank=True, null=True)
    note = models.CharField(max_length=200, default='Check-out recorded')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'biometric_attendance_log'
        ordering = ['-punch_time']

    def __str__(self):
        return f"PIN {self.device_pin} @ {self.punch_time}"


class OvertimeRuleset(models.Model):
    _name = 'hr.attendance.overtime.ruleset'
    _description = 'Overtime Ruleset'

    name = models.CharField(max_length=150, default='Default Ruleset')
    rate_combination_mode = models.CharField(max_length=50, default='Maximum Rate')
    description = models.TextField(blank=True, default='Provide a description or sources for this ruleset.')
    country = models.CharField(max_length=100, default='India')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_overtime_ruleset'
        ordering = ['name']

    def __str__(self):
        return self.name


class OvertimeRule(models.Model):
    _name = 'hr.attendance.overtime.rule'
    _description = 'Overtime Rule Line'

    ruleset = models.ForeignKey(OvertimeRuleset, on_delete=models.CASCADE, related_name='rules')
    name = models.CharField(max_length=150)
    based_off = models.CharField(max_length=100, default='Quantity')
    information = models.CharField(max_length=255, default='From Employee')
    rate = models.CharField(max_length=20, default='100%')
    sequence = models.IntegerField(default=10)

    class Meta:
        db_table = 'attendance_overtime_rule'
        ordering = ['sequence', 'id']

    def __str__(self):
        return f"{self.name} ({self.rate})"


class AttendanceSetting(models.Model):
    _name = 'attendance.config.settings'
    _description = 'Attendance Global Configuration Settings'

    attendances_from_backend = models.BooleanField(default=False)
    automatic_checkout = models.BooleanField(default=False)
    absence_management = models.BooleanField(default=False)
    device_location_tracking = models.BooleanField(default=False)
    display_extra_hours = models.BooleanField(default=True)
    extra_hours_validation = models.CharField(max_length=50, default='Approved by Manager')

    class Meta:
        db_table = 'attendance_settings'

    def __str__(self):
        return "Attendance System Settings"

