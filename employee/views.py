import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from base.auth_helpers import get_current_ir_user, login_required_ir, is_admin_user, is_hr_officer_or_admin
from base.models import MailMessage
from employee.models import Department, Employee, OnboardingTemplate


def is_hr_manager_or_admin(user):
    return is_hr_officer_or_admin(user)


def hr_officer_required(view_func):
    @login_required_ir
    def _wrapped(request, *args, **kwargs):
        current_user = get_current_ir_user(request)
        if not is_hr_officer_or_admin(current_user):
            messages.error(request, "Access Restricted: The Employee directory and Department administration are restricted to HR Officers and Administrators. You can view your employee details in My Profile.")
            return redirect('profile')
        return view_func(request, *args, **kwargs)
    return _wrapped


from base.search_metadata import (
    get_search_metadata,
    apply_search,
    apply_group_by,
    get_favorites,
    get_operators_json,
)
from base.models import IrModel


@hr_officer_required
def employee_list(request):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user)
    is_hr = is_hr_manager_or_admin(current_user)

    self_ir_model = IrModel.objects.filter(model_name='hr.employee').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model) if self_ir_model else ([], [])

    default_filterable = [
        {'name': 'name', 'label': 'Employee Name', 'field_type': 'VARCHAR', 'operators': [['ilike', 'contains'], ['=', 'is equal to']]},
        {'name': 'employee_code', 'label': 'Code', 'field_type': 'VARCHAR', 'operators': [['ilike', 'contains'], ['=', 'is equal to']]},
        {'name': 'department', 'label': 'Department', 'field_type': 'VARCHAR', 'operators': [['ilike', 'contains'], ['=', 'is equal to']]},
        {'name': 'job_title', 'label': 'Job Position', 'field_type': 'VARCHAR', 'operators': [['ilike', 'contains'], ['=', 'is equal to']]},
        {'name': 'branch', 'label': 'Branch', 'field_type': 'VARCHAR', 'operators': [['ilike', 'contains'], ['=', 'is equal to']]},
        {'name': 'employment_type', 'label': 'Employment Type', 'field_type': 'VARCHAR', 'operators': [['ilike', 'contains'], ['=', 'is equal to']]},
    ]
    if not filterable_fields:
        filterable_fields = default_filterable

    default_groupable = [
        {'name': 'department', 'label': 'Department'},
        {'name': 'job_title', 'label': 'Job Position'},
        {'name': 'branch', 'label': 'Branch'},
        {'name': 'employment_type', 'label': 'Employment Type'},
    ]
    if not groupable_fields:
        groupable_fields = default_groupable

    query = request.GET.get('q', '').strip()
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''
    view_mode = request.GET.get('view_mode', 'kanban')  # kanban or list

    employees = Employee.objects.filter(is_active=True).select_related('department_rel', 'manager')
    employees = apply_search(employees, domain, query, search_fields=['name', 'employee_code', 'email', 'job_title', 'department', 'branch'])

    groups = apply_group_by(employees, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='hr.employee')

    columns = [
        {'name': 'employee_code', 'label': 'Code'},
        {'name': 'name', 'label': 'Employee Name'},
        {'name': 'department', 'label': 'Department'},
        {'name': 'job_title', 'label': 'Job Position'},
        {'name': 'manager', 'label': 'Manager'},
        {'name': 'branch', 'label': 'Branch'},
        {'name': 'email', 'label': 'Work Email'},
        {'name': 'phone', 'label': 'Phone'},
    ]

    return render(request, 'employee/employee_list.html', {
        'employees': employees,
        'object_list': employees,
        'total_count': employees.count(),
        'title': 'Employees',
        'create_url': reverse('employee_create') if is_hr else None,
        'search_model_key': 'hr.employee',
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'operators_by_type_json': get_operators_json(),
        'current_domain': json.dumps(domain),
        'active_group_by': group_by_field,
        'groups': groups,
        'favorites': favorites,
        'columns': columns,
        'view_mode': view_mode,
        'current_user': current_user,
        'is_admin': is_admin,
        'is_hr': is_hr,
    })


