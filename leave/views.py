import calendar
import json
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from base.auth_helpers import (
    get_current_ir_user,
    is_admin_user,
    login_required_ir,
    is_leave_officer_or_admin,
    get_user_linked_employee,
    is_approving_manager,
)
from base.search_metadata import (
    apply_group_by,
    get_favorites,
    get_operators_json,
)
from employee.models import Employee
from leave.models import LeaveType, LeaveAllocation, LeaveRequest, MandatoryDay


def leave_officer_required(view_func):
    """Decorator to restrict access strictly to Leave / Time Off Officers and Administrators."""
    @login_required_ir
    def _wrapped(request, *args, **kwargs):
        current_user = get_current_ir_user(request)
        if not is_leave_officer_or_admin(current_user):
            messages.error(request, "Access Restricted: This view is restricted to Time Off Officers and Administrators.")
            return redirect('leave_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def leave_manager_or_officer_required(view_func):
    """Decorator to restrict access to Approving Managers, Officers, and Administrators."""
    @login_required_ir
    def _wrapped(request, *args, **kwargs):
        current_user = get_current_ir_user(request)
        is_officer = is_leave_officer_or_admin(current_user)
        is_manager = is_approving_manager(current_user)
        if not is_officer and not is_manager:
            messages.error(request, "Access Restricted: Leave management approvals are restricted to Managers and Officers.")
            return redirect('my_time_off')
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required_ir
def leave_dashboard(request):
    """
    Overview Calendar Dashboard matching Odoo 17 Time Off screen recording.
    Displays month calendar with plotted leaves, today highlight, right-side balance quotas & public holidays.
    Regular employees see strictly their own leaves; Managers see their team's and their own; Officers see all.
    """
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)
    is_admin = is_admin_user(current_user) if current_user else False
    is_officer = is_leave_officer_or_admin(current_user)
    is_manager = is_approving_manager(current_user)

    # Date parsing (default to October 2026 matching system recording)
    year = int(request.GET.get('year', 2026))
    month = int(request.GET.get('month', 10))
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    month_days = cal.monthdatescalendar(year, month)
    today = date(2026, 10, 24)

    # Navigation months
    prev_month_date = date(year, month, 1) - timedelta(days=1)
    next_month_date = date(year, month, 28) + timedelta(days=5)

    # Fetch Leave Requests & Holidays in the visible window
    window_start = month_days[0][0]
    window_end = month_days[-1][-1]

    requests_qs = LeaveRequest.objects.filter(
        is_active=True,
        start_date__lte=window_end,
        end_date__gte=window_start
    ).select_related('employee', 'leave_type')

    # Record rule scoping per audio directive
    if not is_officer:
        if is_manager and current_emp:
            requests_qs = requests_qs.filter(
                Q(employee=current_emp) |
                Q(employee__manager=current_emp) |
                Q(employee__leave_approver_l1=current_emp) |
                Q(employee__leave_approver_l2=current_emp)
            )
        elif current_emp:
            requests_qs = requests_qs.filter(employee=current_emp)
        else:
            requests_qs = requests_qs.none()

    holidays = MandatoryDay.objects.filter(
        is_active=True,
        start_date__lte=window_end,
        end_date__gte=window_start
    )

    # Build calendar matrix
    calendar_weeks = []
    for week in month_days:
        week_days = []
        for d in week:
            is_in_month = (d.month == month)
            is_today = (d == today)
            
            # Find holidays for this day
            day_holidays = [h for h in holidays if h.start_date <= d <= h.end_date]
            # Find leaves for this day
            day_leaves = [
                r for r in requests_qs 
                if r.start_date <= d <= r.end_date
            ]

            week_days.append({
                'date': d,
                'day_num': d.day,
                'in_month': is_in_month,
                'is_today': is_today,
                'is_holiday': bool(day_holidays),
                'holidays': day_holidays,
                'leaves': day_leaves,
            })
        calendar_weeks.append(week_days)

    # Employee Balance Quotas for Right Sidebar
    leave_types = list(LeaveType.objects.filter(is_active=True).order_by('name'))
    balances = []
    for lt in leave_types:
        allocated = Decimal('0.00')
        taken = Decimal('0.00')
        if current_emp:
            allocated = LeaveAllocation.objects.filter(
                employee=current_emp,
                leave_type=lt,
                status='validate',
                is_active=True
            ).aggregate(total=Sum('allocated_days'))['total'] or Decimal('0.00')

            taken = LeaveRequest.objects.filter(
                employee=current_emp,
                leave_type=lt,
                status='validate',
                is_active=True
            ).aggregate(total=Sum('duration_days'))['total'] or Decimal('0.00')

        available = max(Decimal('0.00'), allocated - taken)
        balances.append({
            'type': lt,
            'allocated': allocated,
            'taken': taken,
            'available': available,
        })

    upcoming_holidays = MandatoryDay.objects.filter(
        is_active=True,
        start_date__gte=today
    ).order_by('start_date')[:5]

    if is_officer:
        all_employees = Employee.objects.filter(is_active=True).order_by('name')
    elif is_manager and current_emp:
        all_employees = Employee.objects.filter(
            Q(id=current_emp.id) |
            Q(manager=current_emp) |
            Q(leave_approver_l1=current_emp) |
            Q(leave_approver_l2=current_emp),
            is_active=True
        ).order_by('name')
    elif current_emp:
        all_employees = [current_emp]
    else:
        all_employees = []

    return render(request, 'leave/leave_dashboard.html', {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'prev_month': prev_month_date.month,
        'prev_year': prev_month_date.year,
        'next_month': next_month_date.month,
        'next_year': next_month_date.year,
        'calendar_weeks': calendar_weeks,
        'balances': balances,
        'upcoming_holidays': upcoming_holidays,
        'current_emp': current_emp,
        'all_employees': all_employees,
        'leave_types': leave_types,
        'current_user': current_user,
        'is_admin': is_admin,
        'is_officer': is_officer,
        'is_manager': is_manager,
        'is_officer_or_manager': is_officer or is_manager,
    })


