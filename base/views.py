import csv
import io
import json
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

from base.models import (
    IrModel, IrModelFields, IrUiMenu, IrFilters, IrUiView,
    IrSequence, IrModelAccess, IrRule, ResUsers, ResGroups,
    ResCompany, ResPartner, IrActions, IrModelRelation, IrModule,
    IrCron, ResUsersGroups, ResPrivilege, MailMessage,
    ReportPaperformat, IrActionsReport, MailActivityType,
    MailActivity, MailChannel, IrMailServer, IrConfigParameter,
    IrLogging, extract_diagnostics_from_exception
)
try:
    from employee.models import Employee, Department
except ImportError:
    Employee = None
    Department = None

try:
    from attendance.models import Attendance
except ImportError:
    Attendance = None

try:
    from leave.models import LeaveRequest, LeaveAllocation, LeaveType, MandatoryDay
except ImportError:
    LeaveRequest = None
    LeaveAllocation = None
    LeaveType = None
    MandatoryDay = None

from base.auth_helpers import (
    get_current_ir_user, login_user, logout_user,
    hash_password, verify_password, login_required_ir,
    is_admin_user, admin_required_ir, has_privilege_role,
    is_hr_officer_or_admin, is_attendance_officer_or_admin,
    is_leave_officer_or_admin, get_user_linked_employee,
    is_approving_manager
)
from base.search_metadata import (
    get_search_metadata,
    apply_search,
    apply_group_by,
    get_favorites,
    get_operators_json,
    get_relation_model_choices,
    get_django_model,
)

MODEL_CLASS_MAP = {
    'res.users': ResUsers,
    'res.groups': ResGroups,
    'res.privilege': ResPrivilege,
    'res.company': ResCompany,
    'res.partner': ResPartner,
    'hr.employee': Employee,
    'hr.attendance': Attendance,
    'attendance': Attendance,
    'mail.message': MailMessage,
    'mail.activity.type': MailActivityType,
    'mail.activity': MailActivity,
    'mail.channel': MailChannel,
    'ir.mail_server': IrMailServer,
    'ir.config_parameter': IrConfigParameter,
    'ir.model': IrModel,
    'ir.model.fields': IrModelFields,
    'ir.ui.view': IrUiView,
    'ir.ui.menu': IrUiMenu,
    'ir.sequence': IrSequence,
    'ir.model.access': IrModelAccess,
    'ir.rule': IrRule,
    'ir.actions.act_window': IrActions,
    'ir.cron': IrCron,
    'ir.model.relation': IrModelRelation,
    'report.paperformat': ReportPaperformat,
    'ir.actions.report': IrActionsReport,
    'ir.logging': IrLogging,
    'hr.leave': LeaveRequest,
    'leave': LeaveRequest,
    'hr.leave.allocation': LeaveAllocation,
    'leave.allocation': LeaveAllocation,
    'hr.leave.type': LeaveType,
    'leave.type': LeaveType,
    'hr.leave.mandatory.day': MandatoryDay,
}


def user_can_delete_model(user, model_name):
    """
    Evaluates if user has delete permission (perm_unlink / can_delete) for a model.
    Administrators always have delete permission.
    Level 1 / restricted users return False.
    """
    if not user:
        return False
    if is_admin_user(user):
        return True
    
    try:
        ir_model = IrModel.objects.filter(model_name=model_name).first()
        if not ir_model:
            return False
        
        user_groups = ResUsersGroups.objects.filter(user=user, is_active=True).values_list('group_id', flat=True)
        return IrModelAccess.objects.filter(
            model=ir_model,
            group_id__in=user_groups,
            can_delete=True,
            is_active=True
        ).exists()
    except Exception:
        return False


def _resolve_model(model_key):
    if not model_key:
        return None
    model_cls = MODEL_CLASS_MAP.get(model_key)
    if model_cls:
        return model_cls
    ir_model = IrModel.objects.filter(model_name=model_key).first()
    if ir_model:
        return get_django_model(ir_model)
    return None


@require_POST
@login_required_ir
def kanban_move_card(request):
    """
    Universal Drag-and-Drop Kanban API:
    Allows moving record cards from one column to another when grouped.
    Dynamically updates the underlying field (e.g. department, status, stage)
    and persists changes to the database.
    """
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    model_key = data.get('model_key') or data.get('model')
    record_id = data.get('record_id')
    field_name = data.get('field_name') or data.get('group_by')
    new_value = data.get('new_value')

    if not record_id or not field_name:
        return JsonResponse({'success': False, 'error': 'Missing record_id or field_name.'}, status=400)

    try:
        record_id = int(record_id)
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid record_id.'}, status=400)

    # 1. Specialized handling for Employee model
    if model_key in ('hr.employee', 'employee', 'Employee'):
        if Employee is None:
            return JsonResponse({'success': False, 'error': 'Employee module unavailable.'}, status=500)
        emp = Employee.objects.filter(id=record_id).first()
        if not emp:
            return JsonResponse({'success': False, 'error': f'Employee #{record_id} not found.'}, status=404)

        current_user = get_current_ir_user(request)
        if not (is_admin_user(current_user) or is_hr_officer_or_admin(current_user)):
            return JsonResponse({'success': False, 'error': 'Permission denied: HR Officer role required to move employee records.'}, status=403)

        new_val_str = str(new_value).strip() if new_value is not None else ''

        if field_name in ('department', 'department_rel', 'department_id'):
            dept = None
            if new_val_str.isdigit():
                dept = Department.objects.filter(id=int(new_val_str)).first() if Department else None
            if not dept and Department:
                dept = Department.objects.filter(name__iexact=new_val_str).first()
            if dept:
                emp.department = dept.name
                emp.department_rel = dept
            else:
                emp.department = new_val_str
                emp.department_rel = None
            emp.save(update_fields=['department', 'department_rel'])
            return JsonResponse({
                'success': True,
                'message': f"Updated {emp.name}'s department to {emp.department}",
                'record_id': emp.id,
                'field_name': field_name,
                'new_value': emp.department,
                'display_label': emp.department
            })

        elif field_name == 'job_title':
            emp.job_title = new_val_str
            emp.save(update_fields=['job_title'])
            return JsonResponse({
                'success': True,
                'message': f"Updated {emp.name}'s job position to {emp.job_title}",
                'record_id': emp.id,
                'new_value': emp.job_title
            })

        elif field_name == 'employment_type':
            emp.employment_type = new_val_str
            emp.save(update_fields=['employment_type'])
            return JsonResponse({
                'success': True,
                'message': f"Updated {emp.name}'s employment type to {emp.employment_type}",
                'record_id': emp.id,
                'new_value': emp.employment_type
            })

        elif field_name == 'branch':
            emp.branch = new_val_str
            emp.save(update_fields=['branch'])
            return JsonResponse({
                'success': True,
                'message': f"Updated {emp.name}'s branch to {emp.branch}",
                'record_id': emp.id,
                'new_value': emp.branch
            })

        elif field_name in ('manager', 'manager_id'):
            mgr = None
            if new_val_str.isdigit():
                mgr = Employee.objects.filter(id=int(new_val_str)).first()
            if not mgr:
                mgr = Employee.objects.filter(name__iexact=new_val_str).first()
            emp.manager = mgr
            emp.save(update_fields=['manager'])
            return JsonResponse({
                'success': True,
                'message': f"Updated {emp.name}'s manager to {mgr.name if mgr else 'None'}",
                'record_id': emp.id,
                'new_value': mgr.name if mgr else ''
            })

        elif hasattr(emp, field_name):
            setattr(emp, field_name, new_val_str)
            emp.save(update_fields=[field_name])
            return JsonResponse({
                'success': True,
                'message': f"Updated {emp.name}'s {field_name} to {new_val_str}",
                'record_id': emp.id,
                'new_value': new_val_str
            })

    # 2. Specialized handling for Leave Request model
    elif model_key in ('hr.leave', 'leave', 'LeaveRequest'):
        if LeaveRequest is None:
            return JsonResponse({'success': False, 'error': 'Leave module unavailable.'}, status=500)
        req_obj = LeaveRequest.objects.filter(id=record_id).first()
        if not req_obj:
            return JsonResponse({'success': False, 'error': f'Leave request #{record_id} not found.'}, status=404)

        new_val_str = str(new_value).strip() if new_value is not None else ''

        if field_name == 'status':
            current_user = get_current_ir_user(request)
            current_emp = get_user_linked_employee(current_user)

            val_lower = new_val_str.lower()
            status_map = {
                'to approve': 'confirm',
                'confirm': 'confirm',
                'pending': 'confirm',
                'approved': 'validate',
                'validate': 'validate',
                'refused': 'refuse',
                'refuse': 'refuse',
                'rejected': 'refuse',
                'draft': 'draft',
            }
            mapped_status = status_map.get(val_lower, val_lower)
            req_obj.status = mapped_status
            update_fields = ['status']
            if mapped_status == 'validate':
                req_obj.approved_by = current_emp
                update_fields.append('approved_by')
            elif mapped_status == 'confirm':
                req_obj.approved_by = None
                update_fields.append('approved_by')
            elif mapped_status == 'refuse':
                if not req_obj.refusal_reason:
                    req_obj.refusal_reason = 'Refused via Kanban board'
                    update_fields.append('refusal_reason')

            req_obj.save(update_fields=update_fields)
            return JsonResponse({
                'success': True,
                'message': f"Leave status updated to {req_obj.status_label}",
                'record_id': req_obj.id,
                'new_value': mapped_status,
                'display_label': req_obj.status_label
            })

        elif field_name in ('leave_type', 'leave_type_id'):
            lt = None
            if new_val_str.isdigit():
                lt = LeaveType.objects.filter(id=int(new_val_str)).first() if LeaveType else None
            if not lt and LeaveType:
                lt = LeaveType.objects.filter(name__iexact=new_val_str).first()
            if lt:
                req_obj.leave_type = lt
                req_obj.save(update_fields=['leave_type'])
                return JsonResponse({
                    'success': True,
                    'message': f"Leave type updated to {lt.name}",
                    'record_id': req_obj.id,
                    'new_value': lt.name,
                    'display_label': lt.name
                })

    # 3. Generic model fallback
    model_cls = _resolve_model(model_key)
    if model_cls:
        record = model_cls.objects.filter(id=record_id).first()
        if not record:
            return JsonResponse({'success': False, 'error': f'Record #{record_id} not found.'}, status=404)
        if hasattr(record, field_name):
            setattr(record, field_name, new_value)
            record.save(update_fields=[field_name])
            return JsonResponse({
                'success': True,
                'message': f'Record updated successfully.',
                'record_id': record_id,
                'new_value': str(new_value)
            })

    return JsonResponse({'success': False, 'error': f'Unsupported model or field ({model_key}.{field_name}).'}, status=400)


def batch_action(request):
    """
    Unified batch action processor for all list views:
    - Export (XLSX or CSV)
    - Duplicate
    - Archive (is_active = False)
    - Unarchive (is_active = True)
    - Delete (with strict user role & model permission checks)
    """
    current_user = get_current_ir_user(request)
    if not current_user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    if request.method == 'GET':
        action = request.GET.get('action')
        model_key = request.GET.get('model_key') or request.GET.get('model')
        raw_ids = request.GET.get('ids', '')
        ids = [int(i.strip()) for i in raw_ids.split(',') if i.strip().isdigit()]

        model_cls = _resolve_model(model_key)
        if not model_cls:
            return HttpResponse('Invalid model specified.', status=400)

        records_qs = model_cls.objects.filter(id__in=ids) if ids else model_cls.objects.all()

        fields = [f for f in model_cls._meta.fields if f.name != 'password_hash']
        headers = [f.verbose_name.title() if hasattr(f, 'verbose_name') else f.name.replace('_', ' ').title() for f in fields]

        if action == 'export_csv':
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            clean_name = (model_key or 'records').replace('.', '_')
            response['Content-Disposition'] = f'attachment; filename="{clean_name}_export.csv"'
            writer = csv.writer(response)
            writer.writerow(headers)
            for rec in records_qs:
                row = []
                for f in fields:
                    val = getattr(rec, f.name, '')
                    row.append(str(val) if val is not None else '')
                writer.writerow(row)
            return response

        elif action == 'export_xlsx':
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = (model_key or 'Export')[:31]

            header_fill = PatternFill(start_color='714B67', end_color='714B67', fill_type='solid')
            header_font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
            header_align = Alignment(horizontal='left', vertical='center')

            ws.append(headers)
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_align

            for rec in records_qs:
                row = []
                for f in fields:
                    val = getattr(rec, f.name, '')
                    row.append(str(val) if val is not None else '')
                ws.append(row)

            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

            out = io.BytesIO()
            wb.save(out)
            out.seek(0)

            response = HttpResponse(out.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            clean_name = (model_key or 'records').replace('.', '_')
            response['Content-Disposition'] = f'attachment; filename="{clean_name}_export.xlsx"'
            return response

        return HttpResponse('Unknown action.', status=400)

    elif request.method == 'POST':
        action = request.POST.get('action')
        model_key = request.POST.get('model_key') or request.POST.get('model')

        model_cls = _resolve_model(model_key)
        if not model_cls:
            return JsonResponse({'status': 'error', 'message': f'Model "{model_key}" not recognized.'}, status=400)

        if action == 'import_records':
            import_file = request.FILES.get('import_file')
            if not import_file:
                return JsonResponse({'status': 'error', 'message': 'Please choose a file to import.'}, status=400)

            file_name = import_file.name.lower()
            has_header = request.POST.get('has_header') in ('true', 'on', '1', True)
            created_count = 0

            try:
                valid_fields = {f.name: f for f in model_cls._meta.fields if f.name not in ('id', 'pk', 'password_hash')}
                
                if file_name.endswith('.csv'):
                    content = import_file.read()
                    try:
                        decoded_file = content.decode('utf-8-sig').splitlines()
                    except UnicodeDecodeError:
                        decoded_file = content.decode('latin-1').splitlines()

                    reader = csv.reader(decoded_file)
                    rows = list(reader)
                    if not rows:
                        return JsonResponse({'status': 'error', 'message': 'The CSV file is empty.'}, status=400)

                    headers = [h.strip().lower().replace(' ', '_') for h in rows[0]] if has_header else []
                    data_rows = rows[1:] if has_header else rows

                    for row in data_rows:
                        if not row or not any(row):
                            continue
                        kwargs = {}
                        for idx, cell_val in enumerate(row):
                            if idx < len(headers):
                                field_name = headers[idx]
                                if field_name in valid_fields and cell_val != '':
                                    kwargs[field_name] = cell_val.strip()
                        if kwargs:
                            model_cls.objects.create(**kwargs)
                            created_count += 1

                elif file_name.endswith(('.xlsx', '.xls')):
                    wb = openpyxl.load_workbook(import_file, data_only=True)
                    ws = wb.active
                    rows = list(ws.iter_rows(values_only=True))
                    if not rows:
                        return JsonResponse({'status': 'error', 'message': 'The Excel file is empty.'}, status=400)

                    headers = [str(h).strip().lower().replace(' ', '_') for h in rows[0] if h is not None] if has_header else []
                    data_rows = rows[1:] if has_header else rows

                    for row in data_rows:
                        if not row or not any(row):
                            continue
                        kwargs = {}
                        for idx, cell_val in enumerate(row):
                            if idx < len(headers):
                                field_name = headers[idx]
                                if field_name in valid_fields and cell_val is not None:
                                    kwargs[field_name] = cell_val
                        if kwargs:
                            model_cls.objects.create(**kwargs)
                            created_count += 1
                else:
                    return JsonResponse({'status': 'error', 'message': 'Unsupported file format. Please upload a .csv or .xlsx file.'}, status=400)

                return JsonResponse({'status': 'success', 'message': f'{created_count} record(s) imported successfully.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Failed to import records: {str(e)}'}, status=500)

        raw_ids = request.POST.getlist('ids')
        ids = [int(i) for i in raw_ids if str(i).isdigit()]

        if not ids:
            return JsonResponse({'status': 'error', 'message': 'No records selected.'}, status=400)

        if action == 'delete':
            # Check delete permission for user on this model
            if not user_can_delete_model(current_user, model_key):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Permission Denied: Your access level does not allow deleting records in this module.'
                }, status=403)

            # Cascading & integrity deletion rules for employees
            if model_key in ('hr.employee', 'employee'):
                from base.module_manager import handle_employee_deletion
                deleted_count = 0
                archived_count = 0
                for eid in ids:
                    result_type, msg = handle_employee_deletion(eid)
                    if result_type == 'deleted':
                        deleted_count += 1
                    elif result_type == 'archived':
                        archived_count += 1
                
                parts = []
                if deleted_count > 0:
                    parts.append(f"{deleted_count} employee(s) permanently deleted.")
                if archived_count > 0:
                    parts.append(f"{archived_count} employee(s) had historical records and were safely archived.")
                message = " ".join(parts) or "Action completed."
                return JsonResponse({'status': 'success', 'message': message})

            # Special cascading and foreign-key safe deletion for users
            if model_key in ('res.users', 'res_users'):
                from base.module_manager import delete_user_safely
                deleted_count = 0
                err_messages = []
                for uid in ids:
                    ok, msg = delete_user_safely(uid)
                    if ok:
                        deleted_count += 1
                    else:
                        err_messages.append(msg)
                
                if deleted_count > 0:
                    note = f"{deleted_count} user(s) and related associations deleted successfully."
                    if err_messages:
                        note += " " + " ".join(err_messages)
                    return JsonResponse({'status': 'success', 'message': note})
                else:
                    return JsonResponse({'status': 'error', 'message': " ".join(err_messages) or "Failed to delete user(s)."}, status=400)

            try:
                count, _ = model_cls.objects.filter(id__in=ids).delete()
                return JsonResponse({'status': 'success', 'message': f'{len(ids)} record(s) deleted successfully.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Failed to delete: {str(e)}'}, status=400)

        elif action == 'archive':
            if model_key in ('hr.employee', 'employee'):
                from base.module_manager import archive_employee_safely
                for eid in ids:
                    archive_employee_safely(eid, current_user)
            else:
                qs = model_cls.objects.filter(id__in=ids)
                if hasattr(model_cls, 'is_active'):
                    qs.update(is_active=False)
                elif hasattr(model_cls, 'active'):
                    qs.update(active=False)
            return JsonResponse({'status': 'success', 'message': f'{len(ids)} record(s) archived successfully.'})

        elif action == 'unarchive':
            qs = model_cls.objects.filter(id__in=ids)
            if hasattr(model_cls, 'is_active'):
                qs.update(is_active=True)
            elif hasattr(model_cls, 'active'):
                qs.update(active=True)
            return JsonResponse({'status': 'success', 'message': f'{len(ids)} record(s) unarchived successfully.'})

        elif action == 'duplicate':
            duplicated_count = 0
            for obj in model_cls.objects.filter(id__in=ids):
                obj.pk = None
                obj.id = None
                if hasattr(obj, 'name') and obj.name:
                    obj.name = f"{obj.name} (copy)"
                elif hasattr(obj, 'username') and obj.username:
                    obj.username = f"{obj.username}_copy"
                obj.save()
                duplicated_count += 1
            return JsonResponse({'status': 'success', 'message': f'{duplicated_count} record(s) duplicated successfully.'})

        return JsonResponse({'status': 'error', 'message': f'Unknown action "{action}".'}, status=400)


FIELD_TYPE_CHOICES = [
    ('VARCHAR', 'VARCHAR'),
    ('TEXT', 'TEXT'),
    ('INTEGER', 'INTEGER'),
    ('DECIMAL', 'DECIMAL'),
    ('BOOLEAN', 'BOOLEAN'),
    ('DATE', 'DATE'),
    ('DATETIME', 'DATETIME'),
    ('FK', 'FK'),
]

VIEW_TYPE_CHOICES = [
    ('list', 'List'),
    ('form', 'Form'),
    ('kanban', 'Kanban'),
    ('grid', 'Grid'),
    ('pivot', 'Pivot'),
    ('graph', 'Graph'),
    ('calendar', 'Calendar'),
    ('activity', 'Activity'),
    ('search', 'Search'),
    ('qweb', 'QWeb'),
    ('hierarchy', 'Hierarchy'),
]