@hr_officer_required
def employee_detail(request, emp_id):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user)
    is_hr = is_hr_manager_or_admin(current_user)

    emp = get_object_or_404(Employee.objects.select_related('department_rel', 'manager', 'timesheet_approver', 'leave_approver_l1', 'leave_approver_l2', 'expense_approver_l1', 'expense_approver_l2'), id=emp_id)

    # Permission check: Self-service users can only view their own record unless HR/Admin
    is_self = current_user.employee_id == emp.id if current_user.employee_id else False
    if not (is_hr or is_self):
        messages.error(request, "Permission Denied: You can only view your own employee profile.")
        if current_user.employee_id:
            return redirect('employee_detail', emp_id=current_user.employee_id)
        return redirect('employee_list')

    if request.method == 'POST':
        if not is_hr:
            # Self-service user updating personal details
            emp.phone = request.POST.get('phone', emp.phone)
            emp.emergency_contact_name = request.POST.get('emergency_contact_name', emp.emergency_contact_name)
            emp.emergency_contact_relation = request.POST.get('emergency_contact_relation', emp.emergency_contact_relation)
            emp.emergency_contact_phone = request.POST.get('emergency_contact_phone', emp.emergency_contact_phone)
            emp.current_address = request.POST.get('current_address', emp.current_address)
            emp.current_city = request.POST.get('current_city', emp.current_city)
            emp.current_state = request.POST.get('current_state', emp.current_state)
            emp.current_pincode = request.POST.get('current_pincode', emp.current_pincode)
            emp.permanent_address = request.POST.get('permanent_address', emp.permanent_address)
            emp.permanent_city = request.POST.get('permanent_city', emp.permanent_city)
            emp.permanent_state = request.POST.get('permanent_state', emp.permanent_state)
            emp.permanent_pincode = request.POST.get('permanent_pincode', emp.permanent_pincode)
            emp.save()
            messages.success(request, "Your personal contact information has been updated.")
            return redirect('employee_detail', emp_id=emp.id)

        # Full HR/Admin update
        emp.name = request.POST.get('name', emp.name).strip()
        emp.employee_code = request.POST.get('employee_code', emp.employee_code).strip()
        emp.email = request.POST.get('email', emp.email).strip()
        emp.phone = request.POST.get('phone', emp.phone).strip()
        dept_id = request.POST.get('department_id')
        if dept_id:
            emp.department_rel_id = int(dept_id)
            emp.department = Department.objects.filter(id=dept_id).values_list('name', flat=True).first()
        else:
            emp.department_rel = None
            emp.department = request.POST.get('department', '').strip()

        emp.job_title = request.POST.get('job_title', emp.job_title).strip()
        emp.branch = request.POST.get('branch', emp.branch).strip()
        emp.employment_type = request.POST.get('employment_type', emp.employment_type).strip()

        date_joined = request.POST.get('date_joined')
        if date_joined:
            emp.date_joined = date_joined
        conf_date = request.POST.get('confirmation_date')
        emp.confirmation_date = conf_date if conf_date else None

        manager_id = request.POST.get('manager_id')
        emp.manager_id = int(manager_id) if manager_id else None

        # Personal demographics
        emp.gender = request.POST.get('gender', emp.gender)
        dob = request.POST.get('date_of_birth')
        emp.date_of_birth = dob if dob else None
        emp.marital_status = request.POST.get('marital_status', emp.marital_status)
        emp.blood_group = request.POST.get('blood_group', emp.blood_group)
        emp.father_spouse_name = request.POST.get('father_spouse_name', emp.father_spouse_name)
        emp.emergency_contact_name = request.POST.get('emergency_contact_name', emp.emergency_contact_name)
        emp.emergency_contact_relation = request.POST.get('emergency_contact_relation', emp.emergency_contact_relation)
        emp.emergency_contact_phone = request.POST.get('emergency_contact_phone', emp.emergency_contact_phone)

        # Addresses
        emp.current_address = request.POST.get('current_address', emp.current_address)
        emp.current_city = request.POST.get('current_city', emp.current_city)
        emp.current_state = request.POST.get('current_state', emp.current_state)
        emp.current_pincode = request.POST.get('current_pincode', emp.current_pincode)
        emp.permanent_address = request.POST.get('permanent_address', emp.permanent_address)
        emp.permanent_city = request.POST.get('permanent_city', emp.permanent_city)
        emp.permanent_state = request.POST.get('permanent_state', emp.permanent_state)
        emp.permanent_pincode = request.POST.get('permanent_pincode', emp.permanent_pincode)

        # Identification & Statutory
        emp.pan_number = request.POST.get('pan_number', emp.pan_number).strip().upper()
        emp.aadhaar_number = request.POST.get('aadhaar_number', emp.aadhaar_number).strip()
        emp.passport_number = request.POST.get('passport_number', emp.passport_number).strip()
        emp.uan_number = request.POST.get('uan_number', emp.uan_number).strip()
        emp.pf_number = request.POST.get('pf_number', emp.pf_number).strip()
        emp.esic_number = request.POST.get('esic_number', emp.esic_number).strip()

        # Approver Matrices (Configurable per Employee - README 4.1)
        ts_appr = request.POST.get('timesheet_approver_id')
        emp.timesheet_approver_id = int(ts_appr) if ts_appr else None

        l1_appr = request.POST.get('leave_approver_l1_id')
        emp.leave_approver_l1_id = int(l1_appr) if l1_appr else None

        l2_appr = request.POST.get('leave_approver_l2_id')
        emp.leave_approver_l2_id = int(l2_appr) if l2_appr else None

        exp1_appr = request.POST.get('expense_approver_l1_id')
        emp.expense_approver_l1_id = int(exp1_appr) if exp1_appr else None

        exp2_appr = request.POST.get('expense_approver_l2_id')
        emp.expense_approver_l2_id = int(exp2_appr) if exp2_appr else None

        # Banking & Costing (CTC rate used for project profitability)
        emp.bank_name = request.POST.get('bank_name', emp.bank_name).strip()
        emp.bank_account_number = request.POST.get('bank_account_number', emp.bank_account_number).strip()
        emp.ifsc_code = request.POST.get('ifsc_code', emp.ifsc_code).strip()
        emp.bank_branch = request.POST.get('bank_branch', emp.bank_branch).strip()

        if is_admin or is_hr:
            hourly_cost = request.POST.get('hourly_cost')
            if hourly_cost is not None and hourly_cost != '':
                emp.hourly_cost = float(hourly_cost)
            annual_ctc = request.POST.get('annual_ctc')
            if annual_ctc is not None and annual_ctc != '':
                emp.annual_ctc = float(annual_ctc)

        if 'avatar' in request.FILES and request.FILES['avatar']:
            from django.core.files.storage import default_storage
            avatar_file = request.FILES['avatar']
            saved_path = default_storage.save(f"employee_avatars/{emp.id}_{avatar_file.name}", avatar_file)
            emp.avatar_url = default_storage.url(saved_path)

        emp.save()

        # Audit log in Chatter
        if current_user:
            try:
                from datetime import datetime
                MailMessage.objects.create(
                    model_name='hr.employee',
                    record_id=emp.id,
                    author=current_user,
                    message_type='note',
                    body=f"Profile modified on version '{datetime.now().strftime('%b %d, %Y')}'"
                )
            except Exception:
                pass

        messages.success(request, f"Employee '{emp.name}' updated successfully.")
        return redirect('employee_detail', emp_id=emp.id)

    # Pager calculation
    all_emp_ids = list(Employee.objects.filter(is_active=True).order_by('name').values_list('id', flat=True))
    current_index = all_emp_ids.index(emp.id) + 1 if emp.id in all_emp_ids else 1
    total_employees = len(all_emp_ids)
    prev_id = all_emp_ids[current_index - 2] if current_index > 1 else None
    next_id = all_emp_ids[current_index] if current_index < total_employees else None

    departments = Department.objects.filter(is_active=True).order_by('name')
    all_employees = Employee.objects.filter(is_active=True).exclude(id=emp.id).order_by('name')

    # Chatter Messages Feed
    messages_list = []
    try:
        raw_msgs = MailMessage.objects.filter(model_name='hr.employee', record_id=emp.id).select_related('author').order_by('-created_at')
        seen = set()
        for m in raw_msgs:
            key = (m.author_id, m.body.strip() if m.body else '', m.created_at.strftime('%Y-%m-%d %H:%M') if m.created_at else None)
            if key not in seen:
                seen.add(key)
                messages_list.append(m)

        if not messages_list and current_user:
            init_msg = MailMessage.objects.create(
                model_name='hr.employee',
                record_id=emp.id,
                author=current_user,
                message_type='note',
                body="Congratulations! May I recommend you to setup an onboarding plan?\nEmployee profile initialized."
            )
            messages_list.append(init_msg)
    except Exception:
        pass

    # Mini Organization Hierarchy Chain (Executive -> Manager -> Employee -> Directs)
    manager_chain = []
    curr = emp.manager
    visited = {emp.id}
    while curr and curr.id not in visited and len(manager_chain) < 4:
        visited.add(curr.id)
        manager_chain.insert(0, curr)
        curr = curr.manager

    direct_reports = list(emp.subordinates.filter(is_active=True).order_by('name')[:6])

    return render(request, 'employee/employee_detail.html', {
        'emp': emp,
        'departments': departments,
        'all_employees': all_employees,
        'current_index': current_index,
        'total_employees': total_employees,
        'prev_id': prev_id,
        'next_id': next_id,
        'messages_list': messages_list,
        'manager_chain': manager_chain,
        'direct_reports': direct_reports,
        'current_user': current_user,
        'is_admin': is_admin,
        'is_hr': is_hr,
        'is_self': is_self,
    })


