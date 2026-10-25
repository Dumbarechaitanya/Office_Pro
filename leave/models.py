from django.db import models
from django.utils import timezone
from employee.models import Employee


class LeaveType(models.Model):
    _name = 'hr.leave.type'
    _description = 'Time Off Type'

    TIME_OFF_UNIT_CHOICES = [
        ('day', 'Day'),
        ('half_day', 'Half-day'),
        ('hours', 'Hours'),
    ]

    APPROVAL_CHOICES = [
        ('no_validation', 'No Validation'),
        ('officer', 'By Time Off Officer'),
        ('both', 'By Approver and Officer'),
    ]

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, default='PTO')
    color = models.CharField(max_length=20, default='#10b981')
    take_time_off_in = models.CharField(max_length=20, choices=TIME_OFF_UNIT_CHOICES, default='day')
    requires_allocation = models.BooleanField(default=True)
    approval_type = models.CharField(max_length=30, choices=APPROVAL_CHOICES, default='officer')
    max_days_per_year = models.IntegerField(default=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'leave_type'
        ordering = ['name']

    def __str__(self):
        return self.name


class LeaveAllocation(models.Model):
    _name = 'hr.leave.allocation'
    _description = 'Time Off Allocation'

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirm', 'To Approve'),
        ('validate', 'Approved'),
        ('refuse', 'Refused'),
    ]

    name = models.CharField(max_length=200, default='Annual Allocation')
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        db_column='employee_id',
        related_name='leave_allocations'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        db_column='leave_type_id',
        related_name='allocations'
    )
    allocated_days = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirm')
    notes = models.TextField(blank=True, null=True)
    approver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='approver_id',
        related_name='approved_allocations'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'leave_allocation'
        ordering = ['-created_at']

    def __str__(self):
        emp_name = self.employee.name if self.employee else 'Unknown'
        return f"{self.name} - {emp_name} ({self.allocated_days} days)"

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class LeaveRequest(models.Model):
    _name = 'hr.leave'
    _description = 'Time Off Request'

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirm', 'To Approve'),
        ('validate', 'Approved'),
        ('refuse', 'Refused'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        db_column='employee_id',
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        db_column='leave_type_id',
        related_name='requests'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    duration_days = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirm')
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='approved_by',
        related_name='approved_leaves'
    )
    first_approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='first_approved_by',
        related_name='first_approved_leaves'
    )
    refusal_reason = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'leave_request'
        ordering = ['-start_date']

    def __str__(self):
        emp_name = self.employee.name if self.employee else 'Unknown'
        type_name = self.leave_type.name if self.leave_type else 'Time Off'
        return f"{emp_name} - {type_name} ({self.start_date} to {self.end_date})"

    @property
    def awaiting_final_approval(self):
        """True when the first of two approval steps is done and the final step is pending."""
        return self.status in ('confirm', 'Pending') and self.first_approved_by_id is not None

    @property
    def status_label(self):
        if self.awaiting_final_approval:
            return 'Waiting Final Approval'
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class MandatoryDay(models.Model):
    _name = 'hr.leave.mandatory.day'
    _description = 'Mandatory Day / Public Holiday'

    name = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    color = models.CharField(max_length=20, default='#8b5cf6')
    is_mandatory = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'leave_mandatory_day'
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date})"