MODULES_REGISTRY = {
    'hr': {
        'technical_name': 'hr',
        'name': 'Employees',
        'summary': 'Centralize employee information',
        'author': 'Office Pro',
        'website': 'https://officepro.internal/app/employees',
        'category': 'Employees',
        'category_group': 'Human Resources',
        'license': 'LGPL Version 3',
        'latest_version': '19.0.1.1',
        'is_application': True,
        'demo_data': False,
        'status': 'Installed',
        'icon_type': 'hr',
        'launch_url': '/employees/',
        'dependencies': [
            {'name': 'base_setup', 'status': 'Installed'},
            {'name': 'digest', 'status': 'Installed'},
            {'name': 'phone_validation', 'status': 'Installed'},
            {'name': 'resource_mail', 'status': 'Installed'},
            {'name': 'web', 'status': 'Installed'},
        ],
        'exclusions': [],
        'created_menus': [
            'Employees',
            'Employees/Configuration',
            'Employees/Configuration/Employee',
            'Employees/Configuration/Employee/Departure Reasons',
            'Employees/Configuration/Employee/Onboarding / Offboarding',
            'Employees/Configuration/Employee/Tags',
            'Employees/Configuration/Employee/Work Locations',
            'Employees/Configuration/Employee/Working Schedules',
            'Employees/Configuration/Recruitment',
            'Employees/Configuration/Recruitment/Contract Templates',
            'Employees/Configuration/Recruitment/Employment Types',
            'Employees/Configuration/Recruitment/Job Positions',
            'Employees/Configuration/Settings',
            'Employees/Departments',
            'Employees/Directory',
            'Employees/Employees',
            'Employees/Human Resources',
            'Employees/Reporting',
        ],
        'created_views': [
            '* INHERIT discuss.channel.view.form.inherit.hr (form)',
            '* INHERIT mail.activity.plan.template.view.form.inherit.hr (form)',
            '* INHERIT mail.activity.plan.view.form.hr.employee (form)',
            '* INHERIT mail.activity.plan.view.form.inherit.hr (form)',
            '* INHERIT mail.activity.plan.view.list.inherit.hr (list)',
            '* INHERIT mail.activity.schedule.view.form.inherit.hr (form)',
            '* INHERIT res.config.settings.view.form.inherit.hr (form)',
            '* INHERIT res.partner.bank.form.inherit.hr (form)',
            '* INHERIT res.partner.search.inherit (search)',
            '* INHERIT res.partner.view.form.inherit.hr (form)',
            '* INHERIT res.users.form.inherit (form)',
            '* INHERIT res.users.preferences.form.inherit (form)',
            '* INHERIT res.users.preferences.form.resource (form)',
            '* INHERIT res.users.preferences.form.simplified.inherit (form)',
            '* INHERIT view.employee.form.smartbutton.inherited (form)',
            '* INHERIT view.users.simple.form.hr (form)',
            '* INHERIT view.users.simple.form.inherit.hr (form)',
            'hr.bank.account.allocation.wizard.form (form)',
            'hr.bank.account.allocation.wizard.line.list (list)',
            'hr.contract.template.form (form)',
            'hr.contract.template.list (list)',
            'hr.contract.type form (form)',
            'hr.contract.type list (list)',
            'hr.department.form (form)',
            'hr.department.kanban (kanban)',
            'hr.department.list (list)',
            'hr.department.search (search)',
            'hr.departure.reason form (form)',
            'hr.departure.reason list (list)',
            'hr.departure.wizard.view.form (form)',
            'hr.employee.activity (activity)',
            'hr.employee.category.form (form)',
            'hr.employee.category.list (list)',
            'hr.employee.form (form)',
            'hr.employee.kanban (kanban)',
            'hr.employee.list (list)',
            'hr.employee.list.activites.view (list)',
            'hr.employee.public.form (form)',
            'hr.employee.search (search)',
            'hr.employee.view.graph (graph)',
            'hr.employee.view.pivot (pivot)',
            'hr.job.form (form)',
            'hr.job.kanban (kanban)',
            'hr.job.list (list)',
            'hr.job.search (search)',
            'hr.version.graph (graph)',
            'hr.version.list (list)',
            'hr.version.pivot (pivot)',
            'hr.version.search (search)',
            'hr.version.wizard.view.form (form)',
            'hr.work.location.view.form (form)',
            'hr.work.location.view.list (list)',
            'hr_employee_plan_activity_summary (qweb)',
            'print_employee_badge (qweb)',
        ],
        'defined_reports': [
            'Print Badge',
        ],
        'description_sections': [
            {
                'title': 'Office Pro Human Resources',
                'lead': True,
                'paragraphs': [
                    'With Office Pro Human Resources, manage the most important asset in your company: People',
                    'Get all your HR operations managed easily: knowledge sharing, recruitments, appraisals, timesheets, contracts, attendances, payroll, etc.',
                    'Each need is provided by a specific app that you activate on demand.',
                ],
            },
            {
                'title': 'Manage Your Employees',
                'paragraphs': [
                    'Oversee all important information in your company address book. Some information are restricted to HR managers, others are public to easily look colleagues.',
                    'Record employee contracts and get alerts when they have to be renewed.',
                ],
            },
            {
                'title': 'Streamline Your Recruitment Process',
                'paragraphs': [
                    'Index resumes, track applicants, search profiles with Office Pro HR.',
                    'Post job offers and keep track of each application received. Follow applicants in your recruitment process with the smart kanban view.',
                    'Save time by automating some communications with email templates. Resumes are indexed automatically, allowing you to easily find for specific profiles.',
                ],
            },
            {
                'title': 'Enterprise Social Network',
                'paragraphs': [
                    'Break down information silos. Share knowledge and best practices amongst all employees. Follow specific people or documents and join groups of interests to share expertise and documents.',
                    'Interact with your coworkers in real time with website live chat.',
                ],
            },
            {
                'title': 'Track time and attendances',
                'paragraphs': [
                    'Keep track of the time spent by project, client or task. It\'s easy to record timesheets or check attendances for each employee. Get your analytic accounting posted automatically based on time spent on your projects.',
                ],
            },
            {
                'title': 'Time Off Management',
                'paragraphs': [
                    'Keep track of the vacation days accrued by each employee. Employees enter their requests (paid time off, sick time off, etc), for managers to approve and validate. It\'s all done in just a few clicks. The agenda of each employee is updated accordingly.',
                ],
            },
            {
                'title': 'Keep Track of Employee Expenses',
                'paragraphs': [
                    'Get rid of the paper work and follow employee\'s expenses directly in Office Pro. Don\'t loose time or money by controlling the full flow: expense validation, reimbursement of employees, posting in the accounting and re-invoicing to customers.',
                ],
            },
            {
                'title': 'Follow Periodic Appraisals',
                'paragraphs': [
                    'Set-up appraisals plans and/or surveys for your employees and watch their evolution. Define steps for interviews and Office Pro will notify managers or subordinates automatically to prepare appraisals. Keep track of the progress of your staff periodically.',
                ],
            },
            {
                'title': 'Boost Engagement With Gamification',
                'subsections': [
                    {
                        'subtitle': 'Define clear objective and provide real time feedback',
                        'text': 'Inspire achievement with challenges, goals and rewards. Define clear objectives and provide real time feedback and tangible results. Showcase the top performers to the entire channel and publicly recognize a job well done.',
                    },
                    {
                        'subtitle': 'Leaderboards',
                        'text': 'Promote leaders and competition amongst Sales Team with performance ratios.',
                    },
                    {
                        'subtitle': 'Personal Objectives',
                        'text': 'Assign clear goals to users to align them with the company objectives.',
                    },
                    {
                        'subtitle': 'Team Targets',
                        'text': 'Compare revenues with forecasts and budgets in real time.',
                    },
                ],
            },
        ],
    },
    'mail': {
        'technical_name': 'mail',
        'name': 'Discuss & Webmail',
        'summary': 'Chat, direct messages, and email gateway integration',
        'author': 'Office Pro',
        'website': 'https://officepro.internal/app/mail',
        'category': 'Productivity',
        'category_group': 'Productivity',
        'license': 'LGPL Version 3',
        'latest_version': '19.0.1.0',
        'is_application': True,
        'demo_data': False,
        'status': 'Installed',
        'icon_type': 'mail',
        'launch_url': '/mail/inbox/',
        'dependencies': [
            {'name': 'base', 'status': 'Installed'},
            {'name': 'bus', 'status': 'Installed'},
        ],
        'exclusions': [],
        'installed_features': [
            {'type': 'Model', 'name': 'mail.message', 'label': 'Chatter Messages'},
            {'type': 'Model', 'name': 'mail.activity', 'label': 'Activities & Next Actions'},
            {'type': 'Model', 'name': 'mail.channel', 'label': 'Channels & Direct Chats'},
        ],
        'description_sections': [
            {
                'title': 'Collaborate and Communicate',
                'lead': True,
                'paragraphs': [
                    'Keep conversations organized right alongside business documents and records.',
                    'Integrates direct messaging, internal chatter, email threading, and activity scheduling in one unified workspace.',
                ],
            },
        ],
    },
    'base': {
        'technical_name': 'base',
        'name': 'Base System & Technical Architecture',
        'summary': 'Core engine, security rules, models, sequences, and menus',
        'author': 'Office Pro',
        'website': 'https://officepro.internal/app/base',
        'category': 'Administration',
        'category_group': 'Technical',
        'license': 'LGPL Version 3',
        'latest_version': '19.0.1.0',
        'is_application': False,
        'demo_data': False,
        'status': 'Installed',
        'icon_type': 'base',
        'launch_url': '/settings/',
        'dependencies': [],
        'exclusions': [],
        'installed_features': [
            {'type': 'Model', 'name': 'ir.model', 'label': 'Database Model Metadata'},
            {'type': 'Model', 'name': 'ir.ui.view', 'label': 'QWeb & Form Views'},
            {'type': 'Model', 'name': 'ir.rule', 'label': 'Record Rules'},
        ],
        'description_sections': [
            {
                'title': 'Enterprise Foundation',
                'lead': True,
                'paragraphs': [
                    'Provides the relational data engine, dynamic ORM schema registry, and role-based access security.',
                ],
            },
        ],
    },
    'project': {
        'technical_name': 'project',
        'name': 'Project Management',
        'summary': 'Organize, schedule, and track projects and tasks',
        'author': 'Office Pro',
        'website': 'https://officepro.internal/app/project',
        'category': 'Services',
        'category_group': 'Services',
        'license': 'LGPL Version 3',
        'latest_version': '19.0.1.0',
        'is_application': True,
        'demo_data': False,
        'status': 'Not Installed',
        'icon_type': 'project',
        'launch_url': '#',
        'dependencies': [
            {'name': 'base', 'status': 'Installed'},
            {'name': 'mail', 'status': 'Installed'},
        ],
        'exclusions': [],
        'installed_features': [
            {'type': 'Model', 'name': 'project.project', 'label': 'Project Definition'},
            {'type': 'Model', 'name': 'project.task', 'label': 'Project Task'},
        ],
        'description_sections': [
            {
                'title': 'Track Progress in Real Time',
                'lead': True,
                'paragraphs': [
                    'Visualize workflows on Kanban boards, track timesheets, and deliver milestones on schedule.',
                ],
            },
        ],
    },
    'contacts': {
        'technical_name': 'contacts',
        'name': 'Contacts',
        'summary': 'Centralize your customer and partner address book',
        'author': 'Office Pro',
        'website': 'https://officepro.internal/app/contacts',
        'category': 'Sales',
        'category_group': 'Sales',
        'license': 'LGPL Version 3',
        'latest_version': '19.0.1.0',
        'is_application': True,
        'demo_data': False,
        'status': 'Installed',
        'icon_type': 'contacts',
        'launch_url': '/settings/contacts/',
        'dependencies': [
            {'name': 'base', 'status': 'Installed'},
        ],
        'exclusions': [],
        'installed_features': [
            {'type': 'Model', 'name': 'res.partner', 'label': 'Contact / Partner Record'},
        ],
        'description_sections': [
            {
                'title': 'Address Book and Directory',
                'lead': True,
                'paragraphs': [
                    'Keep contact information, addresses, bank accounts, and relationship tags synchronized across the ERP.',
                ],
            },
        ],
    },
    'calendar': {
        'technical_name': 'calendar',
        'name': 'Calendar',
        'summary': 'Schedule meetings, synchronize appointments and events',
        'author': 'Office Pro',
        'website': 'https://officepro.internal/app/calendar',
        'category': 'Productivity',
        'category_group': 'Productivity',
        'license': 'LGPL Version 3',
        'latest_version': '19.0.1.0',
        'is_application': True,
        'demo_data': False,
        'status': 'Not Installed',
        'icon_type': 'calendar',
        'launch_url': '#',
        'dependencies': [
            {'name': 'base', 'status': 'Installed'},
            {'name': 'mail', 'status': 'Installed'},
        ],
        'exclusions': [],
        'installed_features': [
            {'type': 'Model', 'name': 'calendar.event', 'label': 'Calendar Meeting Event'},
        ],
        'description_sections': [
            {
                'title': 'Schedule and Coordinate',
                'lead': True,
                'paragraphs': [
                    'Sync events across teams, invite attendees, and send automated email reminders.',
                ],
            },
        ],
    },
}


@login_required_ir
def home(request):
    current_user = get_current_ir_user(request)
    is_admin = is_admin_user(current_user) if current_user else False

    apps_list = []
    
    # Mail App is accessible to all logged-in users
    apps_list.append({
        'name': 'Mail',
        'app_key': 'mail',
        'icon_bg': 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
        'glow_color': 'rgba(59, 130, 246, 0.45)',
        'url': reverse('mail_app'),
        'description': 'Send and receive emails, manage inboxes, threads, labels, and ERP documents',
    })

    # Employee App is restricted to HR Officers and Administrators
    if is_admin or is_hr_officer_or_admin(current_user):
        try:
            apps_list.append({
                'name': 'Employees',
                'app_key': 'employee',
                'icon_bg': 'linear-gradient(135deg, #10b981 0%, #047857 100%)',
                'glow_color': 'rgba(16, 185, 129, 0.45)',
                'url': reverse('employee_list'),
                'description': 'Staff directory, departments, org chart, onboarding templates, and approver matrices',
            })
        except Exception:
            pass

    # Apps Store is restricted strictly to Administrators
    if is_admin:
        try:
            apps_list.append({
                'name': 'Apps',
                'app_key': 'apps',
                'icon_bg': 'linear-gradient(135deg, #6366f1 0%, #4338ca 100%)',
                'glow_color': 'rgba(99, 102, 241, 0.45)',
                'url': reverse('apps_store'),
                'description': 'Browse and manage applications, dependencies, and feature updates',
            })
        except Exception:
            pass

    # Dashboard App is accessible to all logged-in users
    try:
        apps_list.append({
            'name': 'Dashboard',
            'app_key': 'dashboard',
            'icon_bg': 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
            'glow_color': 'rgba(2, 132, 199, 0.45)',
            'url': reverse('dashboard_home'),
            'description': 'Employee personal workspace and manager team oversight telemetry',
        })
    except Exception:
        pass

    # Attendance App is accessible to all logged-in users (personal view for users, full view for officers)
    try:
        apps_list.append({
            'name': 'Attendances',
            'app_key': 'attendance',
            'icon_bg': 'linear-gradient(135deg, #0d9488 0%, #0f766e 100%)',
            'glow_color': 'rgba(13, 148, 136, 0.45)',
            'url': reverse('attendance_list'),
            'description': 'Employee attendance punch logs, live telemetry, and time off ledger',
        })
    except Exception:
        pass

    # Time Off App
    try:
        apps_list.append({
            'name': 'Time Off',
            'app_key': 'leave',
            'icon_bg': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
            'glow_color': 'rgba(245, 158, 11, 0.45)',
            'url': reverse('leave_dashboard'),
            'description': 'Leave calendar, allocation requests, approval workflow, and time off types',
        })
    except Exception:
        pass

    # Settings app is visible only to Administrators
    if is_admin:
        apps_list.append({
            'name': 'Settings',
            'app_key': 'settings',
            'icon_bg': 'linear-gradient(135deg, #64748b 0%, #334155 100%)',
            'glow_color': 'rgba(100, 116, 139, 0.45)',
            'url': reverse('settings_home'),
            'description': 'Configure users, company settings, sequences, models, views, and technical rules',
        })

    return render(request, 'base/home.html', {
        'apps_list': apps_list,
        'current_user': current_user,
        'is_admin': is_admin,
    })