@hr_officer_required
def employee_create(request):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user)
    is_hr = is_hr_manager_or_admin(current_user)

    if not is_hr:
        messages.error(request, "Permission Denied: Only HR Officers or Administrators can add employees.")
        return redirect('employee_list')

    templates = OnboardingTemplate.objects.filter(is_active=True).order_by('name')
    departments = Department.objects.filter(is_active=True).order_by('name')
    all_employees = Employee.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        employee_code = request.POST.get('employee_code', '').strip()
        date_joined = request.POST.get('date_joined')

        if not (name and email and employee_code and date_joined):
            messages.error(request, "Please fill in all mandatory fields (Name, Code, Email, Date Joined).")
            return render(request, 'employee/employee_create.html', {
                'templates': templates,
                'departments': departments,
                'all_employees': all_employees,
            })

        dept_id = request.POST.get('department_id')
        dept_obj = Department.objects.filter(id=dept_id).first() if dept_id else None

        emp = Employee.objects.create(
            name=name,
            employee_code=employee_code,
            email=email,
            phone=request.POST.get('phone', '').strip(),
            department_rel=dept_obj,
            department=dept_obj.name if dept_obj else request.POST.get('department', '').strip(),
            job_title=request.POST.get('job_title', '').strip(),
            date_joined=date_joined,
            branch=request.POST.get('branch', 'Pune HQ').strip(),
            employment_type=request.POST.get('employment_type', 'Full-Time').strip(),
            confirmation_date=request.POST.get('confirmation_date') or None,
            manager_id=int(request.POST['manager_id']) if request.POST.get('manager_id') else None,
            gender=request.POST.get('gender') or None,
            date_of_birth=request.POST.get('date_of_birth') or None,
            marital_status=request.POST.get('marital_status') or None,
            blood_group=request.POST.get('blood_group') or None,
            father_spouse_name=request.POST.get('father_spouse_name', '').strip(),
            emergency_contact_name=request.POST.get('emergency_contact_name', '').strip(),
            emergency_contact_relation=request.POST.get('emergency_contact_relation', '').strip(),
            emergency_contact_phone=request.POST.get('emergency_contact_phone', '').strip(),
            current_address=request.POST.get('current_address', '').strip(),
            current_city=request.POST.get('current_city', '').strip(),
            current_state=request.POST.get('current_state', '').strip(),
            current_pincode=request.POST.get('current_pincode', '').strip(),
            permanent_address=request.POST.get('permanent_address', '').strip(),
            permanent_city=request.POST.get('permanent_city', '').strip(),
            permanent_state=request.POST.get('permanent_state', '').strip(),
            permanent_pincode=request.POST.get('permanent_pincode', '').strip(),
            pan_number=request.POST.get('pan_number', '').strip().upper(),
            aadhaar_number=request.POST.get('aadhaar_number', '').strip(),
            passport_number=request.POST.get('passport_number', '').strip(),
            uan_number=request.POST.get('uan_number', '').strip(),
            pf_number=request.POST.get('pf_number', '').strip(),
            esic_number=request.POST.get('esic_number', '').strip(),
            timesheet_approver_id=int(request.POST['timesheet_approver_id']) if request.POST.get('timesheet_approver_id') else None,
            leave_approver_l1_id=int(request.POST['leave_approver_l1_id']) if request.POST.get('leave_approver_l1_id') else None,
            leave_approver_l2_id=int(request.POST['leave_approver_l2_id']) if request.POST.get('leave_approver_l2_id') else None,
            expense_approver_l1_id=int(request.POST['expense_approver_l1_id']) if request.POST.get('expense_approver_l1_id') else None,
            expense_approver_l2_id=int(request.POST['expense_approver_l2_id']) if request.POST.get('expense_approver_l2_id') else None,
            bank_name=request.POST.get('bank_name', '').strip(),
            bank_account_number=request.POST.get('bank_account_number', '').strip(),
            ifsc_code=request.POST.get('ifsc_code', '').strip(),
            bank_branch=request.POST.get('bank_branch', '').strip(),
            hourly_cost=float(request.POST['hourly_cost']) if request.POST.get('hourly_cost') else 0.00,
            annual_ctc=float(request.POST['annual_ctc']) if request.POST.get('annual_ctc') else 0.00,
        )

        if 'avatar' in request.FILES and request.FILES['avatar']:
            from django.core.files.storage import default_storage
            avatar_file = request.FILES['avatar']
            saved_path = default_storage.save(f"employee_avatars/{emp.id}_{avatar_file.name}", avatar_file)
            emp.avatar_url = default_storage.url(saved_path)
            emp.save(update_fields=['avatar_url'])
        messages.success(request, f"Employee '{emp.name}' ({emp.employee_code}) created successfully.")
        return redirect('employee_detail', emp_id=emp.id)

    return render(request, 'employee/employee_create.html', {
        'templates': templates,
        'departments': departments,
        'all_employees': all_employees,
        'current_user': current_user,
        'is_admin': is_admin,
        'is_hr': is_hr,
    })