@leave_manager_or_officer_required
def leave_management_requests(request):
    """
    Management > Time Off: Kanban & List view with diagonal ribbons and 1-click approvals.
    Uses Universal Search Panel metadata (search_model_key="hr.leave").
    Scoped strictly to team for Managers, and company for Officers.
    """
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)
    is_admin = is_admin_user(current_user) if current_user else False
    is_officer = is_leave_officer_or_admin(current_user)
    is_manager = is_approving_manager(current_user)

    view_mode = request.GET.get('view_mode', 'kanban')
    filter_mode = request.GET.get('filter', 'all')
    search_q = request.GET.get('q', '').strip()
    group_by_field = request.GET.get('group_by', '').strip()
    if not group_by_field and view_mode == 'kanban':
        group_by_field = 'status'

    qs = LeaveRequest.objects.filter(is_active=True).select_related('employee', 'leave_type', 'approved_by')

    # Manager vs Officer scoping
    if not is_officer and current_emp:
        qs = qs.filter(
            Q(employee__manager=current_emp) |
            Q(employee__leave_approver_l1=current_emp) |
            Q(employee__leave_approver_l2=current_emp)
        )

    # Quick Filter Pills
    if filter_mode == 'to_approve':
        qs = qs.filter(Q(status='confirm') | Q(status='Pending'))
    elif filter_mode == 'approved':
        qs = qs.filter(Q(status='validate') | Q(status='Approved'))
    elif filter_mode == 'refused':
        qs = qs.filter(Q(status='refuse') | Q(status='Rejected'))

    # Free text search
    if search_q:
        qs = qs.filter(
            Q(employee__name__icontains=search_q) |
            Q(leave_type__name__icontains=search_q) |
            Q(reason__icontains=search_q)
        )

    # Domain filtering if passed as JSON
    raw_domain = request.GET.get('domain')
    domain = []
    if raw_domain:
        try:
            domain = json.loads(raw_domain)
            for condition in domain:
                if len(condition) == 3:
                    f, op, val = condition
                    if op in ('=', '=='):
                        qs = qs.filter(**{f: val})
                    elif op == 'ilike':
                        qs = qs.filter(**{f"{f}__icontains": val})
        except Exception:
            pass

    records = list(qs.order_by('-start_date'))

    base_count_qs = LeaveRequest.objects.filter(is_active=True)
    if not is_officer and current_emp:
        base_count_qs = base_count_qs.filter(
            Q(employee__manager=current_emp) |
            Q(employee__leave_approver_l1=current_emp) |
            Q(employee__leave_approver_l2=current_emp)
        )
    to_approve_count = base_count_qs.filter(Q(status='confirm') | Q(status='Pending')).count()
    approved_count = base_count_qs.filter(Q(status='validate') | Q(status='Approved')).count()

    groups = apply_group_by(records, group_by_field) if group_by_field else None

    # Search panel metadata
    default_filterable = [
        {'name': 'employee__name', 'label': 'Employee', 'field_type': 'VARCHAR'},
        {'name': 'leave_type__name', 'label': 'Time Off Type', 'field_type': 'VARCHAR'},
        {'name': 'status', 'label': 'Status', 'field_type': 'VARCHAR'},
        {'name': 'start_date', 'label': 'Start Date', 'field_type': 'DATE'},
        {'name': 'duration_days', 'label': 'Duration (Days)', 'field_type': 'DECIMAL'},
    ]
    default_groupable = [
        {'name': 'employee.name', 'label': 'Employee'},
        {'name': 'leave_type.name', 'label': 'Time Off Type'},
        {'name': 'status', 'label': 'Status'},
    ]
    favorites = get_favorites(request, model_key='hr.leave')

    return render(request, 'leave/leave_management_requests.html', {
        'requests': records,
        'groups': groups,
        'total_count': len(records),
        'to_approve_count': to_approve_count,
        'approved_count': approved_count,
        'view_mode': view_mode,
        'filter_mode': filter_mode,
        'search_q': search_q,
        'active_group_by': group_by_field,
        'search_model_key': 'hr.leave',
        'create_url': reverse('leave_request_create') if (is_officer or is_manager) else None,
        'filterable_fields': default_filterable,
        'groupable_fields': default_groupable,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'operators_by_type_json': get_operators_json(),
        'current_user': current_user,
        'is_admin': is_admin,
        'is_officer': is_officer,
        'is_manager': is_manager,
        'is_officer_or_manager': is_officer or is_manager,
    })