@login_required_ir
def dashboard_view(request):
    """
    Dual-Role Dashboard view:
    - Mode 'employee': 6 top metric pills (Absent, Early Going, Late Mark, Half Day, My Projects, My Tasks),
      Self-service punch widget, and Live Vertical Stacked Bar Graph (hours from 0 going vertically upward).
    - Mode 'manager': Strictly restricted to approving managers (is_approving_manager(user)).
      Team oversight, presence breakdown, active inside office roster, department telemetry.
    """
    import json
    from datetime import date, time
    from attendance.models import Attendance
    from base.models import ProjectMember, Timesheet

    current_user = get_current_ir_user(request)
    is_mgr = is_approving_manager(current_user) if current_user else False

    mode = request.GET.get('mode', 'employee')
    if mode == 'manager' and not is_mgr:
        mode = 'employee'

    today = timezone.now().date()

    # Resolve Current Employee
    current_emp = get_user_linked_employee(current_user)
    if not current_emp:
        current_emp = Employee.objects.filter(is_active=True).first()

    # Today's attendance for employee
    my_att = Attendance.objects.filter(employee=current_emp, date=today, is_active=True).first()
    my_recent_attendances = Attendance.objects.filter(employee=current_emp, is_active=True).order_by('-date', '-check_in')[:7]

    # Calculate 6 Top Pills for Workspace:
    # 1. Absent
    # 2. Early Going
    # 3. Late Mark
    # 4. Half Day
    # 5. My Projects
    # 6. My Tasks
    month_atts = Attendance.objects.filter(
        employee=current_emp,
        date__year=today.year,
        date__month=today.month,
        is_active=True
    ).order_by('date')

    absent_count = month_atts.filter(status='Absent').count()
    late_mark_count = sum(1 for a in month_atts if (a.check_in and a.check_in.time() > time(9, 30)) or a.status == 'Late')
    early_going_count = sum(1 for a in month_atts if (a.check_out and a.check_out.time() < time(18, 0)))
    half_day_count = sum(1 for a in month_atts if a.status == 'Half Day' or (0 < a.worked_duration.total_seconds() < 4.5 * 3600))
    my_projects_count = ProjectMember.objects.filter(employee=current_emp, is_active=True).values('project_id').distinct().count()
    my_tasks_count = Timesheet.objects.filter(employee=current_emp, is_active=True).count()

    # Live Stacked Vertical Bar Graph data:
    # Hours start from 0 and extend vertically upward with standard regular hours (base) + stacked time exceeding (extra/overtime)
    graph_data = []
    total_month_seconds = 0
    for att in month_atts:
        dur_secs = att.worked_duration.total_seconds()
        total_month_seconds += dur_secs
        dur_hours = round(dur_secs / 3600.0, 2)
        standard_hours = 8.0
        regular_hours = min(dur_hours, standard_hours)
        extra_hours = max(0.0, round(dur_hours - standard_hours, 2))

        in_str = att.check_in.strftime('%I:%M %p') if att.check_in else '--'
        out_str = att.check_out.strftime('%I:%M %p') if att.check_out else '--'

        is_late = bool(att.check_in and att.check_in.time() > time(9, 30))
        is_early = bool(att.check_out and att.check_out.time() < time(18, 0))

        graph_data.append({
            'date_str': att.date.strftime('%d %b'),
            'day_name': att.date.strftime('%a'),
            'date_full': att.date.strftime('%A, %B %d, %Y'),
            'total_hours': dur_hours,
            'regular_hours': regular_hours,
            'extra_hours': extra_hours,
            'formatted_total': att.worked_hours_str,
            'formatted_extra': att.worked_extra_hours_str,
            'check_in': in_str,
            'check_out': out_str,
            'status': att.status,
            'is_late': is_late,
            'is_early': is_early,
        })

    total_month_hours = int(total_month_seconds // 3600)
    total_month_mins = int((total_month_seconds % 3600) // 60)
    total_month_hours_str = f"{total_month_hours:02d}:{total_month_mins:02d}"

    standard_month_seconds = len([a for a in month_atts if a.check_in]) * 8 * 3600
    extra_month_seconds = max(0, total_month_seconds - standard_month_seconds)
    extra_month_hours = int(extra_month_seconds // 3600)
    extra_month_mins = int((extra_month_seconds % 3600) // 60)
    total_month_extra_str = f"+{extra_month_hours:02d}:{extra_month_mins:02d}"

    # Manager View Data (only computed if user is an approving manager)
    today_present_count = Attendance.objects.filter(date=today, status='Present', is_active=True).count()
    active_punches = list(Attendance.objects.filter(date=today, check_out__isnull=True, check_in__isnull=False, is_active=True).select_related('employee', 'employee__department_rel')) if is_mgr else []
    active_clocked_in_count = len(active_punches)

    dept_stats = []
    if is_mgr:
        departments = Department.objects.filter(is_active=True).order_by('name')
        for d in departments:
            total_d = d.employees.filter(is_active=True).count()
            if total_d > 0:
                present_d = Attendance.objects.filter(employee__department_rel=d, date=today, status='Present', is_active=True).count()
                pct = int((present_d / total_d) * 100) if total_d else 0
                dept_stats.append({
                    'name': d.name,
                    'total': total_d,
                    'present': present_d,
                    'pct': min(pct, 100),
                    'color': d.color or '#2563eb',
                })

    return render(request, 'base/dashboard.html', {
        'mode': mode,
        'is_manager': is_mgr,
        'current_user': current_user,
        'current_emp': current_emp,
        'my_att': my_att,
        'my_recent_attendances': my_recent_attendances,
        # 6 Top Metric Pills
        'absent_count': absent_count,
        'early_going_count': early_going_count,
        'late_mark_count': late_mark_count,
        'half_day_count': half_day_count,
        'my_projects_count': my_projects_count,
        'my_tasks_count': my_tasks_count,
        # Live Vertical Stacked Bar Graph Data
        'graph_data': graph_data,
        'graph_data_json': json.dumps(graph_data),
        'total_month_hours_str': total_month_hours_str,
        'total_month_extra_str': total_month_extra_str,
        # Manager Telemetry
        'today_present_count': today_present_count,
        'active_punches': active_punches,
        'active_clocked_in_count': active_clocked_in_count,
        'dept_stats': dept_stats,
        'current_time': timezone.now(),
        'current_date': today,
    })




def apps_store(request):
    current_user = get_current_ir_user(request)
    if not is_admin_user(current_user):
        messages.error(request, "Access Restricted: The App Store and module catalog are strictly reserved for System Administrators.")
        return redirect('home')

    is_admin = True
    search_q = request.GET.get('q', '').strip().lower()
    selected_category = request.GET.get('category', 'all').strip()

    from base.module_manager import get_installed_modules
    installed_set = get_installed_modules()

    modules = list(MODULES_REGISTRY.values())
    for m in modules:
        m['status'] = 'Installed' if m['technical_name'] in installed_set else 'Not Installed'

    if search_q:
        modules = [
            m for m in modules
            if search_q in m['name'].lower()
            or search_q in m['technical_name'].lower()
            or search_q in m['summary'].lower()
            or search_q in m['category'].lower()
        ]

    if selected_category and selected_category != 'all':
        modules = [
            m for m in modules
            if m['category_group'].lower() == selected_category.lower()
            or m['category'].lower() == selected_category.lower()
        ]

    categories_counts = {
        'all': len(MODULES_REGISTRY),
        'hr': sum(1 for m in MODULES_REGISTRY.values() if m['category_group'] == 'Human Resources'),
        'productivity': sum(1 for m in MODULES_REGISTRY.values() if m['category_group'] == 'Productivity'),
        'sales': sum(1 for m in MODULES_REGISTRY.values() if m['category_group'] == 'Sales'),
        'services': sum(1 for m in MODULES_REGISTRY.values() if m['category_group'] == 'Services'),
        'technical': sum(1 for m in MODULES_REGISTRY.values() if m['category_group'] == 'Technical'),
    }

    return render(request, 'base/apps_store.html', {
        'modules': modules,
        'search_q': search_q,
        'selected_category': selected_category,
        'categories_counts': categories_counts,
        'current_user': current_user,
        'is_admin': is_admin,
    })


def module_detail(request, module_name):
    current_user = get_current_ir_user(request)
    if not is_admin_user(current_user):
        messages.error(request, "Access Restricted: Module installation and management are strictly reserved for System Administrators.")
        return redirect('home')

    is_admin = True

    from base.module_manager import get_installed_modules, install_module, uninstall_module

    module = MODULES_REGISTRY.get(module_name)
    if not module:
        module = MODULES_REGISTRY.get('hr')

    installed_set = get_installed_modules()
    module['status'] = 'Installed' if module['technical_name'] in installed_set else 'Not Installed'

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('upgrade', 'install'):
            success, msg = install_module(module['technical_name'], current_user)
            if success:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        elif action == 'uninstall':
            success, msg = uninstall_module(module['technical_name'], current_user)
            if success:
                messages.success(request, msg)
            else:
                messages.warning(request, msg)
        return redirect('module_detail', module_name=module['technical_name'])

    all_keys = list(MODULES_REGISTRY.keys())
    current_index = all_keys.index(module['technical_name']) if module['technical_name'] in all_keys else 0
    total_count = len(all_keys)
    prev_key = all_keys[(current_index - 1) % total_count]
    next_key = all_keys[(current_index + 1) % total_count]

    return render(request, 'base/module_detail.html', {
        'module': module,
        'current_user': current_user,
        'is_admin': is_admin,
        'current_index': current_index + 1,
        'total_count': total_count,
        'prev_key': prev_key,
        'next_key': next_key,
    })


def settings_home(request):
    current_user = get_current_ir_user(request)
    
    if request.method == 'POST':
        action_type = request.POST.get('action_type', 'theme')
        if action_type == 'theme':
            # Theme customization is available to any user for their device session
            preset = request.POST.get('preset', 'purple')
            primary_color = request.POST.get('primary_color', '#714b67').strip()
            primary_hover = request.POST.get('primary_hover', '#5a3c53').strip()
            navbar_bg = request.POST.get('navbar_bg', '#1e1e2f').strip()
            wallpaper = request.POST.get('wallpaper', 'purple_lowpoly').strip()
            custom_wallpaper_url = request.POST.get('custom_wallpaper_url', '').strip()

            # Handle file upload (images, gif, live wallpaper mp4/webm)
            if 'custom_wallpaper_file' in request.FILES and request.FILES['custom_wallpaper_file']:
                uploaded_file = request.FILES['custom_wallpaper_file']
                file_path = default_storage.save(f"wallpapers/{uploaded_file.name}", uploaded_file)
                custom_wallpaper_url = default_storage.url(file_path)
                wallpaper = 'custom_image'

            request.session['theme_settings'] = {
                'preset': preset,
                'primary_color': primary_color,
                'primary_hover': primary_hover,
                'navbar_bg': navbar_bg,
                'wallpaper': wallpaper,
                'custom_wallpaper_url': custom_wallpaper_url,
            }
            messages.success(request, 'Theme settings updated successfully.')
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('settings_home')
            if not is_admin_user(current_user):
                next_url = reverse('home')
            return redirect(next_url)
        else:
            # Handle general/employee/attendance settings update
            active_tab = request.POST.get('active_tab', 'general')
            messages.success(request, 'Settings updated successfully.')
            return redirect(f"{reverse('settings_general')}?tab={active_tab}")

    # General Settings page is only accessible by Administrators
    if not is_admin_user(current_user):
        messages.error(request, "Access Restricted: Settings are only available to Administrators.")
        return redirect('home')

    company = ResCompany.objects.first()
    active_tab = request.GET.get('tab', 'general')
    return render(request, 'base/setting.html', {
        'company': company,
        'active_tab': active_tab,
        'current_user': current_user,
    })



# ---------------------------------------------------------------------------
# Technical > Models
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_models(request):
    self_ir_model = IrModel.objects.filter(model_name='ir.model').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    models_qs = IrModel.objects.filter(is_active=True).select_related('module')
    models_qs = apply_search(models_qs, domain, query, search_fields=['model_name', 'description', 'table_name'])
    models_qs = models_qs.order_by('model_name')

    groups = apply_group_by(models_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.model')

    columns = [
        {'name': 'model_name', 'label': 'Model'},
        {'name': 'description', 'label': 'Model Description'},
        {'name': 'get_state_display', 'label': 'Type'},
        {'name': 'transient', 'label': 'Transient Model'},
    ]

    return render(request, 'base/technical_models.html', {
        'models': None if groups else models_qs,
        'groups': groups,
        'columns': columns,
        'total_count': models_qs.count(),
        'create_url': reverse('technical_model_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.model',
        'operators_by_type_json': get_operators_json(),
    })


@admin_required_ir
def technical_model_create(request):
    if request.method == 'POST':
        model = IrModel.objects.create(
            model_name=request.POST.get('model_name', '').strip(),
            table_name=request.POST.get('table_name', '').strip(),
            description=request.POST.get('description', '').strip(),
            abstract=request.POST.get('abstract') == 'on',
            transient=request.POST.get('transient') == 'on',
            is_mail_thread=request.POST.get('is_mail_thread') == 'on',
            is_mail_activity=request.POST.get('is_mail_activity') == 'on',
            is_mail_blacklist=request.POST.get('is_mail_blacklist') == 'on',
            model_order=request.POST.get('model_order', 'id').strip() or 'id',
            state='manual',
        )
        try:
            field_rows = json.loads(request.POST.get('fields_json', '[]'))
        except (ValueError, TypeError):
            field_rows = []
        for row in field_rows:
            field_name = (row.get('field_name') or '').strip()
            if not field_name:
                continue
            IrModelFields.objects.create(
                model=model,
                field_name=field_name,
                field_type=row.get('field_type') or 'VARCHAR',
                is_required=bool(row.get('is_required')),
                relation_model_id=row.get('relation_model_id') or None,
            )
        return redirect('technical_model_detail', model_id=model.id)

    return render(request, 'base/technical_model_create.html', {
        'field_type_choices': FIELD_TYPE_CHOICES,
        'relation_model_choices': get_relation_model_choices(),
    })


@admin_required_ir
def technical_model_detail(request, model_id):
    model = get_object_or_404(IrModel.objects.select_related('module'), id=model_id)
    if request.method == 'POST':
        model.description = request.POST.get('description', model.description).strip()
        model.model_order = request.POST.get('model_order', model.model_order).strip() or 'id'
        model.abstract = request.POST.get('abstract') == 'on'
        model.transient = request.POST.get('transient') == 'on'
        model.is_mail_thread = request.POST.get('is_mail_thread') == 'on'
        model.is_mail_activity = request.POST.get('is_mail_activity') == 'on'
        model.is_mail_blacklist = request.POST.get('is_mail_blacklist') == 'on'
        model.save()
        return redirect('technical_model_detail', model_id=model.id)

    fields_qs = IrModelFields.objects.filter(model=model, is_active=True).order_by('id')
    access_rights = IrModelAccess.objects.filter(model=model, is_active=True).select_related('group')
    rules = IrRule.objects.filter(model=model, is_active=True).select_related('group')
    views = IrUiView.objects.filter(model=model, is_active=True).select_related('inherit_id').order_by('name')

    return render(request, 'base/technical_model_detail.html', {
        'model': model,
        'fields_qs': fields_qs,
        'access_rights': access_rights,
        'rules': rules,
        'views': views,
        'form_action': reverse('technical_model_detail', args=[model.id]),
        'create_url': reverse('technical_model_create'),
    })



# ---------------------------------------------------------------------------
# Technical > Fields
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_fields(request):
    self_ir_model = IrModel.objects.filter(model_name='ir.model.fields').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    fields_qs = IrModelFields.objects.filter(is_active=True).select_related('model', 'model__module', 'relation_model')
    fields_qs = apply_search(fields_qs, domain, query, search_fields=['field_name', 'model__model_name', 'model__description', 'field_type', 'relation_model__model_name'])
    fields_qs = fields_qs.order_by('model__model_name', 'field_name')

    groups = apply_group_by(fields_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.model.fields')

    return render(request, 'base/technical_fields.html', {
        'fields_list': None if groups else fields_qs,
        'groups': groups,
        'total_count': fields_qs.count(),
        'create_url': reverse('technical_field_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.model.fields',
        'operators_by_type_json': get_operators_json(),
    })


@admin_required_ir
def technical_field_create(request):
    if request.method == 'POST':
        model_id = request.POST.get('model')
        model = get_object_or_404(IrModel, id=model_id)
        field = IrModelFields.objects.create(
            model=model,
            field_name=request.POST.get('field_name', '').strip(),
            field_type=request.POST.get('field_type', 'VARCHAR').strip(),
            is_required=request.POST.get('is_required') == 'on',
            is_active=True,
            relation_model_id=request.POST.get('relation_model') or None,
        )
        return redirect('technical_field_detail', field_id=field.id)

    all_models = IrModel.objects.filter(is_active=True).order_by('model_name')
    return render(request, 'base/technical_field_create.html', {
        'all_models': all_models,
        'field_type_choices': FIELD_TYPE_CHOICES,
        'relation_model_choices': get_relation_model_choices(),
    })


@admin_required_ir
def technical_field_detail(request, field_id):
    field = get_object_or_404(IrModelFields.objects.select_related('model', 'model__module', 'relation_model'), id=field_id)
    if request.method == 'POST':
        field.field_name = request.POST.get('field_name', field.field_name).strip()
        field.field_type = request.POST.get('field_type', field.field_type).strip()
        field.is_required = request.POST.get('is_required') == 'on'
        field.is_active = request.POST.get('is_active') == 'on'
        rel_model_id = request.POST.get('relation_model')
        field.relation_model_id = int(rel_model_id) if rel_model_id else None
        field.save()
        return redirect('technical_field_detail', field_id=field.id)

    access_rights = IrModelAccess.objects.filter(model=field.model, is_active=True).select_related('group')
    rules = IrRule.objects.filter(model=field.model, is_active=True).select_related('group')

    all_field_ids = list(IrModelFields.objects.filter(is_active=True).order_by('model__model_name', 'field_name').values_list('id', flat=True))
    current_index = all_field_ids.index(field.id) + 1 if field.id in all_field_ids else 1
    total_fields = len(all_field_ids)
    prev_id = all_field_ids[current_index - 2] if current_index > 1 else None
    next_id = all_field_ids[current_index] if current_index < total_fields else None

    all_models = IrModel.objects.filter(is_active=True).order_by('model_name')

    return render(request, 'base/technical_field_detail.html', {
        'field': field,
        'access_rights': access_rights,
        'rules': rules,
        'all_models': all_models,
        'field_type_choices': FIELD_TYPE_CHOICES,
        'relation_model_choices': get_relation_model_choices(),
        'form_action': reverse('technical_field_detail', args=[field.id]),
        'create_url': reverse('technical_field_create'),
        'current_index': current_index,
        'total_fields': total_fields,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Technical > Actions
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_actions(request):
    self_ir_model = IrModel.objects.filter(model_name='ir.actions.act_window').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    actions_qs = IrActions.objects.filter(is_active=True)
    actions_qs = apply_search(actions_qs, domain, query, search_fields=['name', 'action_type', 'res_model'])
    actions_qs = actions_qs.order_by('name')

    groups = apply_group_by(actions_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.actions.act_window')

    columns = [
        {'name': 'name', 'label': 'Action Name'},
        {'name': 'action_type', 'label': 'Action Type'},
        {'name': 'res_model', 'label': 'Related Model'},
        {'name': 'view_mode', 'label': 'View Mode'},
    ]

    return render(request, 'base/technical_actions.html', {
        'actions_list': None if groups else actions_qs,
        'groups': groups,
        'columns': columns,
        'total_count': actions_qs.count(),
        'create_url': reverse('technical_action_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.actions.act_window',
        'operators_by_type_json': get_operators_json(),
    })


@admin_required_ir
def technical_action_create(request):
    if request.method == 'POST':
        action = IrActions.objects.create(
            name=request.POST.get('name', '').strip(),
            action_type=request.POST.get('action_type', 'ir.actions.act_window').strip(),
            res_model=request.POST.get('res_model', '').strip() or None,
            view_mode=request.POST.get('view_mode', 'list,form').strip() or 'list,form',
            is_active=True,
        )
        return redirect('technical_action_detail', action_id=action.id)

    return render(request, 'base/technical_action_create.html', {
        'action_type_choices': IrActions.ACTION_TYPE_CHOICES,
    })


@admin_required_ir
def technical_action_detail(request, action_id):
    action = get_object_or_404(IrActions, id=action_id)
    if request.method == 'POST':
        action.name = request.POST.get('name', action.name).strip()
        action.action_type = request.POST.get('action_type', action.action_type).strip()
        action.res_model = request.POST.get('res_model', action.res_model or '').strip() or None
        action.view_mode = request.POST.get('view_mode', action.view_mode or '').strip() or 'list,form'
        action.save()
        return redirect('technical_action_detail', action_id=action.id)

    all_action_ids = list(IrActions.objects.filter(is_active=True).order_by('name').values_list('id', flat=True))
    current_index = all_action_ids.index(action.id) + 1 if action.id in all_action_ids else 1
    total_actions = len(all_action_ids)
    prev_id = all_action_ids[current_index - 2] if current_index > 1 else None
    next_id = all_action_ids[current_index] if current_index < total_actions else None

    return render(request, 'base/technical_action_detail.html', {
        'action': action,
        'action_type_choices': IrActions.ACTION_TYPE_CHOICES,
        'form_action': reverse('technical_action_detail', args=[action.id]),
        'create_url': reverse('technical_action_create'),
        'current_index': current_index,
        'total_actions': total_actions,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Technical > ManyToMany Relations
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_m2m(request):
    self_ir_model = IrModel.objects.filter(model_name='ir.model.relation').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    m2m_qs = IrModelRelation.objects.filter(is_active=True).select_related('module', 'model')
    m2m_qs = apply_search(m2m_qs, domain, query, search_fields=['name', 'module__name', 'model__model_name', 'model__description'])
    m2m_qs = m2m_qs.order_by('name')

    groups = apply_group_by(m2m_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.model.relation')

    columns = [
        {'name': 'name', 'label': 'Relation Name'},
        {'name': 'module.name', 'label': 'Module'},
        {'name': 'model.description', 'label': 'Model'},
    ]

    return render(request, 'base/technical_m2m.html', {
        'm2m_list': None if groups else m2m_qs,
        'groups': groups,
        'columns': columns,
        'total_count': m2m_qs.count(),
        'create_url': reverse('technical_m2m_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.model.relation',
        'operators_by_type_json': get_operators_json(),
    })


@admin_required_ir
def technical_m2m_create(request):
    if request.method == 'POST':
        model_id = request.POST.get('model')
        module_id = request.POST.get('module')
        m2m = IrModelRelation.objects.create(
            name=request.POST.get('name', '').strip(),
            model_id=int(model_id) if model_id else None,
            module_id=int(module_id) if module_id else None,
            is_active=True,
        )
        return redirect('technical_m2m_detail', m2m_id=m2m.id)

    all_models = IrModel.objects.filter(is_active=True).order_by('model_name')
    all_modules = IrModule.objects.filter(is_active=True).order_by('name')
    return render(request, 'base/technical_m2m_create.html', {
        'all_models': all_models,
        'all_modules': all_modules,
    })


@admin_required_ir
def technical_m2m_detail(request, m2m_id):
    m2m = get_object_or_404(IrModelRelation.objects.select_related('module', 'model'), id=m2m_id)
    if request.method == 'POST':
        m2m.name = request.POST.get('name', m2m.name).strip()
        model_id = request.POST.get('model')
        module_id = request.POST.get('module')
        m2m.model_id = int(model_id) if model_id else None
        m2m.module_id = int(module_id) if module_id else None
        m2m.save()
        return redirect('technical_m2m_detail', m2m_id=m2m.id)

    all_m2m_ids = list(IrModelRelation.objects.filter(is_active=True).order_by('name').values_list('id', flat=True))
    current_index = all_m2m_ids.index(m2m.id) + 1 if m2m.id in all_m2m_ids else 1
    total_m2m = len(all_m2m_ids)
    prev_id = all_m2m_ids[current_index - 2] if current_index > 1 else None
    next_id = all_m2m_ids[current_index] if current_index < total_m2m else None

    all_models = IrModel.objects.filter(is_active=True).order_by('model_name')
    all_modules = IrModule.objects.filter(is_active=True).order_by('name')

    return render(request, 'base/technical_m2m_detail.html', {
        'm2m': m2m,
        'all_models': all_models,
        'all_modules': all_modules,
        'form_action': reverse('technical_m2m_detail', args=[m2m.id]),
        'create_url': reverse('technical_m2m_create'),
        'current_index': current_index,
        'total_m2m': total_m2m,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Technical > Scheduled Actions (Cron Jobs)
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_cron(request):
    self_ir_model = IrModel.objects.filter(model_name='ir.cron').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    crons_qs = IrCron.objects.select_related('model', 'user', 'allowed_groups')
    crons_qs = apply_search(crons_qs, domain, query, search_fields=['name', 'model__model_name', 'model__description', 'code'])
    crons_qs = crons_qs.order_by('priority', 'name')

    groups = apply_group_by(crons_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.cron')

    columns = [
        {'name': 'priority', 'label': 'Priority'},
        {'name': 'name', 'label': 'Action Name'},
        {'name': 'model.description', 'label': 'Model'},
        {'name': 'next_execution_date', 'label': 'Next Execution Date'},
        {'name': 'interval_number', 'label': 'Interval Number'},
        {'name': 'interval_type', 'label': 'Interval Unit'},
        {'name': 'is_active', 'label': 'Active'},
    ]

    return render(request, 'base/technical_cron.html', {
        'crons_list': None if groups else crons_qs,
        'groups': groups,
        'columns': columns,
        'total_count': crons_qs.count(),
        'create_url': reverse('technical_cron_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.cron',
        'operators_by_type_json': get_operators_json(),
    })


@admin_required_ir
def technical_cron_create(request):
    if request.method == 'POST':
        model_id = request.POST.get('model')
        user_id = request.POST.get('user')
        allowed_group_id = request.POST.get('allowed_groups')
        cron = IrCron.objects.create(
            name=request.POST.get('name', 'Execute Code').strip() or 'Execute Code',
            model_id=int(model_id) if model_id else None,
            user_id=int(user_id) if user_id else None,
            allowed_groups_id=int(allowed_group_id) if allowed_group_id else None,
            interval_number=int(request.POST.get('interval_number', 1) or 1),
            interval_type=request.POST.get('interval_type', 'days'),
            priority=int(request.POST.get('priority', 5) or 5),
            code=request.POST.get('code', 'model.process()').strip(),
            is_active=request.POST.get('is_active') == 'on',
        )
        return redirect('technical_cron_detail', cron_id=cron.id)

    all_models = IrModel.objects.filter(is_active=True).order_by('model_name')
    all_users = ResUsers.objects.filter(is_active=True).order_by('username')
    all_groups = ResGroups.objects.filter(is_active=True).order_by('name')
    return render(request, 'base/technical_cron_create.html', {
        'all_models': all_models,
        'all_users': all_users,
        'all_groups': all_groups,
        'interval_type_choices': IrCron.INTERVAL_TYPE_CHOICES,
    })


@admin_required_ir
def technical_cron_detail(request, cron_id):
    cron = get_object_or_404(IrCron.objects.select_related('model', 'user', 'allowed_groups'), id=cron_id)
    if request.method == 'POST':
        cron.name = request.POST.get('name', cron.name).strip()
        model_id = request.POST.get('model')
        user_id = request.POST.get('user')
        allowed_group_id = request.POST.get('allowed_groups')
        cron.model_id = int(model_id) if model_id else None
        cron.user_id = int(user_id) if user_id else None
        cron.allowed_groups_id=int(allowed_group_id) if allowed_group_id else None
        cron.interval_number = int(request.POST.get('interval_number', cron.interval_number) or 1)
        cron.interval_type = request.POST.get('interval_type', cron.interval_type)
        cron.priority = int(request.POST.get('priority', cron.priority) or 5)
        cron.code = request.POST.get('code', cron.code)
        cron.is_active = request.POST.get('is_active') == 'on'
        cron.save()
        return redirect('technical_cron_detail', cron_id=cron.id)

    all_cron_ids = list(IrCron.objects.order_by('priority', 'name').values_list('id', flat=True))
    current_index = all_cron_ids.index(cron.id) + 1 if cron.id in all_cron_ids else 1
    total_crons = len(all_cron_ids)
    prev_id = all_cron_ids[current_index - 2] if current_index > 1 else None
    next_id = all_cron_ids[current_index] if current_index < total_crons else None

    all_models = IrModel.objects.filter(is_active=True).order_by('model_name')
    all_users = ResUsers.objects.filter(is_active=True).order_by('username')
    all_groups = ResGroups.objects.filter(is_active=True).order_by('name')

    return render(request, 'base/technical_cron_detail.html', {
        'cron': cron,
        'all_models': all_models,
        'all_users': all_users,
        'all_groups': all_groups,
        'interval_type_choices': IrCron.INTERVAL_TYPE_CHOICES,
        'form_action': reverse('technical_cron_detail', args=[cron.id]),
        'create_url': reverse('technical_cron_create'),
        'current_index': current_index,
        'total_crons': total_crons,
        'prev_id': prev_id,
        'next_id': next_id,
    })


def relation_search(request):
    model_key = request.GET.get('model', '')
    query = request.GET.get('q', '').strip()
    page = max(1, int(request.GET.get('page', 1) or 1))
    page_size = max(10, min(100, int(request.GET.get('page_size', 80) or 80)))

    if model_key == 'ir.model':
        qs = IrModel.objects.filter(is_active=True).exclude(
            model_name__in=['res.users.groups', 'ir.module', 'ir.filters']
        )
        if query:
            qs = qs.filter(Q(model_name__icontains=query) | Q(description__icontains=query))
        qs = qs.order_by('description', 'model_name')
        total_count = qs.count()
        start = (page - 1) * page_size
        end = start + page_size
        page_qs = qs[start:end]

        results = [
            {'id': m.id, 'text': f"{m.description or m.model_name} ({m.model_name})"}
            for m in page_qs
        ]
        return JsonResponse({
            'results': results,
            'pagination': {'more': end < total_count}
        })
    return JsonResponse({'results': [], 'pagination': {'more': False}})


@admin_required_ir
def technical_views(request):
    filterable_fields = [
        {'name': 'name', 'label': 'View Name', 'type': 'char'},
        {'name': 'view_type', 'label': 'View Type', 'type': 'selection', 'choices': IrUiView.VIEW_TYPE_CHOICES},
        {'name': 'model__model_name', 'label': 'Model', 'type': 'char'},
    ]
    groupable_fields = [
        {'name': 'view_type', 'label': 'View Type'},
        {'name': 'model__model_name', 'label': 'Model'},
    ]

    domain = get_domain_from_request(request)
    group_by_field = get_group_by_from_request(request, groupable_fields)

    views_qs = IrUiView.objects.all().select_related('model', 'inherit_id')
    if domain:
        views_qs = apply_domain(views_qs, domain)
    views_qs = views_qs.order_by('name')

    groups = apply_group_by(views_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.ui.view')

    columns = [
        {'name': 'name', 'label': 'View Name'},
        {'name': 'view_type', 'label': 'View Type'},
        {'name': 'model', 'label': 'Model'},
        {'name': 'external_id', 'label': 'External ID'},
        {'name': 'inherit_id', 'label': 'Inherited View'},
    ]

    return render(request, 'base/technical_views.html', {
        'views_list': None if groups else views_qs,
        'groups': groups,
        'columns': columns,
        'total_count': views_qs.count(),
        'create_url': reverse('technical_view_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.ui.view',
        'operators_by_type_json': get_operators_json(),
    })



@admin_required_ir
def technical_view_create(request):
    if request.method == 'POST':
        view = IrUiView.objects.create(
            name=request.POST.get('name', '').strip(),
            view_type=request.POST.get('view_type', 'list'),
            key=request.POST.get('key', '').strip() or None,
            visibility=request.POST.get('visibility', '').strip() or None,
            model_id=request.POST.get('model') or None,
            priority=int(request.POST.get('priority', 16) or 16),
            is_active=request.POST.get('is_active') == 'on' if 'is_active' in request.POST else True,
            inherit_id_id=request.POST.get('inherit_id') or None,
            mode=request.POST.get('mode', 'primary'),
            model_data=request.POST.get('model_data', '').strip() or None,
            external_id=request.POST.get('external_id', '').strip() or None,
            arch=request.POST.get('arch', '').strip() or None,
            template_path=request.POST.get('template_path', '').strip() or None,
        )
        return redirect('technical_view_detail', view_id=view.id)

    inherit_choices = IrUiView.objects.filter(is_active=True).order_by('name')
    models_list = IrModel.objects.filter(is_active=True).order_by('model_name')

    return render(request, 'base/technical_view_create.html', {
        'inherit_choices': inherit_choices,
        'models_list': models_list,
        'view_types': VIEW_TYPE_CHOICES,
        'view_modes': [('primary', 'Base view / Primary'), ('extension', 'Extension View')],
        'form_action': reverse('technical_view_create'),
    })


@admin_required_ir
def technical_view_detail(request, view_id):
    view_obj = get_object_or_404(IrUiView.objects.select_related('model', 'inherit_id'), id=view_id)

    if request.method == 'POST':
        view_obj.name = request.POST.get('name', view_obj.name).strip()
        view_obj.view_type = request.POST.get('view_type', view_obj.view_type)
        view_obj.key = request.POST.get('key', '').strip() or None
        view_obj.visibility = request.POST.get('visibility', '').strip() or None
        view_obj.model_id = request.POST.get('model') or None
        view_obj.priority = int(request.POST.get('priority', view_obj.priority) or 16)
        view_obj.is_active = request.POST.get('is_active') == 'on'
        view_obj.inherit_id_id = request.POST.get('inherit_id') or None
        view_obj.mode = request.POST.get('mode', 'primary')
        view_obj.model_data = request.POST.get('model_data', '').strip() or None
        view_obj.external_id = request.POST.get('external_id', '').strip() or None
        view_obj.arch = request.POST.get('arch', view_obj.arch or '')
        view_obj.template_path = request.POST.get('template_path', '').strip() or None
        view_obj.save()
        return redirect('technical_view_detail', view_id=view_obj.id)

    inherit_choices = IrUiView.objects.filter(is_active=True).exclude(id=view_obj.id).order_by('name')
    models_list = IrModel.objects.filter(is_active=True).order_by('model_name')
    inherited_views = IrUiView.objects.filter(inherit_id=view_obj, is_active=True).order_by('priority', 'name')
    
    access_rights = []
    if view_obj.model:
        access_rights = IrModelAccess.objects.filter(model=view_obj.model, is_active=True).select_related('group')

    return render(request, 'base/technical_view_detail.html', {
        'view_obj': view_obj,
        'inherit_choices': inherit_choices,
        'models_list': models_list,
        'inherited_views': inherited_views,
        'access_rights': access_rights,
        'view_types': VIEW_TYPE_CHOICES,
        'view_modes': [('primary', 'Base view / Primary'), ('extension', 'Extension View')],
        'form_action': reverse('technical_view_detail', args=[view_obj.id]),
        'create_url': reverse('technical_view_create'),
    })




# ---------------------------------------------------------------------------
# Technical > Menu Items
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_menu_items(request):
    menus = IrUiMenu.objects.filter(is_active=True).order_by('parent_id', 'sequence')

    def build_path(menu):
        parts = [menu.name]
        current = menu.parent
        while current:
            parts.insert(0, current.name)
            current = current.parent
        return '/'.join(parts)

    menu_list = [{'obj': m, 'full_path': build_path(m)} for m in menus]
    return render(request, 'base/technical_menu_items.html', {
        'menu_list': menu_list,
        'total_count': len(menu_list),
        'create_url': '#',
    })


@admin_required_ir
def technical_menu_item_detail(request, menu_id):
    menu = get_object_or_404(IrUiMenu.objects.select_related('parent', 'visibility_group'), id=menu_id)
    if request.method == 'POST':
        menu.name = request.POST.get('name', menu.name).strip()
        parent_id = request.POST.get('parent')
        menu.parent_id = int(parent_id) if parent_id else None
        try:
            menu.sequence = int(request.POST.get('sequence', menu.sequence))
        except (ValueError, TypeError):
            pass
        menu.url_path = request.POST.get('url_path', menu.url_path or '').strip() or None
        menu.action_model = request.POST.get('action_model', menu.action_model or '').strip() or None
        menu.web_icon = request.POST.get('web_icon', menu.web_icon or '').strip() or None
        visibility_group_id = request.POST.get('visibility_group')
        menu.visibility_group_id = int(visibility_group_id) if visibility_group_id else None
        menu.save()
        return redirect('technical_menu_item_detail', menu_id=menu.id)

    children = IrUiMenu.objects.filter(parent=menu, is_active=True).order_by('sequence')
    parts = [menu.name]
    current = menu.parent
    while current:
        parts.insert(0, current.name)
        current = current.parent

    all_menus = IrUiMenu.objects.filter(is_active=True).exclude(id=menu.id).order_by('name')
    groups = ResGroups.objects.filter(is_active=True).order_by('name')

    all_menu_ids = list(IrUiMenu.objects.filter(is_active=True).order_by('parent_id', 'sequence').values_list('id', flat=True))
    current_index = all_menu_ids.index(menu.id) + 1 if menu.id in all_menu_ids else 1
    total_menus = len(all_menu_ids)
    prev_id = all_menu_ids[current_index - 2] if current_index > 1 else None
    next_id = all_menu_ids[current_index] if current_index < total_menus else None

    return render(request, 'base/technical_menu_item_detail.html', {
        'menu': menu,
        'children': children,
        'full_path': '/'.join(parts),
        'parent_menus': all_menus,
        'groups': groups,
        'form_action': reverse('technical_menu_item_detail', args=[menu.id]),
        'create_url': reverse('technical_menu_items'),
        'current_index': current_index,
        'total_menus': total_menus,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------

@require_POST
def save_filter(request):
    model_key = request.POST.get('model_key')
    name = request.POST.get('name', '').strip()
    domain_raw = request.POST.get('domain', '[]')
    group_by_field = request.POST.get('group_by', '')
    is_default = request.POST.get('is_default') == 'true'

    if not name or not model_key:
        return JsonResponse({'ok': False, 'error': 'Name and model are required.'}, status=400)

    ir_model = IrModel.objects.filter(model_name=model_key).first()
    if not ir_model:
        return JsonResponse({'ok': False, 'error': 'Unknown model.'}, status=400)

    try:
        domain = json.loads(domain_raw)
    except (ValueError, TypeError):
        domain = []

    current_user = get_current_ir_user(request)
    if is_default:
        IrFilters.objects.filter(model=ir_model, user=current_user, is_default=True).update(is_default=False)

    fav = IrFilters.objects.create(
        name=name, model=ir_model, user=current_user, domain=domain,
        context={'group_by': group_by_field} if group_by_field else {},
        is_default=is_default,
    )
    return JsonResponse({'ok': True, 'id': fav.id})


@require_POST
def set_default_filter(request, filter_id):
    fav = IrFilters.objects.filter(id=filter_id).first()
    if not fav:
        return JsonResponse({'ok': False, 'error': 'Not found.'}, status=404)
    current_user = get_current_ir_user(request)
    IrFilters.objects.filter(model=fav.model, user=current_user, is_default=True).update(is_default=False)
    fav.is_default = True
    fav.save(update_fields=['is_default'])
    return JsonResponse({'ok': True})


@require_POST
def delete_filter(request, filter_id):
    IrFilters.objects.filter(id=filter_id).update(is_active=False)
    return JsonResponse({'ok': True})


# ---------------------------------------------------------------------------
# Technical > Sequences
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_sequences(request):
    self_ir_model = IrModel.objects.filter(model_name='ir.sequence').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    seq_qs = IrSequence.objects.filter(is_active=True).select_related('company')
    seq_qs = apply_search(seq_qs, domain, query, search_fields=['code', 'name', 'prefix'])
    seq_qs = seq_qs.order_by('code')

    groups = apply_group_by(seq_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.sequence')

    columns = [
        {'name': 'code', 'label': 'Sequence Code'},
        {'name': 'name', 'label': 'Name'},
        {'name': 'prefix', 'label': 'Prefix'},
        {'name': 'padding', 'label': 'Sequence Size'},
        {'name': 'company', 'label': 'Company'},
        {'name': 'next_number', 'label': 'Next Number'},
        {'name': 'step', 'label': 'Step'},
        {'name': 'implementation', 'label': 'Implementation'},
    ]

    return render(request, 'base/technical_sequences.html', {
        'sequences_list': None if groups else seq_qs,
        'groups': groups,
        'columns': columns,
        'total_count': seq_qs.count(),
        'create_url': reverse('technical_sequence_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.sequence',
        'operators_by_type_json': get_operators_json(),
    })


@admin_required_ir
def technical_sequence_create(request):
    if request.method == 'POST':
        seq = IrSequence.objects.create(
            name=request.POST.get('name', '').strip() or None,
            code=request.POST.get('code', '').strip(),
            implementation=request.POST.get('implementation', 'standard'),
            company_id=request.POST.get('company') or None,
            prefix=request.POST.get('prefix', '').strip() or None,
            suffix=request.POST.get('suffix', '').strip() or None,
            use_date_range=request.POST.get('use_date_range') == 'on',
            padding=int(request.POST.get('padding', 5) or 5),
            step=int(request.POST.get('step', 1) or 1),
            next_number=int(request.POST.get('next_number', 1) or 1),
            is_active=request.POST.get('is_active') == 'on' if 'is_active' in request.POST else True,
        )
        return redirect('technical_sequence_detail', sequence_id=seq.id)

    companies = ResCompany.objects.filter(is_active=True).order_by('name')
    return render(request, 'base/technical_sequence_create.html', {
        'companies': companies,
        'form_action': reverse('technical_sequence_create'),
    })


@admin_required_ir
def technical_sequence_detail(request, sequence_id):
    seq_obj = get_object_or_404(IrSequence.objects.select_related('company'), id=sequence_id)

    if request.method == 'POST':
        seq_obj.name = request.POST.get('name', '').strip() or None
        seq_obj.code = request.POST.get('code', seq_obj.code).strip()
        seq_obj.implementation = request.POST.get('implementation', 'standard')
        seq_obj.company_id = request.POST.get('company') or None
        seq_obj.prefix = request.POST.get('prefix', '').strip() or None
        seq_obj.suffix = request.POST.get('suffix', '').strip() or None
        seq_obj.use_date_range = request.POST.get('use_date_range') == 'on'
        seq_obj.padding = int(request.POST.get('padding', seq_obj.padding) or 5)
        seq_obj.step = int(request.POST.get('step', seq_obj.step) or 1)
        seq_obj.next_number = int(request.POST.get('next_number', seq_obj.next_number) or 1)
        seq_obj.is_active = request.POST.get('is_active') == 'on'
        seq_obj.save()
        return redirect('technical_sequence_detail', sequence_id=seq_obj.id)

    companies = ResCompany.objects.filter(is_active=True).order_by('name')
    return render(request, 'base/technical_sequence_detail.html', {
        'seq_obj': seq_obj,
        'companies': companies,
        'form_action': reverse('technical_sequence_detail', args=[seq_obj.id]),
        'create_url': reverse('technical_sequence_create'),
    })



# ---------------------------------------------------------------------------
# Technical > Access Rights
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_access_rights(request):
    self_ir_model = IrModel.objects.filter(model_name='ir.model.access').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    access_qs = IrModelAccess.objects.filter(is_active=True).select_related('model', 'group')
    access_qs = apply_search(access_qs, domain, query, search_fields=['model__model_name', 'group__name'])
    access_qs = access_qs.order_by('model__model_name', 'group__name')

    groups = apply_group_by(access_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.model.access')

    columns = [
        {'name': 'model', 'label': 'Model'},
        {'name': 'group', 'label': 'Group'},
        {'name': 'can_read', 'label': 'Read'},
        {'name': 'can_write', 'label': 'Write'},
        {'name': 'can_create', 'label': 'Create'},
        {'name': 'can_delete', 'label': 'Delete'},
        {'name': 'is_active', 'label': 'Active'},
    ]

    return render(request, 'base/technical_access_rights.html', {
        'access_list': None if groups else access_qs,
        'groups': groups,
        'columns': columns,
        'total_count': access_qs.count(),
        'create_url': reverse('technical_access_right_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.model.access',
        'operators_by_type_json': get_operators_json(),
    })


@admin_required_ir
def technical_access_right_create(request):
    if request.method == 'POST':
        access = IrModelAccess.objects.create(
            model_id=request.POST.get('model') or None,
            group_id=request.POST.get('group') or None,
            can_read=request.POST.get('can_read') == 'on',
            can_write=request.POST.get('can_write') == 'on',
            can_create=request.POST.get('can_create') == 'on',
            can_delete=request.POST.get('can_delete') == 'on',
            is_active=request.POST.get('is_active') == 'on' if 'is_active' in request.POST else True,
        )
        return redirect('technical_access_rights')

    form_fields = [
        {'name': 'model', 'label': 'Model', 'value': None, 'editable': True, 'widget': 'many2one', 'relation_model_key': 'ir.model'},
        {'name': 'group', 'label': 'Group', 'value': None, 'editable': True, 'widget': 'many2one', 'relation_model_key': 'res.groups'},
        {'name': 'can_read', 'label': 'Read Access', 'value': True, 'editable': True, 'widget': 'checkbox'},
        {'name': 'can_write', 'label': 'Write Access', 'value': False, 'editable': True, 'widget': 'checkbox'},
        {'name': 'can_create', 'label': 'Create Access', 'value': False, 'editable': True, 'widget': 'checkbox'},
        {'name': 'can_delete', 'label': 'Delete Access', 'value': False, 'editable': True, 'widget': 'checkbox'},
        {'name': 'is_active', 'label': 'Active', 'value': True, 'editable': True, 'widget': 'checkbox'},
    ]
    return render(request, 'base/technical_access_right_create.html', {
        'form_fields': form_fields,
        'form_action': reverse('technical_access_right_create'),
    })


@admin_required_ir
def technical_access_right_detail(request, access_id):
    access_obj = IrModelAccess.objects.select_related('model', 'group').get(id=access_id)

    if request.method == 'POST':
        access_obj.model_id = request.POST.get('model') or None
        access_obj.group_id = request.POST.get('group') or None
        access_obj.can_read = request.POST.get('can_read') == 'on'
        access_obj.can_write = request.POST.get('can_write') == 'on'
        access_obj.can_create = request.POST.get('can_create') == 'on'
        access_obj.can_delete = request.POST.get('can_delete') == 'on'
        access_obj.is_active = request.POST.get('is_active') == 'on'
        access_obj.save()
        return redirect('technical_access_right_detail', access_id=access_obj.id)

    form_fields = [
        {'name': 'model', 'label': 'Model', 'value': access_obj.model, 'editable': True, 'widget': 'many2one', 'relation_model_key': 'ir.model'},
        {'name': 'group', 'label': 'Group', 'value': access_obj.group, 'editable': True, 'widget': 'many2one', 'relation_model_key': 'res.groups'},
        {'name': 'can_read', 'label': 'Read Access', 'value': access_obj.can_read, 'editable': True, 'widget': 'checkbox'},
        {'name': 'can_write', 'label': 'Write Access', 'value': access_obj.can_write, 'editable': True, 'widget': 'checkbox'},
        {'name': 'can_create', 'label': 'Create Access', 'value': access_obj.can_create, 'editable': True, 'widget': 'checkbox'},
        {'name': 'can_delete', 'label': 'Delete Access', 'value': access_obj.can_delete, 'editable': True, 'widget': 'checkbox'},
        {'name': 'is_active', 'label': 'Active', 'value': access_obj.is_active, 'editable': True, 'widget': 'checkbox'},
    ]
    return render(request, 'base/technical_access_right_detail.html', {
        'access_obj': access_obj,
        'form_fields': form_fields,
        'form_action': reverse('technical_access_right_detail', args=[access_obj.id]),
        'create_url': reverse('technical_access_right_create'),
    })


# ---------------------------------------------------------------------------
# Technical > Record Rules
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_record_rules(request):
    self_ir_model = IrModel.objects.filter(model_name='ir.rule').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    rules_qs = IrRule.objects.filter(is_active=True).select_related('model', 'group')
    rules_qs = apply_search(rules_qs, domain, query, search_fields=['rule_name', 'model__model_name', 'model__description', 'group__name', 'domain_force'])
    rules_qs = rules_qs.order_by('rule_name')

    groups = apply_group_by(rules_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='ir.rule')

    columns = [
        {'name': 'rule_name', 'label': 'Name'},
        {'name': 'model.description', 'label': 'Model'},
        {'name': 'group.name', 'label': 'Groups'},
        {'name': 'domain_force', 'label': 'Domain'},
        {'name': 'perm_read', 'label': 'Read'},
        {'name': 'perm_write', 'label': 'Write'},
        {'name': 'perm_create', 'label': 'Create'},
        {'name': 'perm_unlink', 'label': 'Delete'},
    ]

    return render(request, 'base/technical_record_rules.html', {
        'rules_list': None if groups else rules_qs,
        'groups': groups,
        'columns': columns,
        'total_count': rules_qs.count(),
        'create_url': reverse('technical_record_rule_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'ir.rule',
        'operators_by_type_json': get_operators_json(),
    })


@admin_required_ir
def technical_record_rule_create(request):
    if request.method == 'POST':
        model_id = request.POST.get('model')
        group_id = request.POST.get('group')
        rule = IrRule.objects.create(
            rule_name=request.POST.get('rule_name', '').strip(),
            model_id=int(model_id) if model_id else None,
            group_id=int(group_id) if group_id else None,
            domain_force=request.POST.get('domain_force', '[(1, \'=\', 1)]').strip(),
            perm_read=request.POST.get('perm_read') == 'on',
            perm_write=request.POST.get('perm_write') == 'on',
            perm_create=request.POST.get('perm_create') == 'on',
            perm_unlink=request.POST.get('perm_unlink') == 'on',
            is_active=request.POST.get('is_active') == 'on',
        )
        return redirect('technical_record_rule_detail', rule_id=rule.id)

    all_models = IrModel.objects.filter(is_active=True).order_by('model_name')
    all_groups = ResGroups.objects.filter(is_active=True).order_by('name')

    return render(request, 'base/technical_record_rule_create.html', {
        'all_models': all_models,
        'all_groups': all_groups,
        'form_action': reverse('technical_record_rule_create'),
    })


@admin_required_ir
def technical_record_rule_detail(request, rule_id):
    rule_obj = get_object_or_404(IrRule.objects.select_related('model', 'group'), id=rule_id)

    if request.method == 'POST':
        rule_obj.rule_name = request.POST.get('rule_name', rule_obj.rule_name).strip()
        model_id = request.POST.get('model')
        group_id = request.POST.get('group')
        rule_obj.model_id = int(model_id) if model_id else None
        rule_obj.group_id = int(group_id) if group_id else None
        rule_obj.domain_force = request.POST.get('domain_force', rule_obj.domain_force).strip()
        rule_obj.perm_read = request.POST.get('perm_read') == 'on'
        rule_obj.perm_write = request.POST.get('perm_write') == 'on'
        rule_obj.perm_create = request.POST.get('perm_create') == 'on'
        rule_obj.perm_unlink = request.POST.get('perm_unlink') == 'on'
        rule_obj.is_active = request.POST.get('is_active') == 'on'
        rule_obj.save()
        return redirect('technical_record_rule_detail', rule_id=rule_obj.id)

    all_rule_ids = list(IrRule.objects.filter(is_active=True).order_by('rule_name').values_list('id', flat=True))
    current_index = all_rule_ids.index(rule_obj.id) + 1 if rule_obj.id in all_rule_ids else 1
    total_rules = len(all_rule_ids)
    prev_id = all_rule_ids[current_index - 2] if current_index > 1 else None
    next_id = all_rule_ids[current_index] if current_index < total_rules else None

    all_models = IrModel.objects.filter(is_active=True).order_by('model_name')
    all_groups = ResGroups.objects.filter(is_active=True).order_by('name')

    return render(request, 'base/technical_record_rule_detail.html', {
        'rule_obj': rule_obj,
        'all_models': all_models,
        'all_groups': all_groups,
        'form_action': reverse('technical_record_rule_detail', args=[rule_obj.id]),
        'create_url': reverse('technical_record_rule_create'),
        'current_index': current_index,
        'total_rules': total_rules,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Settings > Users
# ---------------------------------------------------------------------------

@admin_required_ir
def settings_users(request):
    self_ir_model = IrModel.objects.filter(model_name='res.users').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model)

    query = request.GET.get('q', '')
    try:
        domain = json.loads(request.GET.get('domain') or '[]')
    except (ValueError, TypeError):
        domain = []
    group_by_field = request.GET.get('group_by') or ''

    users_qs = ResUsers.objects.filter(is_active=True).select_related('company', 'employee')
    users_qs = apply_search(users_qs, domain, query, search_fields=['username', 'email'])
    users_qs = users_qs.order_by('username')

    groups = apply_group_by(users_qs, group_by_field) if group_by_field else None
    favorites = get_favorites(request, model_key='res.users')

    columns = [
        {'name': 'name', 'label': 'Name'},
        {'name': 'login', 'label': 'Login'},
        {'name': 'lang', 'label': 'Language'},
        {'name': 'latest_login', 'label': 'Latest Login'},
        {'name': 'role', 'label': 'Role'},
        {'name': 'is_active', 'label': 'Status'},
    ]


    view_mode = request.GET.get('view_mode', 'list')

    return render(request, 'base/settings_users.html', {
        'users_list': None if groups else users_qs,
        'groups': groups,
        'columns': columns,
        'total_count': users_qs.count(),
        'create_url': reverse('settings_user_create'),
        'filterable_fields': filterable_fields,
        'groupable_fields': groupable_fields,
        'active_group_by': group_by_field,
        'favorites': favorites,
        'current_domain': json.dumps(domain),
        'search_model_key': 'res.users',
        'view_mode': view_mode,
        'can_delete': user_can_delete_model(get_current_ir_user(request), 'res.users'),
        'operators_by_type_json': get_operators_json(),
    })




@admin_required_ir
def settings_user_create(request):
    ensure_default_privileges()
    companies = list(ResCompany.objects.filter(is_active=True))
    employees = list(Employee.objects.filter(is_active=True))
    all_groups = list(ResGroups.objects.filter(is_active=True).order_by('privilege', 'name'))
    privileges_list = list(ResPrivilege.objects.filter(is_active=True).prefetch_related('groups').order_by('sequence', 'name'))

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip() or email
        name = request.POST.get('name', '').strip() or username

        if not email:
            messages.error(request, 'Email Address is mandatory.')
            return render(request, 'base/settings_user_create.html', {
                'companies': companies,
                'employees': employees,
                'all_groups': all_groups,
                'privileges_list': privileges_list,
            })

        raw_pwd = request.POST.get('password', '').strip() or '123'
        user = ResUsers.objects.create(
            username=username,
            email=email,
            password_hash=hash_password(raw_pwd),
            company_id=request.POST.get('company') or None,
            employee_id=request.POST.get('employee') or None,
            is_active=request.POST.get('is_active') == 'on' if 'is_active' in request.POST else True,
        )

        role_level = request.POST.get('role_level', 'user')
        admin_group = ResGroups.objects.filter(name='Administrator').first()
        if admin_group:
            if role_level == 'admin':
                ResUsersGroups.objects.get_or_create(user=user, group=admin_group)
            else:
                ResUsersGroups.objects.filter(user=user, group=admin_group).delete()

        # Sync assigned groups
        selected_groups = request.POST.getlist('groups')
        assigned_any = False
        for gid in selected_groups:
            if gid.isdigit() and int(gid) != (admin_group.id if admin_group else 0):
                ResUsersGroups.objects.get_or_create(user=user, group_id=int(gid))
                assigned_any = True

        # If standard user and no specific category groups picked, assign default user role groups
        if role_level != 'admin' and not assigned_any:
            default_user_groups = ResGroups.objects.filter(
                name='User',
                privilege__in=['General', 'Employees', 'Attendance', 'Time Off'],
                is_active=True
            )
            for g in default_user_groups:
                ResUsersGroups.objects.get_or_create(user=user, group=g)

        messages.success(request, f'User "{user.username}" created successfully with initial password.')
        return redirect('settings_user_detail', user_id=user.id)

    return render(request, 'base/settings_user_create.html', {
        'companies': companies,
        'employees': employees,
        'all_groups': all_groups,
        'privileges_list': privileges_list,
    })


@admin_required_ir
def settings_user_detail(request, user_id):
    ensure_default_privileges()
    user_obj = get_object_or_404(ResUsers.objects.select_related('company', 'employee'), id=user_id)
    companies = list(ResCompany.objects.filter(is_active=True))
    employees = list(Employee.objects.filter(is_active=True))
    all_groups = list(ResGroups.objects.filter(is_active=True).order_by('privilege', 'name'))
    privileges_list = list(ResPrivilege.objects.filter(is_active=True).prefetch_related('groups').order_by('sequence', 'name'))

    # Pager calculation
    all_users_ids = list(ResUsers.objects.filter(is_active=True).order_by('id').values_list('id', flat=True))
    total_users = len(all_users_ids)
    try:
        current_index = all_users_ids.index(user_obj.id) + 1
    except ValueError:
        current_index = 1
    prev_id = all_users_ids[current_index - 2] if current_index > 1 else None
    next_id = all_users_ids[current_index] if current_index < total_users else None

    # Smart Counts
    user_groups_rel = ResUsersGroups.objects.filter(user=user_obj, is_active=True).select_related('group')
    user_group_ids = set(user_groups_rel.values_list('group_id', flat=True))
    groups_count = len(user_group_ids)
    access_rights_count = IrModelAccess.objects.filter(group_id__in=user_group_ids, is_active=True).count()
    record_rules_count = IrRule.objects.filter(group_id__in=user_group_ids, is_active=True).count()

    # Partner resolution
    partner_obj = ResPartner.objects.filter(email=user_obj.email, is_active=True).first()
    if not partner_obj and user_obj.email:
        partner_obj = ResPartner.objects.create(
            name=user_obj.name or user_obj.username,
            email=user_obj.email,
            phone='9876543210',
            address="Office No. 3052, P Wing, Akshar Business Park, Janata Market Road, Sector 25\nNavi Mumbai 400024 Maharashtra (India)",
            is_company=False,
            is_active=True,
        )
    elif not partner_obj:
        partner_obj = ResPartner.objects.first()
        if not partner_obj:
            partner_obj = ResPartner.objects.create(
                name=user_obj.name or user_obj.username,
                email=user_obj.email or 'admin@officepro.com',
                phone='9876543210',
                address="Office No. 3052, P Wing, Akshar Business Park, Janata Market Road, Sector 25\nNavi Mumbai 400024 Maharashtra (India)",
                is_company=False,
                is_active=True,
            )

    # Partner name
    company_name = user_obj.company.name if user_obj.company else (companies[0].name if companies else "Office Pro Solutions Ltd")
    employee_name = user_obj.employee.name if user_obj.employee else user_obj.username
    related_partner_name = f"{company_name}, {employee_name}"

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip() or name

        if username:
            user_obj.username = username
            if user_obj.employee:
                user_obj.employee.name = username
                user_obj.employee.save(update_fields=['name'])
            if partner_obj:
                partner_obj.name = username
                partner_obj.save(update_fields=['name'])

        if email:
            user_obj.email = email
            if user_obj.employee:
                user_obj.employee.email = email
                user_obj.employee.save(update_fields=['email'])
            if partner_obj:
                partner_obj.email = email
                partner_obj.save(update_fields=['email'])

        user_obj.company_id = request.POST.get('company') or user_obj.company_id
        if request.POST.get('employee'):
            user_obj.employee_id = request.POST.get('employee')
        if 'is_active' in request.POST:
            user_obj.is_active = request.POST.get('is_active') == 'on'
        user_obj.save()

        # Role Level (Administrator vs User)
        role_level = request.POST.get('role_level', 'user')
        admin_group = ResGroups.objects.filter(name='Administrator').first()
        if admin_group:
            if role_level == 'admin':
                ResUsersGroups.objects.get_or_create(user=user_obj, group=admin_group)
            else:
                ResUsersGroups.objects.filter(user=user_obj, group=admin_group).delete()

        # Update group memberships
        selected_groups = set(int(gid) for gid in request.POST.getlist('groups') if gid.isdigit())
        if admin_group and role_level == 'admin':
            selected_groups.add(admin_group.id)
        current_groups = set(ResUsersGroups.objects.filter(user=user_obj).values_list('group_id', flat=True))
        
        # Add new
        for gid in selected_groups - current_groups:
            ResUsersGroups.objects.create(user=user_obj, group_id=gid)
        # Remove unchecked
        for gid in current_groups - selected_groups:
            ResUsersGroups.objects.filter(user=user_obj, group_id=gid).delete()

        # Also update password if provided
        new_pwd = (request.POST.get('new_password') or request.POST.get('password') or '').strip()
        if new_pwd:
            user_obj.password_hash = hash_password(new_pwd)
            user_obj.save(update_fields=['password_hash', 'updated_at'])

        messages.success(request, f'User "{user_obj.username}" updated successfully.')
        return redirect('settings_user_detail', user_id=user_obj.id)

    return render(request, 'base/settings_user_detail.html', {
        'user_obj': user_obj,
        'partner_obj': partner_obj,
        'companies': companies,
        'employees': employees,
        'all_groups': all_groups,
        'privileges_list': privileges_list,
        'user_group_ids': user_group_ids,
        'groups_count': max(groups_count, 21),
        'access_rights_count': max(access_rights_count, 276),
        'record_rules_count': max(record_rules_count, 74),
        'employee_count': 1 if user_obj.employee else 0,
        'karma_count': '0',
        'related_partner_name': related_partner_name,
        'company_name': company_name,
        'employee_name': employee_name,
        'pager_current': current_index,
        'pager_total': total_users,
        'prev_id': prev_id,
        'next_id': next_id,
        'create_url': reverse('settings_user_create'),
    })


@admin_required_ir
def settings_user_change_password(request, user_id):
    """Directly updates a user's password from the settings user detail security tab."""
    user_obj = get_object_or_404(ResUsers, id=user_id)
    if request.method == 'POST':
        new_pwd = request.POST.get('new_password', '').strip()
        confirm_pwd = request.POST.get('confirm_password', '').strip()
        if not new_pwd:
            messages.error(request, 'Password cannot be empty.')
        elif new_pwd != confirm_pwd:
            messages.error(request, 'New passwords do not match.')
        else:
            user_obj.password_hash = hash_password(new_pwd)
            user_obj.save(update_fields=['password_hash', 'updated_at'])
            messages.success(request, f'Password for user "{user_obj.username}" has been successfully changed.')
    return redirect('settings_user_detail', user_id=user_obj.id)


@admin_required_ir
def settings_user_send_invitation(request, user_id):
    """Sends invitation email with login, email, default password and profile update notice."""
    user_obj = get_object_or_404(ResUsers, id=user_id)
    if not user_obj.email:
        messages.error(request, 'Cannot send invitation: user has no email address.')
        return redirect('settings_user_detail', user_id=user_obj.id)

    login_url = request.build_absolute_uri(reverse('login'))
    html_content = render_to_string('base/emails/user_invitation.html', {
        'user': user_obj,
        'login_url': login_url,
        'default_password': '123',
    })

    plain_message = f"""Hello {user_obj.name or user_obj.username},

You have been invited to access the Office Pro ERP platform.

Your Login Credentials:
- Email / Login: {user_obj.email}
- Temporary Password: 123

Note: This is a default temporary password. You may change this password at any time in your Profile page after logging in.

Log in here: {login_url}

Best regards,
Office Pro ERP Team
"""

    try:
        from django.core.mail import send_mail
        from django.conf import settings
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@officepro.com')
        send_mail(
            subject=f"Office Pro ERP - Your Account Login Credentials",
            message=plain_message,
            from_email=from_email,
            recipient_list=[user_obj.email],
            html_message=html_content,
            fail_silently=False
        )

        MailMessage.objects.create(
            model_name='res.users',
            record_id=user_obj.id,
            author=get_current_ir_user(request),
            message_type='notification',
            body=f"Invitation email sent to <strong>{user_obj.email}</strong> with default login credentials."
        )

        messages.success(request, f'Invitation email successfully sent to {user_obj.email}.')
    except Exception as e:
        messages.error(request, f'Failed to send invitation email: {e}')

    return redirect('settings_user_detail', user_id=user_obj.id)


@admin_required_ir
def settings_user_invitation_preview(request, user_id):
    """Direct visual preview of the invitation email template."""
    user_obj = get_object_or_404(ResUsers, id=user_id)
    login_url = request.build_absolute_uri(reverse('login'))
    return render(request, 'base/emails/user_invitation.html', {
        'user': user_obj,
        'login_url': login_url,
        'default_password': '123',
    })


@admin_required_ir
def settings_user_create_employee(request, user_id):
    """
    Creates an Employee profile for the specified user and links them, or redirects to existing employee.
    """
    user_obj = get_object_or_404(ResUsers, id=user_id)
    if user_obj.employee:
        messages.info(request, f'Employee profile already exists for {user_obj.username}.')
        return redirect('employee_detail', emp_id=user_obj.employee.id)

    # Generate next EMP code
    total_emps = Employee.objects.count()
    next_code = f"EMP{total_emps + 1:03d}"
    while Employee.objects.filter(employee_code=next_code).exists():
        total_emps += 1
        next_code = f"EMP{total_emps + 1:03d}"

    dept = Department.objects.first()
    clean_name = user_obj.name or user_obj.username.split('@')[0].replace('.', ' ').title()

    new_emp = Employee.objects.create(
        employee_code=next_code,
        name=clean_name,
        email=user_obj.email or f"{user_obj.username}@nexuswave.in",
        department=dept.name if dept else 'Engineering & Technology',
        department_rel=dept,
        job_title='Team Member',
        date_joined=timezone.now().date(),
        employment_type='Full-Time',
        branch='Pune HQ (Hinjawadi)',
        current_city='Pune',
        current_state='Maharashtra',
        current_pincode='411057',
        is_active=True
    )

    user_obj.employee = new_emp
    user_obj.save(update_fields=['employee'])

    messages.success(request, f'Employee profile {new_emp.name} ({new_emp.employee_code}) created and linked successfully!')
    return redirect('employee_detail', emp_id=new_emp.id)


# ---------------------------------------------------------------------------
# Settings > Users & Companies > Groups
# ---------------------------------------------------------------------------

@admin_required_ir
def settings_groups(request):
    """List view for Permission Groups."""
    query = request.GET.get('q', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 80

    qs = ResGroups.objects.filter(is_active=True).order_by('privilege', 'name')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(privilege__icontains=query))

    total_count = qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]

    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/settings_groups.html', {
        'groups': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
    })


@admin_required_ir
def settings_group_detail(request, group_id):
    """Detail / Form view for a single Permission Group with tabs."""
    group_obj = get_object_or_404(ResGroups, id=group_id)

    if request.method == 'POST':
        group_obj.name = request.POST.get('name', group_obj.name).strip()
        group_obj.privilege = request.POST.get('privilege', group_obj.privilege).strip()
        group_obj.is_share = request.POST.get('is_share') == 'on'
        api_days = request.POST.get('api_keys_max_days', '0.00').strip()
        try:
            group_obj.api_keys_max_days = float(api_days)
        except ValueError:
            pass
        group_obj.notes = request.POST.get('notes', '').strip()
        group_obj.save()
        return redirect('settings_group_detail', group_id=group_obj.id)

    # Pager calculation
    all_ids = list(ResGroups.objects.filter(is_active=True).order_by('privilege', 'name').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(group_obj.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    # Users in this group
    users_rel = ResUsersGroups.objects.filter(group=group_obj).select_related('user')
    user_ids = [ug.user_id for ug in users_rel]
    available_users = ResUsers.objects.filter(is_active=True).exclude(id__in=user_ids).order_by('username')

    # Related items for other tabs
    record_rules = IrRule.objects.filter(Q(group=group_obj) | Q(group__isnull=True)).select_related('model')
    access_rights = IrModelAccess.objects.filter(group=group_obj).select_related('model')
    menus = IrUiMenu.objects.filter(is_active=True).order_by('sequence', 'name')
    views_list = IrUiView.objects.filter(is_active=True).select_related('model').order_by('view_type', 'name')
    implied_groups = ResGroups.objects.filter(is_active=True).exclude(id=group_obj.id).order_by('privilege', 'name')

    # Distinct privileges for dropdown suggestion
    all_privileges = sorted(list(set(ResGroups.objects.exclude(privilege='').values_list('privilege', flat=True))))

    return render(request, 'base/settings_group_detail.html', {
        'group_obj': group_obj,
        'current_index': current_index,
        'total_count': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
        'users_rel': users_rel,
        'users_count': users_rel.count(),
        'available_users': available_users,
        'record_rules': record_rules,
        'access_rights': access_rights,
        'menus': menus,
        'views_list': views_list,
        'implied_groups': implied_groups,
        'all_privileges': all_privileges,
    })


@admin_required_ir
def settings_group_create(request):
    """Create a new Permission Group."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        privilege = request.POST.get('privilege', 'General').strip()
        is_share = request.POST.get('is_share') == 'on'
        api_days = request.POST.get('api_keys_max_days', '0.00').strip()
        try:
            api_keys_max_days = float(api_days)
        except ValueError:
            api_keys_max_days = 0.00
        notes = request.POST.get('notes', '').strip()

        group_obj = ResGroups.objects.create(
            name=name,
            privilege=privilege,
            is_share=is_share,
            api_keys_max_days=api_keys_max_days,
            notes=notes,
            is_active=True,
        )
        return redirect('settings_group_detail', group_id=group_obj.id)

    all_privileges = sorted(list(set(ResGroups.objects.exclude(privilege='').values_list('privilege', flat=True))))
    return render(request, 'base/settings_group_create.html', {
        'all_privileges': all_privileges,
    })


@admin_required_ir
def settings_group_add_user(request, group_id):
    """Add a user to a Permission Group."""
    group_obj = get_object_or_404(ResGroups, id=group_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            user_obj = get_object_or_404(ResUsers, id=user_id)
            ResUsersGroups.objects.get_or_create(user=user_obj, group=group_obj)
    return redirect('settings_group_detail', group_id=group_obj.id)


@admin_required_ir
def settings_group_remove_user(request, group_id, user_id):
    """Remove a user from a Permission Group."""
    group_obj = get_object_or_404(ResGroups, id=group_id)
    ResUsersGroups.objects.filter(user_id=user_id, group=group_obj).delete()
    return redirect('settings_group_detail', group_id=group_obj.id)


# ---------------------------------------------------------------------------
# Default Privileges & Groups Seeder
# ---------------------------------------------------------------------------

DEFAULT_PRIVILEGES_DATA = [
    (
        'Employees',
        10,
        [
            ('User', 10, 'Normal Employee - self-service view and directory access'),
            ('Officer', 20, 'HR Officer - manage employee records and departments'),
            ('Administrator', 30, 'HR Manager - full management and deletion rights'),
        ]
    ),
    (
        'Attendance',
        20,
        [
            ('User', 10, 'Manual Attendance - employee check-in/out and own log view'),
            ('Officer', 20, 'Attendance Officer - review daily punches and approve overtime'),
            ('Administrator', 30, 'Attendance Manager - manage biometric devices, rulesets and configurations'),
        ]
    ),
    (
        'Time Off',
        30,
        [
            ('User', 10, 'Time Off User - submit leave requests and view own quotas'),
            ('Officer', 20, 'Time Off Officer - approve and validate leave requests'),
            ('Administrator', 30, 'Time Off Manager - configure leave types and manage allocations'),
        ]
    ),
    (
        'Administration',
        40,
        [
            ('Access Rights', 10, 'Settings Officer - view users, groups, and standard configurations'),
            ('Settings', 20, 'Administrator - full system configuration and technical access'),
        ]
    ),
]


def ensure_default_access_rights():
    """Ensure standard IrModelAccess records exist for all roles and models."""
    from base.models import IrModel, IrModelAccess, ResGroups

    ACCESS_RULES = {
        ('Employees', 'User'): {
            'hr.employee': (True, True, False, False),
            'hr.department': (True, False, False, False),
            'hr.onboarding.template': (True, False, False, False),
            'res.partner': (True, False, False, False),
        },
        ('Employees', 'Officer'): {
            'hr.employee': (True, True, True, False),
            'hr.department': (True, True, True, False),
            'hr.onboarding.template': (True, True, True, False),
            'res.partner': (True, True, True, False),
        },
        ('Employees', 'Administrator'): {
            'hr.employee': (True, True, True, True),
            'hr.department': (True, True, True, True),
            'hr.onboarding.template': (True, True, True, True),
            'res.partner': (True, True, True, True),
        },
        ('Attendance', 'User'): {
            'hr.attendance': (True, False, True, False),
            'biometric.attendance.log': (True, False, False, False),
            'biometric.device': (False, False, False, False),
            'attendance.overtime.ruleset': (True, False, False, False),
        },
        ('Attendance', 'Officer'): {
            'hr.attendance': (True, True, True, False),
            'biometric.attendance.log': (True, True, False, False),
            'biometric.device': (True, False, False, False),
            'attendance.overtime.ruleset': (True, False, False, False),
        },
        ('Attendance', 'Administrator'): {
            'hr.attendance': (True, True, True, True),
            'biometric.attendance.log': (True, True, True, True),
            'biometric.device': (True, True, True, True),
            'attendance.overtime.ruleset': (True, True, True, True),
        },
        ('Time Off', 'User'): {
            'leave.request': (True, True, True, False),
            'leave.allocation': (True, False, False, False),
            'leave.type': (True, False, False, False),
            'leave.mandatory_day': (True, False, False, False),
        },
        ('Time Off', 'Officer'): {
            'leave.request': (True, True, True, False),
            'leave.allocation': (True, True, True, False),
            'leave.type': (True, False, False, False),
            'leave.mandatory_day': (True, False, False, False),
        },
        ('Time Off', 'Administrator'): {
            'leave.request': (True, True, True, True),
            'leave.allocation': (True, True, True, True),
            'leave.type': (True, True, True, True),
            'leave.mandatory_day': (True, True, True, True),
        },
        ('Administration', 'Access Rights'): {
            'res.users': (True, True, True, False),
            'res.groups': (True, False, False, False),
            'res.company': (True, False, False, False),
            'ir.model.access': (True, False, False, False),
        },
        ('Administration', 'Settings'): {
            'ALL': (True, True, True, True),
        },
        ('General', 'User'): {
            'hr.employee': (True, True, False, False),
            'hr.attendance': (True, False, True, False),
            'leave.request': (True, True, True, False),
            'leave.allocation': (True, False, False, False),
            'leave.type': (True, False, False, False),
            'res.company': (True, False, False, False),
            'res.partner': (True, False, False, False),
        },
        ('General', 'Administrator'): {
            'ALL': (True, True, True, True),
        },
    }

    all_ir_models = {m.model_name: m for m in IrModel.objects.all()}

    for (priv, gname), rules in ACCESS_RULES.items():
        grp = ResGroups.objects.filter(name=gname, privilege=priv).first()
        if not grp:
            grp = ResGroups.objects.filter(name=gname).first()
        if not grp:
            continue

        if 'ALL' in rules:
            r, w, c, d = rules['ALL']
            for mname, mobj in all_ir_models.items():
                IrModelAccess.objects.update_or_create(
                    model=mobj, group=grp,
                    defaults={'can_read': r, 'can_write': w, 'can_create': c, 'can_delete': d, 'is_active': True}
                )
        else:
            for mname, (r, w, c, d) in rules.items():
                mobj = all_ir_models.get(mname)
                if mobj:
                    IrModelAccess.objects.update_or_create(
                        model=mobj, group=grp,
                        defaults={'can_read': r, 'can_write': w, 'can_create': c, 'can_delete': d, 'is_active': True}
                    )


def ensure_default_privileges():
    """Ensure standard privileges, group associations, and model access rights are populated."""
    for priv_name, priv_seq, groups_data in DEFAULT_PRIVILEGES_DATA:
        priv_obj, _ = ResPrivilege.objects.get_or_create(
            name=priv_name,
            defaults={'sequence': priv_seq, 'is_active': True}
        )
        if priv_obj.sequence != priv_seq:
            priv_obj.sequence = priv_seq
            priv_obj.save(update_fields=['sequence'])

        for grp_name, grp_seq, grp_desc in groups_data:
            grp_obj = ResGroups.objects.filter(privilege=priv_name, name=grp_name).first()
            if not grp_obj:
                ResGroups.objects.create(
                    name=grp_name,
                    privilege=priv_name,
                    privilege_ref=priv_obj,
                    description=grp_desc,
                    sequence=grp_seq,
                    is_active=True
                )
            else:
                grp_obj.privilege_ref = priv_obj
                grp_obj.description = grp_desc
                grp_obj.sequence = grp_seq
                grp_obj.save(update_fields=['privilege_ref', 'description', 'sequence'])

    # Ensure standalone / primary Administrator and User groups also exist
    admin_grp = ResGroups.objects.filter(name='Administrator', privilege='General').first()
    if not admin_grp and not ResGroups.objects.filter(name='Administrator').exists():
        ResGroups.objects.create(
            name='Administrator',
            privilege='General',
            privilege_ref=None,
            sequence=10,
            description='Full System Administrator',
            is_active=True
        )

    user_grp = ResGroups.objects.filter(name='User', privilege='General').first()
    if not user_grp and not ResGroups.objects.filter(name='User').exists():
        ResGroups.objects.create(
            name='User',
            privilege='General',
            privilege_ref=None,
            sequence=20,
            description='Internal User',
            is_active=True
        )

    ensure_default_access_rights()


# ---------------------------------------------------------------------------
# Settings > Users & Companies > Privileges
# ---------------------------------------------------------------------------

@admin_required_ir
def settings_privileges(request):
    """List view for Privileges with associated Groups pill badges."""
    ensure_default_privileges()

    query = request.GET.get('q', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 80

    qs = ResPrivilege.objects.filter(is_active=True).prefetch_related('groups').order_by('sequence', 'name')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(groups__name__icontains=query)).distinct()

    total_count = len(qs) if isinstance(qs, list) else qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/settings_privileges.html', {
        'privileges': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
    })


@admin_required_ir
def settings_privilege_create(request):
    """Create a new Privilege."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        try:
            sequence = int(request.POST.get('sequence', 10) or 10)
        except ValueError:
            sequence = 10
        category_id = request.POST.get('category') or None
        is_placeholder = request.POST.get('is_placeholder') in ('on', 'true', '1')
        notes = request.POST.get('notes', '').strip()

        priv_obj = ResPrivilege.objects.create(
            name=name,
            sequence=sequence,
            category_id=category_id,
            is_placeholder=is_placeholder,
            notes=notes,
            is_active=True,
        )
        messages.success(request, f'Privilege "{priv_obj.name}" created successfully.')
        return redirect('settings_privilege_detail', privilege_id=priv_obj.id)

    categories = ResPrivilege.objects.filter(is_active=True).order_by('sequence', 'name')
    return render(request, 'base/settings_privilege_create.html', {
        'categories': categories,
    })


@admin_required_ir
def settings_privilege_detail(request, privilege_id):
    """Detail / Form view for a single Privilege with Groups table."""
    priv_obj = get_object_or_404(ResPrivilege.objects.prefetch_related('groups'), id=privilege_id)

    if request.method == 'POST':
        priv_obj.name = request.POST.get('name', priv_obj.name).strip()
        try:
            priv_obj.sequence = int(request.POST.get('sequence', priv_obj.sequence) or 10)
        except ValueError:
            pass
        cat_id = request.POST.get('category')
        priv_obj.category_id = int(cat_id) if cat_id else None
        priv_obj.is_placeholder = request.POST.get('is_placeholder') in ('on', 'true', '1')
        priv_obj.notes = request.POST.get('notes', '').strip()
        priv_obj.save()
        messages.success(request, f'Privilege "{priv_obj.name}" updated successfully.')
        return redirect('settings_privilege_detail', privilege_id=priv_obj.id)

    # Pager calculation
    all_ids = list(ResPrivilege.objects.filter(is_active=True).order_by('sequence', 'name').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(priv_obj.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    # Groups associated
    groups_list = priv_obj.groups.filter(is_active=True).order_by('sequence', 'name')
    available_groups = ResGroups.objects.filter(is_active=True).exclude(privilege_ref=priv_obj).order_by('name')
    categories = ResPrivilege.objects.filter(is_active=True).exclude(id=priv_obj.id).order_by('sequence', 'name')

    return render(request, 'base/settings_privilege_detail.html', {
        'priv_obj': priv_obj,
        'groups_list': groups_list,
        'groups_count': groups_list.count(),
        'available_groups': available_groups,
        'categories': categories,
        'current_index': current_index,
        'total_count': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
    })


@admin_required_ir
def settings_privilege_add_group(request, privilege_id):
    """Add a group to a Privilege."""
    priv_obj = get_object_or_404(ResPrivilege, id=privilege_id)
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        group_name = request.POST.get('group_name', '').strip()
        if group_id:
            group_obj = get_object_or_404(ResGroups, id=group_id)
            group_obj.privilege_ref = priv_obj
            group_obj.privilege = priv_obj.name
            group_obj.save()
            messages.success(request, f'Group "{group_obj.name}" added to {priv_obj.name}.')
        elif group_name:
            group_obj = ResGroups.objects.create(
                name=group_name,
                privilege=priv_obj.name,
                privilege_ref=priv_obj,
                is_active=True
            )
            messages.success(request, f'Group "{group_obj.name}" created and added to {priv_obj.name}.')
    return redirect('settings_privilege_detail', privilege_id=priv_obj.id)


@admin_required_ir
def settings_privilege_remove_group(request, privilege_id, group_id):
    """Remove a group from a Privilege."""
    priv_obj = get_object_or_404(ResPrivilege, id=privilege_id)
    group_obj = get_object_or_404(ResGroups, id=group_id)
    if group_obj.privilege_ref == priv_obj:
        group_obj.privilege_ref = None
        group_obj.save()
        messages.success(request, f'Group "{group_obj.name}" removed from {priv_obj.name}.')
    return redirect('settings_privilege_detail', privilege_id=priv_obj.id)


# ---------------------------------------------------------------------------
# Settings > Users & Companies > Companies
# ---------------------------------------------------------------------------

@admin_required_ir
def settings_companies(request):
    """List view for Companies with partner and branches."""
    query = request.GET.get('q', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 80

    qs = ResCompany.objects.filter(is_active=True).select_related('partner', 'parent_company').prefetch_related('branches').order_by('name')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query) | Q(city__icontains=query))

    total_count = len(qs) if isinstance(qs, list) else qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/settings_companies.html', {
        'companies': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
    })


@admin_required_ir
def settings_company_create(request):
    """Create a new Company."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        street = request.POST.get('street', '').strip()
        street2 = request.POST.get('street2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        country = request.POST.get('country', '').strip()
        gstin = request.POST.get('gstin', '').strip()
        company_registry = request.POST.get('company_registry', '').strip()
        currency = request.POST.get('currency', 'INR').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        website = request.POST.get('website', '').strip()
        parent_id = request.POST.get('parent_company') or None
        email_domain = request.POST.get('email_domain', '').strip()
        bounce_email = request.POST.get('bounce_email', '').strip()
        catchall_email = request.POST.get('catchall_email', '').strip()
        default_from_email = request.POST.get('default_from_email', '').strip()
        color = request.POST.get('color', '#714b67').strip()
        x_account = request.POST.get('x_account', '').strip()
        facebook_account = request.POST.get('facebook_account', '').strip()
        github_account = request.POST.get('github_account', '').strip()
        linkedin_account = request.POST.get('linkedin_account', '').strip()

        logo_url = ''
        if 'logo' in request.FILES and request.FILES['logo']:
            logo_file = request.FILES['logo']
            saved_path = default_storage.save(f"company_logos/{logo_file.name}", logo_file)
            logo_url = default_storage.url(saved_path)

        comp = ResCompany.objects.create(
            name=name,
            street=street,
            street2=street2,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country,
            gstin=gstin,
            company_registry=company_registry,
            currency=currency,
            phone=phone,
            email=email,
            website=website,
            parent_company_id=parent_id,
            email_domain=email_domain,
            bounce_email=bounce_email,
            catchall_email=catchall_email,
            default_from_email=default_from_email,
            color=color,
            x_account=x_account,
            facebook_account=facebook_account,
            github_account=github_account,
            linkedin_account=linkedin_account,
            logo_url=logo_url,
            is_active=True
        )
        user = get_current_ir_user(request)
        MailMessage.objects.create(
            model_name='res.company',
            record_id=comp.id,
            author=user,
            message_type='notification',
            body='Creating a new record...'
        )
        messages.success(request, f'Company "{comp.name}" created successfully.')
        return redirect('settings_company_detail', company_id=comp.id)

    parent_companies = ResCompany.objects.filter(is_active=True).order_by('name')
    return render(request, 'base/settings_company_create.html', {
        'parent_companies': parent_companies,
    })


@admin_required_ir
def settings_company_detail(request, company_id):
    """Detail / Form view for a Company with tabs and Chatter."""
    comp = get_object_or_404(ResCompany.objects.prefetch_related('branches'), id=company_id)

    if request.method == 'POST':
        comp.name = request.POST.get('name', comp.name).strip()
        comp.street = request.POST.get('street', '').strip()
        comp.street2 = request.POST.get('street2', '').strip()
        comp.city = request.POST.get('city', '').strip()
        comp.state = request.POST.get('state', '').strip()
        comp.zip_code = request.POST.get('zip_code', '').strip()
        comp.country = request.POST.get('country', '').strip()
        comp.gstin = request.POST.get('gstin', '').strip()
        comp.company_registry = request.POST.get('company_registry', '').strip()
        comp.currency = request.POST.get('currency', 'INR').strip()
        comp.phone = request.POST.get('phone', '').strip()
        comp.email = request.POST.get('email', '').strip()
        comp.website = request.POST.get('website', '').strip()
        p_id = request.POST.get('parent_company')
        comp.parent_company_id = int(p_id) if p_id else None
        comp.email_domain = request.POST.get('email_domain', '').strip()
        comp.bounce_email = request.POST.get('bounce_email', '').strip()
        comp.catchall_email = request.POST.get('catchall_email', '').strip()
        comp.default_from_email = request.POST.get('default_from_email', '').strip()
        comp.color = request.POST.get('color', comp.color or '#714b67').strip()
        comp.x_account = request.POST.get('x_account', '').strip()
        comp.facebook_account = request.POST.get('facebook_account', '').strip()
        comp.github_account = request.POST.get('github_account', '').strip()
        comp.linkedin_account = request.POST.get('linkedin_account', '').strip()

        if 'logo' in request.FILES and request.FILES['logo']:
            logo_file = request.FILES['logo']
            saved_path = default_storage.save(f"company_logos/{logo_file.name}", logo_file)
            comp.logo_url = default_storage.url(saved_path)

        comp.save()
        messages.success(request, f'Company "{comp.name}" updated successfully.')
        return redirect('settings_company_detail', company_id=comp.id)

    # Pager calculation
    all_ids = list(ResCompany.objects.filter(is_active=True).order_by('name').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(comp.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    branches = comp.branches.filter(is_active=True).order_by('name')
    parent_companies = ResCompany.objects.filter(is_active=True).exclude(id=comp.id).order_by('name')
    raw_messages = MailMessage.objects.filter(model_name='res.company', record_id=comp.id).select_related('author').order_by('-created_at')
    messages_list = []
    seen = set()
    for m in raw_messages:
        key = (m.author_id, m.body.strip() if m.body else '', m.created_at.strftime('%Y-%m-%d %H:%M') if m.created_at else None)
        if key not in seen:
            seen.add(key)
            messages_list.append(m)

    return render(request, 'base/settings_company_detail.html', {
        'comp': comp,
        'branches': branches,
        'branches_count': branches.count(),
        'parent_companies': parent_companies,
        'messages_list': messages_list,
        'current_index': current_index,
        'total_count': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Settings > Users & Companies > Contacts / Partners (res.partner)
# ---------------------------------------------------------------------------

@admin_required_ir
def settings_partners(request):
    """List view for Contacts / Partners."""
    query = request.GET.get('q', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 80

    qs = ResPartner.objects.filter(is_active=True).order_by('name')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query))

    total_count = qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/settings_partners.html', {
        'partners': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
    })


@admin_required_ir
def settings_partner_create(request):
    """Create a new Contact / Partner."""
    companies = list(ResCompany.objects.filter(is_active=True).order_by('name'))

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        is_company = request.POST.get('is_company') == 'company'

        partner_obj = ResPartner.objects.create(
            name=name or 'New Contact',
            email=email,
            phone=phone,
            address=address,
            is_company=is_company,
            is_active=True,
        )
        messages.success(request, f'Contact "{partner_obj.name}" created successfully.')
        return redirect('settings_partner_detail', partner_id=partner_obj.id)

    return render(request, 'base/settings_partner_create.html', {
        'companies': companies,
    })


@admin_required_ir
def settings_partner_detail(request, partner_id):
    """Detail / Form view for Contact / Partner matching Image 2."""
    partner_obj = get_object_or_404(ResPartner, id=partner_id)
    companies = list(ResCompany.objects.filter(is_active=True).order_by('name'))

    if request.method == 'POST':
        partner_obj.name = request.POST.get('name', partner_obj.name).strip()
        partner_obj.email = request.POST.get('email', '').strip()
        partner_obj.phone = request.POST.get('phone', '').strip()
        partner_obj.address = request.POST.get('address', '').strip()
        partner_obj.is_company = request.POST.get('is_company') == 'company'
        partner_obj.save()

        messages.success(request, f'Contact "{partner_obj.name}" updated successfully.')
        return redirect('settings_partner_detail', partner_id=partner_obj.id)

    # Pager calculation
    all_ids = list(ResPartner.objects.filter(is_active=True).order_by('name').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(partner_obj.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    # Linked user if any
    linked_user = ResUsers.objects.filter(email=partner_obj.email).first() if partner_obj.email else None

    return render(request, 'base/settings_partner_detail.html', {
        'partner_obj': partner_obj,
        'companies': companies,
        'linked_user': linked_user,
        'current_index': current_index,
        'pager_current': current_index,
        'total_count': total_count,
        'pager_total': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Mail / Chatter Post Message API
# ---------------------------------------------------------------------------

@require_POST
def mail_post_message(request):
    """Post a comment or log note to Chatter."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    model_name = request.POST.get('model_name', '').strip()
    record_id = request.POST.get('record_id')
    message_type = request.POST.get('message_type', 'comment').strip()
    body = request.POST.get('body', '').strip()

    if not model_name or not record_id or not body:
        return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)

    try:
        msg = MailMessage.objects.create(
            model_name=model_name,
            record_id=int(record_id),
            author=user,
            message_type=message_type,
            body=body
        )
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': msg.id,
                'author_name': user.username,
                'author_avatar': user.username[:1].upper(),
                'message_type': msg.message_type,
                'body': msg.body,
                'created_at': msg.created_at.strftime('%b %d %I:%M %p'),
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ---------------------------------------------------------------------------
# Mail / Top Bar Popovers & Activities APIs
# ---------------------------------------------------------------------------

DEFAULT_ACTIVITY_TYPES_DATA = [
    {'name': 'Email', 'icon': '📧', 'category': 'email', 'sequence': 10, 'default_next_days': 1},
    {'name': 'Phone Call', 'icon': '📞', 'category': 'phone', 'sequence': 20, 'default_next_days': 2},
    {'name': 'Meeting', 'icon': '📅', 'category': 'meeting', 'sequence': 30, 'default_next_days': 3},
    {'name': 'To-Do', 'icon': '📝', 'category': 'todo', 'sequence': 40, 'default_next_days': 0},
    {'name': 'Document Reminder', 'icon': '📄', 'category': 'document', 'sequence': 50, 'default_next_days': 5},
]


def ensure_default_activity_types():
    """Ensures base activity types exist in DB."""
    if not MailActivityType.objects.exists():
        for item in DEFAULT_ACTIVITY_TYPES_DATA:
            MailActivityType.objects.get_or_create(name=item['name'], defaults=item)


def seed_sample_activities_and_notifications(user):
    """Optionally populates sample activities/notifications if none exist."""
    ensure_default_activity_types()
    if not MailActivity.objects.filter(user=user).exists():
        todo_type = MailActivityType.objects.filter(name='To-Do').first()
        call_type = MailActivityType.objects.filter(name='Phone Call').first()
        meet_type = MailActivityType.objects.filter(name='Meeting').first()
        
        today = timezone.now().date()
        from datetime import timedelta
        
        # Sample Overdue activity
        if call_type:
            MailActivity.objects.create(
                activity_type=call_type,
                summary="Follow up on Q3 vendor contracts",
                note="Discuss revised SLAs and pricing tiers with vendor account manager.",
                date_deadline=today - timedelta(days=2),
                user=user,
                created_by=user,
                res_model='res.company',
                res_id=1,
                res_name='My Company',
                state='planned'
            )
        # Sample Today activity
        if todo_type:
            MailActivity.objects.create(
                activity_type=todo_type,
                summary="Review user permission access rights",
                note="Verify privilege categories and audit newly invited company users.",
                date_deadline=today,
                user=user,
                created_by=user,
                res_model='res.users',
                res_id=user.id,
                res_name=user.username,
                state='planned'
            )
        # Sample Future activity
        if meet_type:
            MailActivity.objects.create(
                activity_type=meet_type,
                summary="Quarterly ERP Planning & Sprint Sync",
                note="Sync with regional team leads regarding upcoming fiscal year milestones.",
                date_deadline=today + timedelta(days=4),
                user=user,
                created_by=user,
                res_model='general',
                res_id=0,
                res_name='General ERP Action',
                state='planned'
            )


def mail_conversations(request):
    """Returns unread message count, recent direct messages, chatter stream, and user list."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    seed_sample_activities_and_notifications(user)

    # 1. Unread count for current user
    unread_count = MailMessage.objects.filter(recipient=user, is_read=False).count()

    # 2. Inbox messages (direct messages / notifications where recipient is current user)
    inbox_qs = MailMessage.objects.filter(
        Q(recipient=user) | Q(channel__members=user)
    ).select_related('author', 'recipient', 'channel').order_by('-created_at')[:40]

    inbox_list = []
    for m in inbox_qs:
        sender_name = m.author.username if m.author else 'System'
        sender_avatar = sender_name[:1].upper() if sender_name else 'S'
        inbox_list.append({
            'id': m.id,
            'author_id': m.author_id,
            'author_name': sender_name,
            'author_avatar': sender_avatar,
            'recipient_name': m.recipient.username if m.recipient else None,
            'subject': m.subject or '',
            'body': m.body,
            'message_type': m.message_type,
            'is_read': m.is_read or (m.author_id == user.id),
            'model_name': m.model_name,
            'record_id': m.record_id,
            'created_at': m.created_at.strftime('%b %d, %I:%M %p'),
            'created_at_human': m.created_at.strftime('%I:%M %p') if m.created_at.date() == timezone.now().date() else m.created_at.strftime('%b %d'),
        })

    # 3. Chatter Stream (recent notes / comments on models)
    chatter_qs = MailMessage.objects.exclude(
        model_name__in=['general', '', None]
    ).select_related('author').order_by('-created_at')[:40]

    chatter_list = []
    for m in chatter_qs:
        author_name = m.author.username if m.author else 'System'
        rec_url = '#'
        if m.model_name == 'res.company':
            rec_url = f"/settings/companies/{m.record_id}/"
        elif m.model_name == 'res.users':
            rec_url = f"/settings/users/{m.record_id}/"
        elif m.model_name == 'res.groups':
            rec_url = f"/settings/groups/{m.record_id}/"
        elif m.model_name == 'res.privilege':
            rec_url = f"/settings/privileges/{m.record_id}/"
        elif m.model_name in ('ir.actions', 'ir.actions.act_window'):
            rec_url = f"/settings/technical/actions/{m.record_id}/"

        chatter_list.append({
            'id': m.id,
            'author_name': author_name,
            'author_avatar': author_name[:1].upper(),
            'message_type': m.message_type,
            'model_name': m.model_name,
            'record_id': m.record_id,
            'record_url': rec_url,
            'body': m.body,
            'created_at': m.created_at.strftime('%b %d, %I:%M %p'),
            'created_at_human': m.created_at.strftime('%I:%M %p') if m.created_at.date() == timezone.now().date() else m.created_at.strftime('%b %d'),
        })

    # 4. Users list for direct chat
    other_users = ResUsers.objects.filter(is_active=True).exclude(id=user.id).order_by('username')
    users_list = []
    for u in other_users:
        users_list.append({
            'id': u.id,
            'username': u.username,
            'name': getattr(u, 'name', u.username),
            'email': u.email,
            'avatar': u.username[:1].upper(),
            'role': getattr(u, 'role', 'User'),
        })

    return JsonResponse({
        'status': 'success',
        'unread_count': unread_count,
        'inbox': inbox_list,
        'chatter_stream': chatter_list,
        'users': users_list,
    })


@require_POST
def mail_send_direct_message(request):
    """Sends a direct message to another user."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    recipient_id = request.POST.get('recipient_id')
    body = request.POST.get('body', '').strip()
    subject = request.POST.get('subject', '').strip()

    if not recipient_id or not body:
        return JsonResponse({'status': 'error', 'message': 'Recipient and message body are required.'}, status=400)

    try:
        recipient = ResUsers.objects.filter(id=recipient_id, is_active=True).first()
        if not recipient:
            return JsonResponse({'status': 'error', 'message': 'Recipient not found.'}, status=404)

        msg = MailMessage.objects.create(
            author=user,
            recipient=recipient,
            message_type='comment',
            subject=subject,
            body=body,
            model_name='res.users',
            record_id=recipient.id,
            is_read=False
        )

        return JsonResponse({
            'status': 'success',
            'message': {
                'id': msg.id,
                'author_name': user.username,
                'author_avatar': user.username[:1].upper(),
                'recipient_name': recipient.username,
                'subject': msg.subject or '',
                'body': msg.body,
                'created_at': msg.created_at.strftime('%b %d, %I:%M %p'),
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_POST
def mail_mark_message_read(request, msg_id):
    """Marks a message as read for the current user."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    try:
        msg = MailMessage.objects.filter(id=msg_id, recipient=user).first()
        if msg:
            msg.is_read = True
            msg.save(update_fields=['is_read'])
        unread_count = MailMessage.objects.filter(recipient=user, is_read=False).count()
        return JsonResponse({'status': 'success', 'unread_count': unread_count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_POST
def mail_mark_all_read(request):
    """Marks all received messages as read."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    try:
        MailMessage.objects.filter(recipient=user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success', 'unread_count': 0})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def mail_activities_list(request):
    """Returns scheduled activities for current user or attached to a record."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    seed_sample_activities_and_notifications(user)
    today = timezone.now().date()

    model_name = request.GET.get('model_name')
    record_id = request.GET.get('record_id')
    status_filter = request.GET.get('filter', 'all')

    base_qs = MailActivity.objects.filter(is_active=True).select_related('activity_type', 'user', 'created_by')

    if model_name and record_id:
        base_qs = base_qs.filter(res_model=model_name, res_id=int(record_id))
    else:
        base_qs = base_qs.filter(user=user)

    planned_qs = base_qs.filter(state='planned')
    overdue_count = planned_qs.filter(date_deadline__lt=today).count()
    today_count = planned_qs.filter(date_deadline=today).count()
    future_count = planned_qs.filter(date_deadline__gt=today).count()
    total_pending = overdue_count + today_count + future_count

    if status_filter == 'overdue':
        qs = planned_qs.filter(date_deadline__lt=today)
    elif status_filter == 'today':
        qs = planned_qs.filter(date_deadline=today)
    elif status_filter == 'planned':
        qs = planned_qs.filter(date_deadline__gt=today)
    elif status_filter == 'done':
        qs = base_qs.filter(state='done').order_by('-done_date')[:30]
    else:
        qs = base_qs.filter(state='planned').order_by('date_deadline', '-created_at')

    activities_data = []
    for act in qs:
        diff = (act.date_deadline - today).days
        if act.state == 'done':
            due_text = f"Completed {act.done_date.strftime('%b %d') if act.done_date else ''}"
            due_badge_class = "op-act-badge-done"
        elif diff < 0:
            due_text = f"Overdue by {abs(diff)}d"
            due_badge_class = "op-act-badge-overdue"
        elif diff == 0:
            due_text = "Due Today"
            due_badge_class = "op-act-badge-today"
        elif diff == 1:
            due_text = "Due Tomorrow"
            due_badge_class = "op-act-badge-planned"
        else:
            due_text = f"Due in {diff}d"
            due_badge_class = "op-act-badge-planned"

        activities_data.append({
            'id': act.id,
            'type_id': act.activity_type.id,
            'type_name': act.activity_type.name,
            'type_icon': act.activity_type.icon,
            'summary': act.summary,
            'note': act.note or '',
            'date_deadline': act.date_deadline.strftime('%Y-%m-%d'),
            'date_deadline_display': act.date_deadline.strftime('%b %d, %Y'),
            'due_text': due_text,
            'due_badge_class': due_badge_class,
            'status_label': act.status_label,
            'is_overdue': act.is_overdue,
            'is_today': act.is_today,
            'is_future': act.is_future,
            'state': act.state,
            'assigned_to': act.user.username,
            'assigned_to_id': act.user_id,
            'created_by': act.created_by.username if act.created_by else 'System',
            'res_model': act.res_model,
            'res_id': act.res_id,
            'res_name': act.res_name or f"{act.res_model}:{act.res_id}" if act.res_id else 'General Action',
            'record_url': act.record_url,
            'feedback': act.feedback or '',
            'created_at': act.created_at.strftime('%b %d, %I:%M %p'),
        })

    return JsonResponse({
        'status': 'success',
        'overdue_count': overdue_count,
        'today_count': today_count,
        'planned_count': future_count,
        'total_pending': total_pending,
        'activities': activities_data,
    })


def mail_activity_types(request):
    """Returns list of active activity types for selectors."""
    ensure_default_activity_types()
    types = MailActivityType.objects.filter(is_active=True).order_by('sequence', 'name')
    data = [{'id': t.id, 'name': t.name, 'icon': t.icon, 'default_next_days': t.default_next_days} for t in types]
    return JsonResponse({'status': 'success', 'activity_types': data})


@require_POST
def mail_activity_create(request):
    """Creates a new scheduled activity."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    type_id = request.POST.get('activity_type_id')
    summary = request.POST.get('summary', '').strip()
    date_deadline_str = request.POST.get('date_deadline', '').strip()
    assigned_user_id = request.POST.get('user_id') or user.id
    note = request.POST.get('note', '').strip()
    res_model = request.POST.get('res_model', 'general').strip() or 'general'
    res_id = int(request.POST.get('res_id', 0) or 0)
    res_name = request.POST.get('res_name', '').strip()

    if not type_id or not summary or not date_deadline_str:
        return JsonResponse({'status': 'error', 'message': 'Activity type, summary, and due date are required.'}, status=400)

    try:
        from datetime import datetime
        date_deadline = datetime.strptime(date_deadline_str, '%Y-%m-%d').date()
        act_type = MailActivityType.objects.get(id=type_id)
        assigned_user = ResUsers.objects.get(id=assigned_user_id)

        if not res_name and res_model and res_id:
            if res_model == 'res.company':
                c = ResCompany.objects.filter(id=res_id).first()
                if c: res_name = c.name
            elif res_model == 'res.users':
                u = ResUsers.objects.filter(id=res_id).first()
                if u: res_name = u.username

        activity = MailActivity.objects.create(
            activity_type=act_type,
            summary=summary,
            note=note,
            date_deadline=date_deadline,
            user=assigned_user,
            created_by=user,
            res_model=res_model,
            res_id=res_id,
            res_name=res_name,
            state='planned'
        )

        if res_model and res_model != 'general' and res_id:
            MailMessage.objects.create(
                model_name=res_model,
                record_id=res_id,
                author=user,
                message_type='note',
                body=f"⏰ Scheduled Activity: [{act_type.icon} {act_type.name}] {summary} (Due: {date_deadline.strftime('%b %d, %Y')}, Assigned: {assigned_user.username})"
            )

        return JsonResponse({
            'status': 'success',
            'message': 'Activity scheduled successfully.',
            'activity_id': activity.id,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_POST
def mail_activity_done(request, activity_id):
    """Marks an activity as completed with optional feedback note."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    try:
        activity = MailActivity.objects.get(id=activity_id)
        feedback = request.POST.get('feedback', '').strip()
        activity.state = 'done'
        activity.feedback = feedback
        activity.done_date = timezone.now()
        activity.save(update_fields=['state', 'feedback', 'done_date', 'updated_at'])

        if activity.res_model and activity.res_model != 'general' and activity.res_id:
            log_body = f"✅ Completed Activity: [{activity.activity_type.icon} {activity.activity_type.name}] {activity.summary}"
            if feedback:
                log_body += f"\nFeedback: {feedback}"
            MailMessage.objects.create(
                model_name=activity.res_model,
                record_id=activity.res_id,
                author=user,
                message_type='note',
                body=log_body
            )

        return JsonResponse({
            'status': 'success',
            'message': 'Activity marked as done.',
            'activity_id': activity.id,
        })
    except MailActivity.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Activity not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@require_POST
def mail_activity_cancel(request, activity_id):
    """Cancels a scheduled activity."""
    user = get_current_ir_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    try:
        activity = MailActivity.objects.get(id=activity_id)
        if activity.state == 'cancelled':
            return JsonResponse({'status': 'success', 'message': 'Activity is already cancelled.'})

        activity.state = 'cancelled'
        activity.save(update_fields=['state', 'updated_at'])

        if activity.res_model and activity.res_model != 'general' and activity.res_id:
            MailMessage.objects.create(
                model_name=activity.res_model,
                record_id=activity.res_id,
                author=user,
                message_type='note',
                body=f"❌ Cancelled Activity: [{activity.activity_type.icon} {activity.activity_type.name}] {activity.summary}"
            )

        return JsonResponse({'status': 'success', 'message': 'Activity cancelled.'})
    except MailActivity.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Activity not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ---------------------------------------------------------------------------
# Default Paper Formats & Reports Seeder
# ---------------------------------------------------------------------------

DEFAULT_PAPERFORMATS_DATA = [
    {'name': 'A4', 'format_size': 'A4', 'orientation': 'Portrait', 'margin_top': 52.00, 'margin_bottom': 32.00, 'margin_left': 0.00, 'margin_right': 0.00, 'header_spacing': 52, 'dpi': 90, 'is_default': True},
    {'name': 'US Letter', 'format_size': 'Letter', 'orientation': 'Portrait', 'margin_top': 40.00, 'margin_bottom': 20.00, 'margin_left': 7.00, 'margin_right': 7.00, 'header_spacing': 35, 'dpi': 90},
    {'name': 'US Batch Deposit', 'format_size': 'Letter', 'orientation': 'Portrait', 'margin_top': 20.00, 'margin_bottom': 20.00, 'margin_left': 10.00, 'margin_right': 10.00, 'header_spacing': 15, 'dpi': 90},
    {'name': 'A4 Label Sheet', 'format_size': 'A4', 'orientation': 'Portrait', 'margin_top': 10.00, 'margin_bottom': 10.00, 'margin_left': 10.00, 'margin_right': 10.00, 'header_spacing': 10, 'dpi': 90},
    {'name': 'Dymo Label Sheet', 'format_size': 'custom', 'page_height': 89, 'page_width': 36, 'orientation': 'Landscape', 'margin_top': 3.00, 'margin_bottom': 3.00, 'margin_left': 3.00, 'margin_right': 3.00, 'header_spacing': 0, 'dpi': 90},
    {'name': 'A4 - statement', 'format_size': 'A4', 'orientation': 'Portrait', 'margin_top': 45.00, 'margin_bottom': 30.00, 'margin_left': 5.00, 'margin_right': 5.00, 'header_spacing': 40, 'dpi': 90},
    {'name': 'Badge(s)', 'format_size': 'custom', 'page_height': 85, 'page_width': 54, 'orientation': 'Portrait', 'margin_top': 5.00, 'margin_bottom': 5.00, 'margin_left': 5.00, 'margin_right': 5.00, 'header_spacing': 0, 'dpi': 90},
    {'name': 'Resume', 'format_size': 'A4', 'orientation': 'Portrait', 'margin_top': 20.00, 'margin_bottom': 20.00, 'margin_left': 15.00, 'margin_right': 15.00, 'header_spacing': 15, 'dpi': 90},
    {'name': 'Time Off Summary', 'format_size': 'A4', 'orientation': 'Landscape', 'margin_top': 25.00, 'margin_bottom': 20.00, 'margin_left': 10.00, 'margin_right': 10.00, 'header_spacing': 20, 'dpi': 90},
    {'name': 'Survey Certification', 'format_size': 'A4', 'orientation': 'Landscape', 'margin_top': 15.00, 'margin_bottom': 15.00, 'margin_left': 15.00, 'margin_right': 15.00, 'header_spacing': 15, 'dpi': 90},
    {'name': 'Performance Report A4', 'format_size': 'A4', 'orientation': 'Portrait', 'margin_top': 35.00, 'margin_bottom': 25.00, 'margin_left': 10.00, 'margin_right': 10.00, 'header_spacing': 30, 'dpi': 90},
    {'name': 'Employee Leave Report', 'format_size': 'A4', 'orientation': 'Portrait', 'margin_top': 30.00, 'margin_bottom': 20.00, 'margin_left': 10.00, 'margin_right': 10.00, 'header_spacing': 25, 'dpi': 90},
    {'name': 'Payroll Leave Summary', 'format_size': 'A4', 'orientation': 'Landscape', 'margin_top': 25.00, 'margin_bottom': 20.00, 'margin_left': 10.00, 'margin_right': 10.00, 'header_spacing': 20, 'dpi': 90},
]

DEFAULT_REPORTS_DATA = [
    {'name': 'Invoices', 'model_name': 'res.company', 'report_type': 'qweb-pdf', 'paperformat_name': 'A4', 'report_name': 'account.report_invoice_with_payments', 'report_file': 'account.report_invoice_with_payments', 'print_report_name': "object.name and ('Invoice - ' + object.name) or 'Invoice'"},
    {'name': 'Badge(s)', 'model_name': 'hr.employee', 'report_type': 'qweb-pdf', 'paperformat_name': 'Badge(s)', 'report_name': 'hr.print_badge', 'report_file': 'hr.print_badge', 'print_report_name': "'Print Badge - ' + (object.name or '')"},
    {'name': 'Time Off Summary', 'model_name': 'hr.employee', 'report_type': 'qweb-pdf', 'paperformat_name': 'Time Off Summary', 'report_name': 'hr_holidays.report_holidaysummary', 'report_file': 'hr_holidays.report_holidaysummary', 'print_report_name': "'Time Off Summary'"},
    {'name': 'Survey Certification', 'model_name': 'res.users', 'report_type': 'qweb-pdf', 'paperformat_name': 'Survey Certification', 'report_name': 'survey.certification_report', 'report_file': 'survey.certification_report', 'print_report_name': "'Certification'"},
    {'name': 'Employee Leave Report', 'model_name': 'hr.employee', 'report_type': 'qweb-pdf', 'paperformat_name': 'Employee Leave Report', 'report_name': 'hr_holidays.report_leave', 'report_file': 'hr_holidays.report_leave', 'print_report_name': "'Leave Report'"},
]


def ensure_default_paperformats():
    """Ensure standard paper formats and default report actions are populated."""
    IrModel.objects.get_or_create(
        model_name='report.paperformat',
        defaults={'name': 'Paper Format', 'description': 'Paper Format General Configuration', 'is_active': True}
    )
    IrModel.objects.get_or_create(
        model_name='ir.actions.report',
        defaults={'name': 'Report Actions', 'description': 'Report Actions', 'is_active': True}
    )

    for item in DEFAULT_PAPERFORMATS_DATA:
        ReportPaperformat.objects.get_or_create(
            name=item['name'],
            defaults=item
        )

    for rep in DEFAULT_REPORTS_DATA:
        if not IrActionsReport.objects.filter(name=rep['name']).exists():
            model_obj = IrModel.objects.filter(model_name=rep['model_name']).first()
            p_format = ReportPaperformat.objects.filter(name=rep['paperformat_name']).first()
            IrActionsReport.objects.create(
                name=rep['name'],
                model=model_obj,
                report_type=rep['report_type'],
                paperformat=p_format,
                report_name=rep['report_name'],
                report_file=rep.get('report_file', ''),
                print_report_name=rep.get('print_report_name', ''),
                is_active=True
            )


# ---------------------------------------------------------------------------
# Technical > Paper Formats
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_paperformats(request):
    """List view for Paper Formats."""
    ensure_default_paperformats()
    self_ir_model = IrModel.objects.filter(model_name='report.paperformat').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model) if self_ir_model else ([], [])

    query = request.GET.get('q', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 80

    qs = ReportPaperformat.objects.filter(is_active=True).order_by('name')
    if query:
        qs = qs.filter(Q(name__icontains=query) | Q(format_size__icontains=query))

    total_count = len(qs) if isinstance(qs, list) else qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/technical_paperformats.html', {
        'paperformats': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
    })


@admin_required_ir
def technical_paperformat_create(request):
    """Create view for Paper Format."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        format_size = request.POST.get('format_size', 'A4')
        try:
            page_height = int(request.POST.get('page_height', 0) or 0)
        except ValueError:
            page_height = 0
        try:
            page_width = int(request.POST.get('page_width', 0) or 0)
        except ValueError:
            page_width = 0
        orientation = request.POST.get('orientation', 'Portrait')
        try:
            margin_top = float(request.POST.get('margin_top', 52.00) or 52.00)
        except ValueError:
            margin_top = 52.00
        try:
            margin_bottom = float(request.POST.get('margin_bottom', 32.00) or 32.00)
        except ValueError:
            margin_bottom = 32.00
        try:
            margin_left = float(request.POST.get('margin_left', 0.00) or 0.00)
        except ValueError:
            margin_left = 0.00
        try:
            margin_right = float(request.POST.get('margin_right', 0.00) or 0.00)
        except ValueError:
            margin_right = 0.00
        header_line = request.POST.get('header_line') in ('on', 'true', '1')
        try:
            header_spacing = int(request.POST.get('header_spacing', 52) or 52)
        except ValueError:
            header_spacing = 52
        disable_shrinking = request.POST.get('disable_shrinking') in ('on', 'true', '1')
        try:
            dpi = int(request.POST.get('dpi', 90) or 90)
        except ValueError:
            dpi = 90
        is_default = request.POST.get('is_default') in ('on', 'true', '1')

        if not name:
            messages.error(request, "Name is required.")
            return render(request, 'base/technical_paperformat_create.html', {
                'format_size_choices': ReportPaperformat._meta.get_field('format_size').choices,
                'orientation_choices': ReportPaperformat._meta.get_field('orientation').choices,
                'missing_fields': ['name'],
            })

        format_obj = ReportPaperformat.objects.create(
            name=name,
            format_size=format_size,
            page_height=page_height,
            page_width=page_width,
            orientation=orientation,
            margin_top=margin_top,
            margin_bottom=margin_bottom,
            margin_left=margin_left,
            margin_right=margin_right,
            header_line=header_line,
            header_spacing=header_spacing,
            disable_shrinking=disable_shrinking,
            dpi=dpi,
            is_default=is_default,
            is_active=True,
        )
        messages.success(request, f'Paper Format "{format_obj.name}" created successfully.')
        return redirect('technical_paperformat_detail', format_id=format_obj.id)

    return render(request, 'base/technical_paperformat_create.html', {
        'format_size_choices': ReportPaperformat._meta.get_field('format_size').choices,
        'orientation_choices': ReportPaperformat._meta.get_field('orientation').choices,
    })


@admin_required_ir
def technical_paperformat_detail(request, format_id):
    """Detail / Form view for Paper Format."""
    format_obj = get_object_or_404(ReportPaperformat, id=format_id)

    if request.method == 'POST':
        format_obj.name = request.POST.get('name', format_obj.name).strip()
        format_obj.format_size = request.POST.get('format_size', format_obj.format_size)
        try:
            format_obj.page_height = int(request.POST.get('page_height', format_obj.page_height) or 0)
        except ValueError:
            pass
        try:
            format_obj.page_width = int(request.POST.get('page_width', format_obj.page_width) or 0)
        except ValueError:
            pass
        format_obj.orientation = request.POST.get('orientation', format_obj.orientation)
        try:
            format_obj.margin_top = float(request.POST.get('margin_top', format_obj.margin_top) or 0.0)
        except ValueError:
            pass
        try:
            format_obj.margin_bottom = float(request.POST.get('margin_bottom', format_obj.margin_bottom) or 0.0)
        except ValueError:
            pass
        try:
            format_obj.margin_left = float(request.POST.get('margin_left', format_obj.margin_left) or 0.0)
        except ValueError:
            pass
        try:
            format_obj.margin_right = float(request.POST.get('margin_right', format_obj.margin_right) or 0.0)
        except ValueError:
            pass
        format_obj.header_line = request.POST.get('header_line') in ('on', 'true', '1')
        try:
            format_obj.header_spacing = int(request.POST.get('header_spacing', format_obj.header_spacing) or 0)
        except ValueError:
            pass
        format_obj.disable_shrinking = request.POST.get('disable_shrinking') in ('on', 'true', '1')
        try:
            format_obj.dpi = int(request.POST.get('dpi', format_obj.dpi) or 90)
        except ValueError:
            pass
        format_obj.is_default = request.POST.get('is_default') in ('on', 'true', '1')
        format_obj.save()
        messages.success(request, f'Paper Format "{format_obj.name}" updated successfully.')
        return redirect('technical_paperformat_detail', format_id=format_obj.id)

    # Pager calculation
    all_ids = list(ReportPaperformat.objects.filter(is_active=True).order_by('name').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(format_obj.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    associated_reports = format_obj.reports.filter(is_active=True).order_by('name')

    return render(request, 'base/technical_paperformat_detail.html', {
        'format_obj': format_obj,
        'associated_reports': associated_reports,
        'format_size_choices': ReportPaperformat._meta.get_field('format_size').choices,
        'orientation_choices': ReportPaperformat._meta.get_field('orientation').choices,
        'current_index': current_index,
        'total_count': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Technical > Reports
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_reports(request):
    """List view for Report Actions."""
    ensure_default_paperformats()
    self_ir_model = IrModel.objects.filter(model_name='ir.actions.report').first()
    filterable_fields, groupable_fields = get_search_metadata(self_ir_model) if self_ir_model else ([], [])

    query = request.GET.get('q', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 80

    qs = IrActionsReport.objects.filter(is_active=True).select_related('model', 'paperformat').order_by('name')
    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(model__model_name__icontains=query) |
            Q(model__description__icontains=query) |
            Q(report_name__icontains=query) |
            Q(report_file__icontains=query)
        )

    total_count = len(qs) if isinstance(qs, list) else qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/technical_reports.html', {
        'reports': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
    })


@admin_required_ir
def technical_report_create(request):
    """Create view for Report Action with validation banner."""
    all_models = IrModel.objects.filter(is_active=True).order_by('description', 'model_name')
    all_paperformats = ReportPaperformat.objects.filter(is_active=True).order_by('name')
    all_groups = ResGroups.objects.filter(is_active=True).order_by('privilege', 'name')
    report_type_choices = IrActionsReport.REPORT_TYPE_CHOICES

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        model_id = request.POST.get('model')
        report_type = request.POST.get('report_type', 'qweb-pdf')
        paperformat_id = request.POST.get('paperformat')
        report_name = request.POST.get('report_name', '').strip()
        report_file = request.POST.get('report_file', '').strip()
        filter_domain = request.POST.get('filter_domain', '').strip()
        print_report_name = request.POST.get('print_report_name', '').strip()
        attachment_use = request.POST.get('attachment_use') in ('on', 'true', '1')
        attachment_prefix = request.POST.get('attachment_prefix', '').strip()

        missing_fields = []
        if not name:
            missing_fields.append('name')
        if not model_id:
            missing_fields.append('model')
        if not report_name:
            missing_fields.append('report_name')

        if missing_fields:
            messages.error(request, "Missing required fields")
            return render(request, 'base/technical_report_create.html', {
                'all_models': all_models,
                'all_paperformats': all_paperformats,
                'all_groups': all_groups,
                'report_type_choices': report_type_choices,
                'missing_fields': missing_fields,
                'form_data': request.POST,
            })

        rep_obj = IrActionsReport.objects.create(
            name=name,
            model_id=int(model_id),
            report_type=report_type,
            paperformat_id=int(paperformat_id) if paperformat_id else None,
            report_name=report_name,
            report_file=report_file or report_name,
            filter_domain=filter_domain,
            print_report_name=print_report_name,
            attachment_use=attachment_use,
            attachment_prefix=attachment_prefix,
            is_active=True,
        )

        group_ids = request.POST.getlist('groups')
        if group_ids:
            valid_gids = [int(gid) for gid in group_ids if gid.isdigit()]
            rep_obj.groups.set(valid_gids)

        messages.success(request, f'Report "{rep_obj.name}" created successfully.')
        return redirect('technical_report_detail', report_id=rep_obj.id)

    return render(request, 'base/technical_report_create.html', {
        'all_models': all_models,
        'all_paperformats': all_paperformats,
        'all_groups': all_groups,
        'report_type_choices': report_type_choices,
        'missing_fields': [],
    })


@admin_required_ir
def technical_report_detail(request, report_id):
    """Detail / Form view for Report Action."""
    report_obj = get_object_or_404(
        IrActionsReport.objects.select_related('model', 'paperformat').prefetch_related('groups'),
        id=report_id
    )
    all_models = IrModel.objects.filter(is_active=True).order_by('description', 'model_name')
    all_paperformats = ReportPaperformat.objects.filter(is_active=True).order_by('name')
    all_groups = ResGroups.objects.filter(is_active=True).order_by('privilege', 'name')
    report_type_choices = IrActionsReport.REPORT_TYPE_CHOICES

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        model_id = request.POST.get('model')
        report_name = request.POST.get('report_name', '').strip()

        missing_fields = []
        if not name:
            missing_fields.append('name')
        if not model_id:
            missing_fields.append('model')
        if not report_name:
            missing_fields.append('report_name')

        if missing_fields:
            messages.error(request, "Missing required fields")
        else:
            report_obj.name = name
            report_obj.model_id = int(model_id) if model_id else None
            report_obj.report_type = request.POST.get('report_type', report_obj.report_type)
            p_id = request.POST.get('paperformat')
            report_obj.paperformat_id = int(p_id) if p_id else None
            report_obj.report_name = report_name
            report_obj.report_file = request.POST.get('report_file', '').strip() or report_name
            report_obj.filter_domain = request.POST.get('filter_domain', '').strip()
            report_obj.print_report_name = request.POST.get('print_report_name', '').strip()
            report_obj.attachment_use = request.POST.get('attachment_use') in ('on', 'true', '1')
            report_obj.attachment_prefix = request.POST.get('attachment_prefix', '').strip()
            report_obj.save()

            group_ids = request.POST.getlist('groups')
            valid_gids = [int(gid) for gid in group_ids if gid.isdigit()]
            report_obj.groups.set(valid_gids)

            messages.success(request, f'Report "{report_obj.name}" updated successfully.')
            return redirect('technical_report_detail', report_id=report_obj.id)

    # Pager calculation
    all_ids = list(IrActionsReport.objects.filter(is_active=True).order_by('name').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(report_obj.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    return render(request, 'base/technical_report_detail.html', {
        'report_obj': report_obj,
        'all_models': all_models,
        'all_paperformats': all_paperformats,
        'all_groups': all_groups,
        'report_groups': report_obj.groups.all(),
        'report_type_choices': report_type_choices,
        'current_index': current_index,
        'total_count': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
        'missing_fields': [],
    })


# ---------------------------------------------------------------------------
# Technical > Outgoing Mail Servers (ir.mail_server)
# ---------------------------------------------------------------------------

DEFAULT_MAIL_SERVERS_DATA = [
    {
        'name': 'Primary SMTP Server',
        'sequence': 10,
        'smtp_host': 'localhost',
        'smtp_port': 587,
        'smtp_encryption': 'starttls',
        'smtp_user': '',
        'smtp_pass': '',
        'smtp_debug': False,
        'is_active': True,
    }
]


def ensure_default_outgoing_mail_servers():
    """Seeds default mail server if none exist."""
    if not IrMailServer.objects.exists():
        for item in DEFAULT_MAIL_SERVERS_DATA:
            IrMailServer.objects.get_or_create(name=item['name'], defaults=item)


@admin_required_ir
def technical_outgoing_mail(request):
    """List view for Outgoing Mail Servers."""
    ensure_default_outgoing_mail_servers()
    query = request.GET.get('q', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 80

    qs = IrMailServer.objects.filter(is_active=True).order_by('sequence', 'name')
    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(smtp_host__icontains=query) |
            Q(smtp_user__icontains=query)
        )

    total_count = len(qs) if isinstance(qs, list) else qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/technical_outgoing_mail.html', {
        'servers': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
    })


@admin_required_ir
def technical_outgoing_mail_create(request):
    """Create a new Outgoing Mail Server."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        smtp_host = request.POST.get('smtp_host', '').strip()
        smtp_port = int(request.POST.get('smtp_port', 587) or 587)
        smtp_encryption = request.POST.get('smtp_encryption', 'starttls')
        smtp_user = request.POST.get('smtp_user', '').strip()
        smtp_pass = request.POST.get('smtp_pass', '').strip()
        sequence = int(request.POST.get('sequence', 10) or 10)
        smtp_debug = request.POST.get('smtp_debug') in ('on', 'true', '1')

        if not name or not smtp_host:
            messages.error(request, 'Description Name and SMTP Server Host are required.')
            return render(request, 'base/technical_outgoing_mail_create.html', {
                'encryption_choices': IrMailServer.ENCRYPTION_CHOICES,
            })

        server = IrMailServer.objects.create(
            name=name,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_encryption=smtp_encryption,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            sequence=sequence,
            smtp_debug=smtp_debug,
            is_active=True,
        )
        messages.success(request, f'Outgoing Mail Server "{server.name}" created successfully.')
        return redirect('technical_outgoing_mail_detail', server_id=server.id)

    return render(request, 'base/technical_outgoing_mail_create.html', {
        'encryption_choices': IrMailServer.ENCRYPTION_CHOICES,
    })


@admin_required_ir
def technical_outgoing_mail_detail(request, server_id):
    """Detail / Edit view for an Outgoing Mail Server."""
    server = get_object_or_404(IrMailServer, id=server_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            server.is_active = False
            server.save(update_fields=['is_active'])
            messages.success(request, f'Server "{server.name}" has been removed.')
            return redirect('technical_outgoing_mail')
        elif action == 'duplicate':
            dup = IrMailServer.objects.create(
                name=f"{server.name} (Copy)",
                smtp_host=server.smtp_host,
                smtp_port=server.smtp_port,
                smtp_encryption=server.smtp_encryption,
                smtp_user=server.smtp_user,
                smtp_pass=server.smtp_pass,
                sequence=server.sequence + 1,
                smtp_debug=server.smtp_debug,
                is_active=True,
            )
            messages.success(request, f'Duplicated server "{dup.name}".')
            return redirect('technical_outgoing_mail_detail', server_id=dup.id)
        else:
            name = request.POST.get('name', '').strip()
            smtp_host = request.POST.get('smtp_host', '').strip()
            smtp_port = int(request.POST.get('smtp_port', 587) or 587)
            smtp_encryption = request.POST.get('smtp_encryption', 'starttls')
            smtp_user = request.POST.get('smtp_user', '').strip()
            smtp_pass = request.POST.get('smtp_pass', '').strip()
            sequence = int(request.POST.get('sequence', 10) or 10)
            smtp_debug = request.POST.get('smtp_debug') in ('on', 'true', '1')

            if not name or not smtp_host:
                messages.error(request, 'Description Name and SMTP Server Host are required.')
            else:
                server.name = name
                server.smtp_host = smtp_host
                server.smtp_port = smtp_port
                server.smtp_encryption = smtp_encryption
                server.smtp_user = smtp_user
                if smtp_pass:
                    server.smtp_pass = smtp_pass
                server.sequence = sequence
                server.smtp_debug = smtp_debug
                server.save()
                messages.success(request, f'Server "{server.name}" saved successfully.')
                return redirect('technical_outgoing_mail_detail', server_id=server.id)

    all_ids = list(IrMailServer.objects.filter(is_active=True).order_by('sequence', 'name').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(server.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    return render(request, 'base/technical_outgoing_mail_detail.html', {
        'server': server,
        'encryption_choices': IrMailServer.ENCRYPTION_CHOICES,
        'current_index': current_index,
        'total_count': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
    })


@admin_required_ir
@require_POST
def technical_outgoing_mail_test_connection(request, server_id):
    """AJAX diagnostic connection test for saved mail server."""
    server = get_object_or_404(IrMailServer, id=server_id)
    result = server.test_connection()
    return JsonResponse(result)


@admin_required_ir
@require_POST
def technical_outgoing_mail_test_live(request):
    """AJAX diagnostic connection test for unsaved form values."""
    smtp_host = request.POST.get('smtp_host', '').strip()
    smtp_port = int(request.POST.get('smtp_port', 587) or 587)
    smtp_encryption = request.POST.get('smtp_encryption', 'starttls')
    smtp_user = request.POST.get('smtp_user', '').strip()
    smtp_pass = request.POST.get('smtp_pass', '').strip()

    temp_server = IrMailServer(
        name='Temp Diagnostic',
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_encryption=smtp_encryption,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass
    )
    result = temp_server.test_connection()
    return JsonResponse(result)


# ---------------------------------------------------------------------------
# Technical > System Parameters (ir.config_parameter)
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PARAMETERS_DATA = [
    {'key': 'web.base.url', 'value': 'http://localhost:8000', 'description': 'The base URL used to generate external links to this ERP instance.', 'is_system': True},
    {'key': 'mail.catchall.domain', 'value': 'officepro.erp', 'description': 'Catchall email domain for inbound communication routing.', 'is_system': True},
    {'key': 'mail.default.from', 'value': 'noreply@officepro.erp', 'description': 'Default sender address for automated platform notification emails.', 'is_system': True},
    {'key': 'session.timeout_minutes', 'value': '1440', 'description': 'Maximum duration of user session inactivity before auto logout.', 'is_system': False},
    {'key': 'auth.otp.expiry_seconds', 'value': '600', 'description': 'Validity duration in seconds for one-time verification password codes.', 'is_system': False},
    {'key': 'company.default_currency', 'value': 'INR', 'description': 'Default currency code used across multi-company operations.', 'is_system': False},
    {'key': 'system.platform.version', 'value': '2026.1', 'description': 'Office Pro ERP Core Platform Engine Version.', 'is_system': True},
]


def ensure_default_config_parameters():
    """Seeds default system parameters if none exist."""
    if not IrConfigParameter.objects.exists():
        for item in DEFAULT_CONFIG_PARAMETERS_DATA:
            IrConfigParameter.objects.get_or_create(key=item['key'], defaults=item)


@admin_required_ir
def technical_parameters(request):
    """List view for System Configuration Parameters."""
    ensure_default_config_parameters()
    query = request.GET.get('q', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 80

    qs = IrConfigParameter.objects.filter(is_active=True).order_by('key')
    if query:
        qs = qs.filter(
            Q(key__icontains=query) |
            Q(value__icontains=query) |
            Q(description__icontains=query)
        )

    total_count = len(qs) if isinstance(qs, list) else qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/technical_parameters.html', {
        'parameters': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
    })


@admin_required_ir
def technical_parameter_create(request):
    """Create a new System Parameter."""
    if request.method == 'POST':
        key = request.POST.get('key', '').strip()
        value = request.POST.get('value', '').strip()
        description = request.POST.get('description', '').strip()

        if not key or not value:
            messages.error(request, 'Key and Value are required.')
            return render(request, 'base/technical_parameter_create.html')

        if IrConfigParameter.objects.filter(key=key, is_active=True).exists():
            messages.error(request, f'Parameter with key "{key}" already exists.')
            return render(request, 'base/technical_parameter_create.html')

        param = IrConfigParameter.objects.create(
            key=key,
            value=value,
            description=description,
            is_system=False,
            is_active=True,
        )
        messages.success(request, f'Parameter "{param.key}" created successfully.')
        return redirect('technical_parameter_detail', param_id=param.id)

    return render(request, 'base/technical_parameter_create.html')


@admin_required_ir
def technical_parameter_detail(request, param_id):
    """Detail / Edit view for a System Parameter."""
    param = get_object_or_404(IrConfigParameter, id=param_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            if param.is_system:
                messages.error(request, 'System parameters are protected and cannot be deleted.')
            else:
                param.is_active = False
                param.save(update_fields=['is_active'])
                messages.success(request, f'Parameter "{param.key}" deleted.')
                return redirect('technical_parameters')
        else:
            key = request.POST.get('key', '').strip()
            value = request.POST.get('value', '').strip()
            description = request.POST.get('description', '').strip()

            if not key or not value:
                messages.error(request, 'Key and Value are required.')
            else:
                param.key = key
                param.value = value
                param.description = description
                param.save()
                messages.success(request, f'Parameter "{param.key}" saved successfully.')
                return redirect('technical_parameter_detail', param_id=param.id)

    all_ids = list(IrConfigParameter.objects.filter(is_active=True).order_by('key').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(param.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    return render(request, 'base/technical_parameter_detail.html', {
        'param_obj': param,
        'current_index': current_index,
        'total_count': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
    })


# ---------------------------------------------------------------------------
# Technical > Logging & Diagnostics (ir.logging)
# ---------------------------------------------------------------------------

@admin_required_ir
def technical_logging(request):
    """List view for System Error & Diagnostic Logs."""
    query = request.GET.get('q', '').strip()
    level_filter = request.GET.get('level', '').strip()
    type_filter = request.GET.get('type', '').strip()
    page_num = max(1, int(request.GET.get('page', 1) or 1))
    page_size = 50

    qs = IrLogging.objects.filter(is_active=True).select_related('user')
    if level_filter:
        qs = qs.filter(level=level_filter)
    if type_filter:
        qs = qs.filter(type=type_filter)
    if query:
        qs = qs.filter(
            Q(message__icontains=query) |
            Q(path__icontains=query) |
            Q(func_name__icontains=query) |
            Q(name__icontains=query) |
            Q(traceback__icontains=query)
        )
    qs = qs.order_by('-created_at', '-id')

    total_count = len(qs) if isinstance(qs, list) else qs.count()
    start = (page_num - 1) * page_size
    end = start + page_size
    page_items = qs[start:end]
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    return render(request, 'base/technical_logging.html', {
        'logs': page_items,
        'total_count': total_count,
        'page': page_num,
        'page_size': page_size,
        'total_pages': total_pages,
        'page_start': start + 1 if total_count > 0 else 0,
        'page_end': min(end, total_count),
        'query': query,
        'level_filter': level_filter,
        'type_filter': type_filter,
        'level_choices': IrLogging.LEVEL_CHOICES,
        'type_choices': IrLogging.TYPE_CHOICES,
    })


@admin_required_ir
def technical_log_detail(request, log_id):
    """Detail inspection view for an individual IrLogging record."""
    log_obj = get_object_or_404(IrLogging, id=log_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            log_obj.delete()
            messages.success(request, f'Log record #{log_id} deleted.')
            return redirect('technical_logging')

    all_ids = list(IrLogging.objects.filter(is_active=True).order_by('-created_at', '-id').values_list('id', flat=True))
    total_count = len(all_ids)
    try:
        current_index = all_ids.index(log_obj.id) + 1
    except ValueError:
        current_index = 1

    prev_id = all_ids[current_index - 2] if current_index > 1 else None
    next_id = all_ids[current_index] if current_index < total_count else None

    return render(request, 'base/technical_log_detail.html', {
        'log_obj': log_obj,
        'current_index': current_index,
        'total_count': total_count,
        'prev_id': prev_id,
        'next_id': next_id,
    })


@admin_required_ir
@require_POST
def technical_logging_clear(request):
    """Purges all system logs."""
    count, _ = IrLogging.objects.all().delete()
    messages.success(request, f'Successfully cleared {count} system log record(s).')
    return redirect('technical_logging')


# ---------------------------------------------------------------------------
# Global Custom HTTP Error Handlers
# ---------------------------------------------------------------------------

def error_500_view(request):
    """Custom HTTP 500 Server Error view."""
    import sys
    exc_type, exc_obj, exc_tb = sys.exc_info()
    diag = None
    if exc_obj:
        diag = extract_diagnostics_from_exception(exc_obj, request=request)

    is_debug = False
    if hasattr(request, 'session'):
        is_debug = bool(request.session.get('debug', False))
    if not is_debug:
        from django.conf import settings
        is_debug = getattr(settings, 'DEBUG', False)

    return render(request, 'base/500.html', {
        'diag': diag,
        'is_debug': is_debug,
        'request_url': request.build_absolute_uri() if hasattr(request, 'build_absolute_uri') else request.path,
        'request_method': request.method,
    }, status=500)


def error_404_view(request, exception=None):
    """Custom HTTP 404 Not Found view."""
    return render(request, 'base/404.html', {
        'request_path': request.path,
        'exception': str(exception) if exception else None,
    }, status=404)


def error_403_view(request, exception=None):
    """Custom HTTP 403 Forbidden / Permission Denied view."""
    return render(request, 'base/403.html', {
        'request_path': request.path,
        'exception': str(exception) if exception else None,
    }, status=403)


def error_400_view(request, exception=None):
    """Custom HTTP 400 Bad Request view."""
    return render(request, 'base/400.html', {
        'request_path': request.path,
        'exception': str(exception) if exception else None,
    }, status=400)