@hr_officer_required
def department_list(request):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user)
    is_hr = is_hr_manager_or_admin(current_user)

    departments = Department.objects.filter(is_active=True).select_related('manager', 'parent').order_by('name')
    all_employees = Employee.objects.filter(is_active=True).order_by('name')

    return render(request, 'employee/department_list.html', {
        'departments': departments,
        'all_employees': all_employees,
        'current_user': current_user,
        'is_admin': is_admin,
        'is_hr': is_hr,
    })


@hr_officer_required
def department_create(request):
    current_user = get_current_ir_user(request)
    if not is_hr_manager_or_admin(current_user):
        messages.error(request, "Permission Denied: Only HR Managers can create departments.")
        return redirect('department_list')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        manager_id = request.POST.get('manager_id')
        parent_id = request.POST.get('parent_id')
        color = request.POST.get('color', '#0284c7').strip()

        if not name:
            messages.error(request, "Department name is required.")
            return redirect('department_list')

        dept = Department.objects.create(
            name=name,
            code=code or None,
            manager_id=int(manager_id) if manager_id else None,
            parent_id=int(parent_id) if parent_id else None,
            color=color,
        )
        messages.success(request, f"Department '{dept.name}' created successfully.")
        return redirect('department_detail', dept_id=dept.id)

    departments = Department.objects.filter(is_active=True).order_by('name')
    employees = Employee.objects.filter(is_active=True).order_by('name')
    return render(request, 'employee/department_form.html', {
        'dept': None,
        'departments': departments,
        'employees': employees,
    })