@leave_manager_or_officer_required
def leave_request_action(request, request_id):
    """
    1-Click Validate / Refuse action for Leave Requests.
    Scoped to supervisees for managers, or all for officers.
    """
    leave_req = get_object_or_404(LeaveRequest, id=request_id)
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)
    is_officer = is_leave_officer_or_admin(current_user)

    if not is_officer:
        is_subordinate = current_emp and (
            leave_req.employee.manager_id == current_emp.id or
            leave_req.employee.leave_approver_l1_id == current_emp.id or
            leave_req.employee.leave_approver_l2_id == current_emp.id
        )
        if not is_subordinate:
            messages.error(request, "Permission Denied: You may only approve leave for employees under your supervision.")
            return redirect('leave_management_requests')

    action = request.POST.get('action') or request.GET.get('action')

    if action == 'validate':
        leave_req.status = 'validate'
        leave_req.approved_by = current_emp
        leave_req.save()
        messages.success(request, f"Leave request for {leave_req.employee.name} approved.")
    elif action == 'refuse':
        refusal_reason = request.POST.get('refusal_reason', 'Operational workload')
        leave_req.status = 'refuse'
        leave_req.refusal_reason = refusal_reason
        leave_req.save()
        messages.warning(request, f"Leave request for {leave_req.employee.name} refused.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'success', 'new_status': leave_req.status, 'status_label': leave_req.status_label})

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('leave_management_requests')
    return redirect(next_url)


@login_required_ir
def leave_request_create(request):
    """
    Form view to submit or request Time Off.
    Regular employees can submit only for themselves; officers can submit for any employee.
    """
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)
    is_officer = is_leave_officer_or_admin(current_user)
    is_manager = is_approving_manager(current_user)

    if request.method == 'POST':
        if not is_officer:
            emp = current_emp
            if not emp:
                messages.error(request, "Your user account is not linked to an employee profile.")
                return redirect('my_time_off')
        else:
            employee_id = request.POST.get('employee_id')
            emp = get_object_or_404(Employee, id=employee_id)

        leave_type_id = request.POST.get('leave_type_id')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        duration = request.POST.get('duration_days', '1.0')
        reason = request.POST.get('reason', '').strip()

        lt = get_object_or_404(LeaveType, id=leave_type_id)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            duration_days = Decimal(duration)
        except Exception as e:
            messages.error(request, f"Invalid date or duration: {e}")
            return redirect('leave_request_create')

        LeaveRequest.objects.create(
            employee=emp,
            leave_type=lt,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            reason=reason,
            status='confirm'
        )
        messages.success(request, f"Time off request submitted for {emp.name}.")
        if is_officer or is_manager:
            return redirect('leave_management_requests')
        else:
            return redirect('my_time_off')

    if is_officer:
        employees = Employee.objects.filter(is_active=True).order_by('name')
    elif is_manager and current_emp:
        employees = Employee.objects.filter(
            Q(id=current_emp.id) |
            Q(manager=current_emp) |
            Q(leave_approver_l1=current_emp) |
            Q(leave_approver_l2=current_emp),
            is_active=True
        ).order_by('name')
    elif current_emp:
        employees = [current_emp]
    else:
        employees = []

    return render(request, 'leave/leave_request_form.html', {
        'employees': employees,
        'leave_types': LeaveType.objects.filter(is_active=True).order_by('name'),
        'current_emp': current_emp,
        'current_user': current_user,
        'is_officer': is_officer,
        'is_manager': is_manager,
        'is_officer_or_manager': is_officer or is_manager,
    })


