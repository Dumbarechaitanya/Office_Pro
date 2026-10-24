from django.db import models


class Department(models.Model):
    _name = 'hr.department'
    _description = 'Department'

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, db_column='manager_id', blank=True, null=True, related_name='managed_departments')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, db_column='parent_id', blank=True, null=True, related_name='child_departments')
    color = models.CharField(max_length=20, default='#0284c7')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'hr_department'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_members(self):
        return self.employees.filter(is_active=True).count()


class Employee(models.Model):
    _name = 'hr.employee'
    _description = 'Employee'

    employee_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    department_rel = models.ForeignKey(Department, on_delete=models.SET_NULL, db_column='department_id', blank=True, null=True, related_name='employees')
    job_title = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateField()
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, db_column='manager_id', blank=True, null=True, related_name='subordinates')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Personal & Demographics
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    father_spouse_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # Statutory & Identification (PAN, Aadhaar, Passport, UAN, PF, ESIC)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    uan_number = models.CharField(max_length=20, blank=True, null=True)
    pf_number = models.CharField(max_length=50, blank=True, null=True)
    esic_number = models.CharField(max_length=25, blank=True, null=True)

    # Address
    current_address = models.TextField(blank=True, null=True)
    current_city = models.CharField(max_length=100, blank=True, null=True)
    current_state = models.CharField(max_length=100, blank=True, null=True)
    current_pincode = models.CharField(max_length=10, blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    permanent_city = models.CharField(max_length=100, blank=True, null=True)
    permanent_state = models.CharField(max_length=100, blank=True, null=True)
    permanent_pincode = models.CharField(max_length=10, blank=True, null=True)

    # Employment & Costing
    employment_type = models.CharField(max_length=50, default='Full-Time')
    branch = models.CharField(max_length=100, default='Pune HQ')
    confirmation_date = models.DateField(blank=True, null=True)
    avatar_url = models.CharField(max_length=255, blank=True, null=True)
    hourly_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    annual_ctc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Banking Details
    bank_name = models.CharField(max_length=150, blank=True, null=True)
    bank_account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=15, blank=True, null=True)
    bank_branch = models.CharField(max_length=150, blank=True, null=True)

    # Multi-Level Approver Matrices (README Section 4.1)
    timesheet_approver = models.ForeignKey('self', on_delete=models.SET_NULL, db_column='timesheet_approver_id', blank=True, null=True, related_name='timesheets_to_approve')
    leave_approver_l1 = models.ForeignKey('self', on_delete=models.SET_NULL, db_column='leave_approver_l1_id', blank=True, null=True, related_name='leaves_to_approve_l1')
    leave_approver_l2 = models.ForeignKey('self', on_delete=models.SET_NULL, db_column='leave_approver_l2_id', blank=True, null=True, related_name='leaves_to_approve_l2')
    expense_approver_l1 = models.ForeignKey('self', on_delete=models.SET_NULL, db_column='expense_approver_l1_id', blank=True, null=True, related_name='expenses_to_approve_l1')
    expense_approver_l2 = models.ForeignKey('self', on_delete=models.SET_NULL, db_column='expense_approver_l2_id', blank=True, null=True, related_name='expenses_to_approve_l2')

    class Meta:
        managed = False
        db_table = 'employee'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.employee_code})"

    @property
    def display_department(self):
        if self.department_rel:
            return self.department_rel.name
        return self.department or 'General'

    @property
    def masked_aadhaar(self):
        if self.aadhaar_number and len(str(self.aadhaar_number)) == 12:
            return f"XXXX-XXXX-{str(self.aadhaar_number)[-4:]}"
        return self.aadhaar_number or ''

    @property
    def masked_pan(self):
        if self.pan_number and len(str(self.pan_number)) == 10:
            return f"{str(self.pan_number)[:2]}XXXXX{str(self.pan_number)[-2:]}"
        return self.pan_number or ''

    @property
    def avatar_color(self):
        PALETTE = [
            '#4f46e5', '#7c3aed', '#059669', '#d97706', '#dc2626',
            '#0284c7', '#0891b2', '#be185d', '#9333ea', '#ea580c',
            '#15803d', '#4338ca', '#b45309', '#0f766e', '#a21caf',
            '#047857', '#b91c1c', '#6d28d9', '#1d4ed8', '#c2410c'
        ]
        seed = ((self.id or 1) * 37 + sum(ord(c) for c in (self.name or ''))) % len(PALETTE)
        return PALETTE[seed]



class OnboardingTemplate(models.Model):
    _name = 'hr.onboarding.template'
    _description = 'Employee Onboarding Template'

    name = models.CharField(max_length=150, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, related_name='onboarding_templates')
    job_title = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=50, default='Full-Time')
    branch = models.CharField(max_length=100, default='Pune HQ')
    timesheet_approver = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='template_timesheet_approvals')
    leave_approver_l1 = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='template_leave_l1_approvals')
    leave_approver_l2 = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='template_leave_l2_approvals')
    expense_approver_l1 = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='template_expense_l1_approvals')
    expense_approver_l2 = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='template_expense_l2_approvals')
    checklist_notes = models.TextField(blank=True, null=True, help_text="Default onboarding checklist items")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_onboarding_template'
        ordering = ['name']

    def __str__(self):
        return self.name