@hr_officer_required
def department_detail(request, dept_id):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user)
    is_hr = is_hr_manager_or_admin(current_user)

    dept = get_object_or_404(Department.objects.select_related('manager', 'parent'), id=dept_id)
    members = Employee.objects.filter(department_rel=dept, is_active=True).order_by('name')

    if request.method == 'POST':
        if not is_hr:
            messages.error(request, "Permission Denied: Only HR Managers can update departments.")
            return redirect('department_detail', dept_id=dept.id)

        dept.name = request.POST.get('name', dept.name).strip()
        dept.code = request.POST.get('code', dept.code).strip()
        manager_id = request.POST.get('manager_id')
        dept.manager_id = int(manager_id) if manager_id else None
        parent_id = request.POST.get('parent_id')
        dept.parent_id = int(parent_id) if parent_id else None
        dept.color = request.POST.get('color', dept.color).strip()
        dept.save()

        messages.success(request, f"Department '{dept.name}' updated successfully.")
        return redirect('department_detail', dept_id=dept.id)

    departments = Department.objects.filter(is_active=True).exclude(id=dept.id).order_by('name')
    employees = Employee.objects.filter(is_active=True).order_by('name')

    return render(request, 'employee/department_detail.html', {
        'dept': dept,
        'members': members,
        'departments': departments,
        'employees': employees,
        'current_user': current_user,
        'is_admin': is_admin,
        'is_hr': is_hr,
    })