@leave_manager_or_officer_required
def leave_management_allocations(request):
    """
    Management > Allocations: Allocation approval workflow.
    """
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)
    is_officer = is_leave_officer_or_admin(current_user)
    is_manager = is_approving_manager(current_user)

    allocations = LeaveAllocation.objects.filter(is_active=True).select_related('employee', 'leave_type', 'approver')

    if not is_officer and current_emp:
        allocations = allocations.filter(
            Q(employee__manager=current_emp) |
            Q(employee__leave_approver_l1=current_emp) |
            Q(employee__leave_approver_l2=current_emp)
        )

    filter_mode = request.GET.get('filter', 'all')
    if filter_mode == 'to_approve':
        allocations = allocations.filter(status='confirm')
    elif filter_mode == 'approved':
        allocations = allocations.filter(status='validate')

    return render(request, 'leave/leave_management_allocations.html', {
        'allocations': allocations,
        'total_count': allocations.count(),
        'filter_mode': filter_mode,
        'search_model_key': 'hr.leave.allocation',
        'create_url': reverse('leave_allocation_create') if is_officer else None,
        'current_user': current_user,
        'is_admin': is_admin_user(current_user) if current_user else False,
        'is_officer': is_officer,
        'is_manager': is_manager,
        'is_officer_or_manager': is_officer or is_manager,
    })


@leave_manager_or_officer_required
def leave_allocation_action(request, allocation_id):
    """
    Validate or refuse an allocation.
    """
    alloc = get_object_or_404(LeaveAllocation, id=allocation_id)
    action = request.POST.get('action') or request.GET.get('action')
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)
    is_officer = is_leave_officer_or_admin(current_user)

    if not is_officer:
        is_subordinate = current_emp and (
            alloc.employee.manager_id == current_emp.id or
            alloc.employee.leave_approver_l1_id == current_emp.id or
            alloc.employee.leave_approver_l2_id == current_emp.id
        )
        if not is_subordinate:
            messages.error(request, "Permission Denied: You may only manage allocations for your direct supervisees.")
            return redirect('leave_management_allocations')

    if action == 'validate':
        alloc.status = 'validate'
        alloc.approver = current_emp
        alloc.save()
        messages.success(request, f"Allocation for {alloc.employee.name} approved.")
    elif action == 'refuse':
        alloc.status = 'refuse'
        alloc.save()
        messages.warning(request, f"Allocation for {alloc.employee.name} refused.")

    return redirect('leave_management_allocations')


@leave_officer_required
def leave_allocation_create(request):
    """
    Grant or request a new leave allocation. Restricted strictly to Officers and Administrators.
    """
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        leave_type_id = request.POST.get('leave_type_id')
        name = request.POST.get('name', 'Allocation')
        allocated_days = Decimal(request.POST.get('allocated_days', '15.0'))
        notes = request.POST.get('notes', '')

        emp = get_object_or_404(Employee, id=employee_id)
        lt = get_object_or_404(LeaveType, id=leave_type_id)

        LeaveAllocation.objects.create(
            name=name,
            employee=emp,
            leave_type=lt,
            allocated_days=allocated_days,
            notes=notes,
            status='validate',
            approver=current_emp
        )
        messages.success(request, f"Allocated {allocated_days} days to {emp.name}.")
        return redirect('leave_management_allocations')

    return render(request, 'leave/leave_allocation_form.html', {
        'employees': Employee.objects.filter(is_active=True).order_by('name'),
        'leave_types': LeaveType.objects.filter(is_active=True).order_by('name'),
        'current_user': current_user,
    })


@login_required_ir
def my_time_off(request):
    """My Time > My Time Off: List of requests for the current user."""
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)
    if current_emp:
        requests_list = LeaveRequest.objects.filter(employee=current_emp, is_active=True).order_by('-start_date')
    else:
        requests_list = LeaveRequest.objects.none()
    return render(request, 'leave/my_time_off.html', {
        'requests': requests_list,
        'current_emp': current_emp,
        'current_user': current_user,
    })