@hr_officer_required
def employee_org_chart(request):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user)
    is_hr = is_hr_manager_or_admin(current_user)

    # Build hierarchy tree: root employees (no manager or reporting to self)
    all_employees = list(Employee.objects.filter(is_active=True).select_related('department_rel', 'manager').order_by('name'))

    emp_dict = {e.id: e for e in all_employees}
    children_map = {}
    roots = []

    for e in all_employees:
        children_map[e.id] = []

    for e in all_employees:
        if e.manager_id and e.manager_id in emp_dict and e.manager_id != e.id:
            children_map[e.manager_id].append(e)
        else:
            roots.append(e)

    # Attach children to root objects recursively for template rendering
    def attach_children(node):
        node.subordinate_nodes = children_map.get(node.id, [])
        for sub in node.subordinate_nodes:
            attach_children(sub)

    for r in roots:
        attach_children(r)

    return render(request, 'employee/org_chart.html', {
        'roots': roots,
        'total_employees': len(all_employees),
        'current_user': current_user,
        'is_admin': is_admin,
        'is_hr': is_hr,
    })


@hr_officer_required
def onboarding_templates(request):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user)
    is_hr = is_hr_manager_or_admin(current_user)

    templates = OnboardingTemplate.objects.filter(is_active=True).select_related(
        'department', 'timesheet_approver', 'leave_approver_l1', 'leave_approver_l2', 'expense_approver_l1', 'expense_approver_l2'
    ).order_by('name')

    return render(request, 'employee/onboarding_templates.html', {
        'templates': templates,
        'current_user': current_user,
        'is_admin': is_admin,
        'is_hr': is_hr,
    })


@hr_officer_required
def onboarding_template_create(request):
    current_user = get_current_ir_user(request)
    if not is_hr_manager_or_admin(current_user):
        messages.error(request, "Permission Denied: Only HR Managers can create onboarding templates.")
        return redirect('employee_onboarding_templates')

    departments = Department.objects.filter(is_active=True).order_by('name')
    employees = Employee.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, "Template name is required.")
            return redirect('employee_onboarding_template_create')

        tmpl = OnboardingTemplate.objects.create(
            name=name,
            department_id=int(request.POST['department_id']) if request.POST.get('department_id') else None,
            job_title=request.POST.get('job_title', '').strip(),
            employment_type=request.POST.get('employment_type', 'Full-Time').strip(),
            branch=request.POST.get('branch', 'Pune HQ').strip(),
            timesheet_approver_id=int(request.POST['timesheet_approver_id']) if request.POST.get('timesheet_approver_id') else None,
            leave_approver_l1_id=int(request.POST['leave_approver_l1_id']) if request.POST.get('leave_approver_l1_id') else None,
            leave_approver_l2_id=int(request.POST['leave_approver_l2_id']) if request.POST.get('leave_approver_l2_id') else None,
            expense_approver_l1_id=int(request.POST['expense_approver_l1_id']) if request.POST.get('expense_approver_l1_id') else None,
            expense_approver_l2_id=int(request.POST['expense_approver_l2_id']) if request.POST.get('expense_approver_l2_id') else None,
            checklist_notes=request.POST.get('checklist_notes', '').strip(),
        )
        messages.success(request, f"Onboarding template '{tmpl.name}' created successfully.")
        return redirect('employee_onboarding_templates')

    return render(request, 'employee/onboarding_template_form.html', {
        'tmpl': None,
        'departments': departments,
        'employees': employees,
    })


@hr_officer_required
def onboarding_template_detail(request, template_id):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user)
    is_hr = is_hr_manager_or_admin(current_user)

    tmpl = get_object_or_404(OnboardingTemplate, id=template_id)
    departments = Department.objects.filter(is_active=True).order_by('name')
    employees = Employee.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        if not is_hr:
            messages.error(request, "Permission Denied: Only HR Managers can modify onboarding templates.")
            return redirect('employee_onboarding_templates')

        tmpl.name = request.POST.get('name', tmpl.name).strip()
        tmpl.department_id = int(request.POST['department_id']) if request.POST.get('department_id') else None
        tmpl.job_title = request.POST.get('job_title', tmpl.job_title).strip()
        tmpl.employment_type = request.POST.get('employment_type', tmpl.employment_type).strip()
        tmpl.branch = request.POST.get('branch', tmpl.branch).strip()
        tmpl.timesheet_approver_id = int(request.POST['timesheet_approver_id']) if request.POST.get('timesheet_approver_id') else None
        tmpl.leave_approver_l1_id = int(request.POST['leave_approver_l1_id']) if request.POST.get('leave_approver_l1_id') else None
        tmpl.leave_approver_l2_id = int(request.POST['leave_approver_l2_id']) if request.POST.get('leave_approver_l2_id') else None
        tmpl.expense_approver_l1_id = int(request.POST['expense_approver_l1_id']) if request.POST.get('expense_approver_l1_id') else None
        tmpl.expense_approver_l2_id = int(request.POST['expense_approver_l2_id']) if request.POST.get('expense_approver_l2_id') else None
        tmpl.checklist_notes = request.POST.get('checklist_notes', tmpl.checklist_notes).strip()
        tmpl.save()

        messages.success(request, f"Onboarding template '{tmpl.name}' updated successfully.")
        return redirect('employee_onboarding_templates')

    return render(request, 'employee/onboarding_template_form.html', {
        'tmpl': tmpl,
        'departments': departments,
        'employees': employees,
        'current_user': current_user,
        'is_admin': is_admin,
        'is_hr': is_hr,
    })


@hr_officer_required
def api_template_details(request, template_id):
    """Returns template configuration JSON to pre-populate employee creation form."""
    tmpl = get_object_or_404(OnboardingTemplate, id=template_id)
    return JsonResponse({
        'id': tmpl.id,
        'name': tmpl.name,
        'department_id': tmpl.department_id,
        'job_title': tmpl.job_title or '',
        'employment_type': tmpl.employment_type or 'Full-Time',
        'branch': tmpl.branch or 'Pune HQ',
        'timesheet_approver_id': tmpl.timesheet_approver_id,
        'leave_approver_l1_id': tmpl.leave_approver_l1_id,
        'leave_approver_l2_id': tmpl.leave_approver_l2_id,
        'expense_approver_l1_id': tmpl.expense_approver_l1_id,
        'expense_approver_l2_id': tmpl.expense_approver_l2_id,
        'checklist_notes': tmpl.checklist_notes or '',
    })