@login_required_ir
def my_allocations(request):
    """My Time > My Allocations: List of balances and allocations for current user."""
    current_user = get_current_ir_user(request)
    current_emp = get_user_linked_employee(current_user)
    if current_emp:
        allocations = LeaveAllocation.objects.filter(employee=current_emp, is_active=True).order_by('-created_at')
    else:
        allocations = LeaveAllocation.objects.none()
    return render(request, 'leave/my_allocations.html', {
        'allocations': allocations,
        'current_emp': current_emp,
        'current_user': current_user,
    })


@leave_officer_required
def reporting_by_employee(request):
    """Reporting > by Employee."""
    current_user = get_current_ir_user(request)
    employees = Employee.objects.filter(is_active=True).order_by('name')
    report_rows = []
    for emp in employees:
        total_taken = LeaveRequest.objects.filter(employee=emp, status='validate', is_active=True).aggregate(t=Sum('duration_days'))['t'] or Decimal('0.00')
        total_alloc = LeaveAllocation.objects.filter(employee=emp, status='validate', is_active=True).aggregate(t=Sum('allocated_days'))['t'] or Decimal('0.00')
        report_rows.append({
            'employee': emp,
            'allocated': total_alloc,
            'taken': total_taken,
            'balance': max(Decimal('0.00'), total_alloc - total_taken)
        })

    return render(request, 'leave/reporting_by_employee.html', {
        'rows': report_rows,
        'current_user': current_user,
    })


@leave_officer_required
def reporting_by_type(request):
    """Reporting > by Type."""
    current_user = get_current_ir_user(request)
    types = LeaveType.objects.filter(is_active=True).order_by('name')
    report_rows = []
    for lt in types:
        total_taken = LeaveRequest.objects.filter(leave_type=lt, status='validate', is_active=True).aggregate(t=Sum('duration_days'))['t'] or Decimal('0.00')
        requests_count = LeaveRequest.objects.filter(leave_type=lt, is_active=True).count()
        report_rows.append({
            'type': lt,
            'total_taken': total_taken,
            'requests_count': requests_count
        })

    return render(request, 'leave/reporting_by_type.html', {
        'rows': report_rows,
        'current_user': current_user,
    })


@leave_officer_required
def configuration_types(request):
    """Configuration > Time Off Types."""
    current_user = get_current_ir_user(request)
    leave_types = LeaveType.objects.filter(is_active=True).order_by('name')
    return render(request, 'leave/configuration_types.html', {
        'types': leave_types,
        'search_model_key': 'hr.leave.type',
        'create_url': reverse('leave_type_create'),
        'current_user': current_user,
        'is_admin': is_admin_user(current_user) if current_user else False,
    })


@leave_officer_required
def leave_type_create(request):
    """Create a new Time Off Type."""
    current_user = get_current_ir_user(request)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', 'PTO').strip()
        color = request.POST.get('color', '#10b981')
        take_time_off_in = request.POST.get('take_time_off_in', 'day')
        requires_allocation = request.POST.get('requires_allocation') == 'on'
        approval_type = request.POST.get('approval_type', 'officer')
        max_days = int(request.POST.get('max_days_per_year', 15))

        if name:
            LeaveType.objects.create(
                name=name,
                code=code,
                color=color,
                take_time_off_in=take_time_off_in,
                requires_allocation=requires_allocation,
                approval_type=approval_type,
                max_days_per_year=max_days
            )
            messages.success(request, f"Time off type '{name}' created.")
            return redirect('leave_config_types')

    return render(request, 'leave/leave_type_form.html', {
        'current_user': current_user,
    })


@leave_officer_required
def configuration_mandatory_days(request):
    """Configuration > Public Holidays & Mandatory Days."""
    current_user = get_current_ir_user(request)
    mandatory_days = MandatoryDay.objects.filter(is_active=True).order_by('start_date')
    return render(request, 'leave/configuration_mandatory_days.html', {
        'days': mandatory_days,
        'search_model_key': 'hr.leave.mandatory.day',
        'create_url': reverse('leave_mandatory_day_create'),
        'current_user': current_user,
        'is_admin': is_admin_user(current_user) if current_user else False,
    })


@leave_officer_required
def mandatory_day_create(request):
    """Create a new Public Holiday / Mandatory Day."""
    current_user = get_current_ir_user(request)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        color = request.POST.get('color', '#8b5cf6')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        notes = request.POST.get('notes', '')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            MandatoryDay.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date,
                color=color,
                is_mandatory=is_mandatory,
                notes=notes
            )
            messages.success(request, f"Public Holiday '{name}' added.")
            return redirect('leave_config_mandatory_days')
        except Exception as e:
            messages.error(request, f"Failed to add holiday: {e}")

    return render(request, 'leave/mandatory_day_form.html', {
        'current_user': current_user,
    })