@hr_officer_required
def employee_config_locations(request):
    current_user = get_current_ir_user(request)
    items = [
        {'name': 'Pune HQ - Hinjawadi Phase 1', 'extra_vals': ['Alpha Tower, Hinjawadi', 'Primary IT Campus']},
        {'name': 'Pune Magarpatta Hub', 'extra_vals': ['Tower 7, Magarpatta City', 'Development Wing']},
        {'name': 'Mumbai BKC Branch', 'extra_vals': ['Parinee Crescenzo, BKC', 'Client & BFSI Hub']},
        {'name': 'Work From Home (Remote)', 'extra_vals': ['Virtual / Pan India', 'Flexible Hybrid']},
    ]
    return render(request, 'employee/employee_configuration.html', {
        'config_category': 'Work Locations',
        'config_title': 'Work Locations',
        'config_item_name': 'Work Location',
        'extra_columns': ['Address', 'Type'],
        'items': items,
        'current_user': current_user,
        'is_admin': is_admin_user(current_user),
        'is_hr': is_hr_manager_or_admin(current_user),
    })


@hr_officer_required
def employee_config_schedules(request):
    current_user = get_current_ir_user(request)
    items = [
        {'name': 'Standard 40 Hours / Week', 'extra_vals': ['Mon-Fri (09:00 - 18:00)', '08:20 daily with breaks']},
        {'name': 'Flexible 45 Hours / Week', 'extra_vals': ['Mon-Fri (09:30 - 19:00)', '09:00 daily with breaks']},
        {'name': 'US Overlap Shift (Night)', 'extra_vals': ['Mon-Fri (18:00 - 03:00)', 'Night differential applicable']},
        {'name': 'Part-Time Schedule (20h)', 'extra_vals': ['Mon-Fri (10:00 - 14:00)', '4 hours daily']},
    ]
    return render(request, 'employee/employee_configuration.html', {
        'config_category': 'Working Schedules',
        'config_title': 'Working Schedules',
        'config_item_name': 'Working Schedule',
        'extra_columns': ['Working Time', 'Details'],
        'items': items,
        'current_user': current_user,
        'is_admin': is_admin_user(current_user),
        'is_hr': is_hr_manager_or_admin(current_user),
    })


@hr_officer_required
def employee_config_departure_reasons(request):
    current_user = get_current_ir_user(request)
    items = [
        {'name': 'Career Advancement & Higher Opportunity', 'extra_vals': ['Resignation']},
        {'name': 'Geographic Relocation', 'extra_vals': ['Resignation']},
        {'name': 'Higher Studies / Masters Degree', 'extra_vals': ['Education Leave / Resignation']},
        {'name': 'Health & Personal Circumstances', 'extra_vals': ['Medical / Personal']},
        {'name': 'Superannuation / Retirement', 'extra_vals': ['Retirement']},
    ]
    return render(request, 'employee/employee_configuration.html', {
        'config_category': 'Departure Reasons',
        'config_title': 'Departure Reasons',
        'config_item_name': 'Departure Reason',
        'extra_columns': ['Category'],
        'items': items,
        'current_user': current_user,
        'is_admin': is_admin_user(current_user),
        'is_hr': is_hr_manager_or_admin(current_user),
    })


@hr_officer_required
def employee_config_skills(request):
    current_user = get_current_ir_user(request)
    items = [
        {'name': 'Python & Django Architecture', 'extra_vals': ['Engineering', 'Backend & APIs']},
        {'name': 'React & Modern Frontend', 'extra_vals': ['Engineering', 'Web UI']},
        {'name': 'PostgreSQL & Database Design', 'extra_vals': ['Engineering', 'Database']},
        {'name': 'AWS Cloud & Kubernetes', 'extra_vals': ['DevOps', 'Infrastructure']},
        {'name': 'Figma & UI/UX Product Design', 'extra_vals': ['Product', 'Design']},
        {'name': 'Agile Scrum & Product Delivery', 'extra_vals': ['Management', 'Delivery']},
    ]
    return render(request, 'employee/employee_configuration.html', {
        'config_category': 'Skill Types',
        'config_title': 'Skill Types & Competencies',
        'config_item_name': 'Skill Type',
        'extra_columns': ['Domain', 'Level'],
        'items': items,
        'current_user': current_user,
        'is_admin': is_admin_user(current_user),
        'is_hr': is_hr_manager_or_admin(current_user),
    })

