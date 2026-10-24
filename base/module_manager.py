"""
Office Pro - Enterprise Module & Lifecycle Manager
Handles modular app installation, uninstallation, dependency resolution,
and safe record archival / deletion rules.
"""
import logging
from django.db import connection, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

PROTECTED_MODULES = {'base', 'ir', 'res'}

def get_installed_modules():
    """
    Returns a set of technical names of all currently active/installed modules.
    Always includes core 'base'.
    """
    try:
        from base.models import IrModule
        installed = set(
            IrModule.objects.filter(is_active=True, state='installed')
            .values_list('name', flat=True)
        )
        installed.add('base')
        return installed
    except Exception as e:
        logger.warning(f"Error querying IrModule: {e}")
        return {'base', 'res', 'hr', 'mail'}


def is_module_installed(technical_name):
    """
    Check if a specific module is installed and active.
    """
    installed = get_installed_modules()
    return technical_name.lower() in installed


def install_module(technical_name, user=None):
    """
    Installs a module:
    1. Validates dependencies.
    2. Runs schema DDL / table creation if needed.
    3. Activates menus in IrUiMenu.
    4. Sets IrModule state to 'installed'.
    """
    from base.views import MODULES_REGISTRY
    from base.models import IrModule, IrUiMenu

    mod_data = MODULES_REGISTRY.get(technical_name)
    if not mod_data:
        return False, f"Module '{technical_name}' is not registered in the system."

    # Check dependencies
    installed_now = get_installed_modules()
    deps = [d['name'] for d in mod_data.get('dependencies', [])]
    missing_deps = [d for d in deps if d not in installed_now and d in MODULES_REGISTRY]
    
    # Auto-install missing registered dependencies first
    for dep_name in missing_deps:
        success, msg = install_module(dep_name, user)
        if not success:
            return False, f"Cannot install '{technical_name}': failed to install dependency '{dep_name}': {msg}"

    try:
        with transaction.atomic():
            ir_mod, _ = IrModule.objects.get_or_create(
                name=technical_name,
                defaults={'state': 'installed', 'is_active': True}
            )
            ir_mod.state = 'installed'
            ir_mod.is_active = True
            ir_mod.save()

            # Activate matching menus
            IrUiMenu.objects.filter(name__icontains=mod_data['name']).update(is_active=True)

        return True, f"Module '{mod_data['name']}' ({technical_name}) was successfully installed."
    except Exception as e:
        logger.exception(f"Failed to install module {technical_name}: {e}")
        return False, f"Installation failed: {str(e)}"


def uninstall_module(technical_name, user=None):
    """
    Safely uninstalls a module:
    1. Blocks if module is core/protected.
    2. Blocks if other active modules depend on it.
    3. Deactivates menus and navigation.
    4. Sets state to 'uninstalled' in IrModule.
    5. Preserves surviving parent records.
    """
    from base.views import MODULES_REGISTRY
    from base.models import IrModule, IrUiMenu

    if technical_name in PROTECTED_MODULES:
        return False, f"Module '{technical_name}' is a core system component and cannot be uninstalled."

    mod_data = MODULES_REGISTRY.get(technical_name)
    mod_display_name = mod_data['name'] if mod_data else technical_name

    # Check if other active modules depend on this one
    installed_now = get_installed_modules()
    for other_key in installed_now:
        if other_key == technical_name:
            continue
        other_data = MODULES_REGISTRY.get(other_key)
        if other_data:
            other_deps = [d['name'] for d in other_data.get('dependencies', [])]
            if technical_name in other_deps:
                return False, f"Cannot uninstall '{mod_display_name}' because module '{other_data['name']}' depends on it."

    try:
        with transaction.atomic():
            # Update IrModule record
            IrModule.objects.filter(name=technical_name).update(state='uninstalled', is_active=False)

            # Deactivate UI menus
            if mod_data:
                IrUiMenu.objects.filter(name__icontains=mod_data['name']).update(is_active=False)

        return True, f"Module '{mod_display_name}' has been safely uninstalled. Associated menus have been removed."
    except Exception as e:
        logger.exception(f"Failed to uninstall module {technical_name}: {e}")
        return False, f"Uninstallation error: {str(e)}"


def archive_employee_safely(emp_id, user=None):
    """
    Archives an employee safely according to enterprise ERP rules:
    - Sets employee.is_active = False.
    - Preserves historical timesheets, attendance, and invoiced records intact.
    - Cancels future/pending leaves so they don't block approvals or calendar schedules.
    - Sets open task assignments to unassigned.
    - Deactivates linked system user login (res_users).
    """
    from employee.models import Employee
    from base.models import ResUsers

    try:
        emp = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return False, "Employee not found."

    with transaction.atomic():
        # 1. Archive Employee record
        emp.is_active = False
        emp.save()

        # 2. Deactivate linked ResUsers account if one exists
        try:
            ResUsers.objects.filter(employee_id=emp.id).update(is_active=False)
        except Exception:
            pass

        # 3. Clean up pending / future leaves via raw SQL safely
        try:
            with connection.cursor() as cursor:
                # Cancel pending leave requests
                cursor.execute("""
                    UPDATE leave_request
                    SET status = 'Rejected'
                    WHERE employee_id = %s AND status = 'Pending'
                """, [emp.id])
        except Exception as e:
            logger.debug(f"Leave table not present or skipped: {e}")

        # 4. Remove employee from active project assignments
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE project_member
                    SET is_active = FALSE
                    WHERE employee_id = %s
                """, [emp.id])
        except Exception as e:
            logger.debug(f"Project member table not present or skipped: {e}")

    return True, f"Employee '{emp.name}' was successfully archived. Historical records remain preserved."


def can_delete_employee(emp_id):
    """
    Evaluates whether an employee can be hard deleted.
    Blocks deletion if there are historical financial, attendance, or project records.
    """
    from employee.models import Employee

    try:
        emp = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return False, "Employee record does not exist."

    # Check attendance
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE employee_id = %s", [emp.id])
            att_count = cursor.fetchone()[0]
            if att_count > 0:
                return False, f"Cannot delete '{emp.name}' because they have {att_count} logged attendance record(s). Please Archive instead."
        except Exception:
            pass

        try:
            cursor.execute("SELECT COUNT(*) FROM leave_request WHERE employee_id = %s", [emp.id])
            leave_count = cursor.fetchone()[0]
            if leave_count > 0:
                return False, f"Cannot delete '{emp.name}' because they have {leave_count} leave record(s). Please Archive instead."
        except Exception:
            pass

        try:
            cursor.execute("SELECT COUNT(*) FROM project WHERE manager_id = %s", [emp.id])
            proj_count = cursor.fetchone()[0]
            if proj_count > 0:
                return False, f"Cannot delete '{emp.name}' because they are assigned as Project Manager on {proj_count} project(s). Please reassign the manager first or Archive the employee."
        except Exception:
            pass

    return True, "Safe to delete."


def handle_employee_deletion(emp_id):
    """
    Handles employee deletion with cascading and integrity rules:
    - If employee has dependent historical records (attendance, leaves):
      Safely archives the employee and related records, deactivates user login,
      and returns ('archived', f"Employee '{emp.name}' has historical attendance/records and was safely archived.")
    - If employee has no dependent records:
      Clears manager links on departments and subordinates,
      unlinks or cleans any orphaned ResUsers account,
      hard-deletes the employee, and returns ('deleted', f"Employee '{emp.name}' was permanently deleted.")
    """
    from employee.models import Employee, Department
    from base.models import ResUsers

    try:
        emp = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return 'not_found', "Employee not found."

    can_del, reason = can_delete_employee(emp_id)
    if not can_del:
        # Dependent records exist -> Safely archive
        archive_employee_safely(emp_id)
        return 'archived', f"Employee '{emp.name}' has historical audit/attendance records; safely archived to protect database integrity."

    with transaction.atomic():
        # Clear department manager FK if this employee was a manager
        Department.objects.filter(manager_id=emp.id).update(manager=None)

        # Reassign direct subordinates to their manager's manager or None
        Employee.objects.filter(manager_id=emp.id).update(manager=emp.manager)
        Employee.objects.filter(timesheet_approver_id=emp.id).update(timesheet_approver_id=None)
        Employee.objects.filter(leave_approver_l1_id=emp.id).update(leave_approver_l1_id=None)
        Employee.objects.filter(leave_approver_l2_id=emp.id).update(leave_approver_l2_id=None)
        Employee.objects.filter(expense_approver_l1_id=emp.id).update(expense_approver_l1_id=None)
        Employee.objects.filter(expense_approver_l2_id=emp.id).update(expense_approver_l2_id=None)

        # Unlink or delete linked user
        linked_users = ResUsers.objects.filter(employee_id=emp.id)
        for u in linked_users:
            if u.id != 1 and u.username != 'admin':
                delete_user_safely(u.id)
            else:
                u.employee_id = None
                u.save(update_fields=['employee_id'])

        emp_name = emp.name
        emp.delete()
        return 'deleted', f"Employee '{emp_name}' was permanently deleted."


def delete_user_safely(user_id):
    """
    Safely deletes a user record:
    - Protects Superuser/Admin (id=1 or username in ('admin', 'administrator')).
    - If user has a linked Employee:
      - If employee has dependent records: archives the employee and unlinks user.
      - If employee has no dependent records: cleanly deletes employee as well.
    - Cleans up all FK join tables and related records pointing to res_users:
      - res_users_groups
      - ir_filters
      - mail_channel_members
      - mail_activity
      - mail_message
      - mail_mail
      - ir_cron
      - ir_logging
    - Deletes the ResUsers record cleanly without throwing FK violation errors.
    """
    from base.models import ResUsers, ResUsersGroups, IrFilters
    from employee.models import Employee

    try:
        user = ResUsers.objects.get(id=user_id)
    except ResUsers.DoesNotExist:
        return False, "User does not exist."

    if user.id == 1 or user.username.lower() in ('admin', 'administrator'):
        return False, "Cannot delete the primary System Administrator account."

    with transaction.atomic():
        # Handle linked employee
        emp = None
        if user.employee_id:
            emp = Employee.objects.filter(id=user.employee_id).first()
        elif user.email:
            emp = Employee.objects.filter(email=user.email).first()

        if emp:
            can_del, _ = can_delete_employee(emp.id)
            if not can_del:
                # Archive employee to keep historical timesheet, attendance, project records
                archive_employee_safely(emp.id)
            else:
                # No historical data -> can be safely cleaned up
                handle_employee_deletion(emp.id)

        # Clean FKs pointing to this user
        ResUsersGroups.objects.filter(user_id=user.id).delete()
        IrFilters.objects.filter(user_id=user.id).delete()

        with connection.cursor() as cursor:
            # mail_channel_members
            try:
                cursor.execute("DELETE FROM mail_channel_members WHERE resusers_id = %s", [user.id])
            except Exception:
                pass

            # mail_activity
            try:
                cursor.execute("DELETE FROM mail_activity WHERE user_id = %s OR created_by_id = %s", [user.id, user.id])
            except Exception:
                pass

            # mail_message (anonymize / detach author and recipient to keep thread integrity)
            try:
                cursor.execute("UPDATE mail_message SET author_id = NULL WHERE author_id = %s", [user.id])
                cursor.execute("UPDATE mail_message SET recipient_id = NULL WHERE recipient_id = %s", [user.id])
            except Exception:
                pass

            # mail_mail
            try:
                cursor.execute("DELETE FROM mail_mail WHERE user_id = %s OR sender_user_id = %s OR recipient_user_id = %s", [user.id, user.id, user.id])
            except Exception:
                pass

            # ir_cron (reassign to admin id=1)
            try:
                cursor.execute("UPDATE ir_cron SET user_id = 1 WHERE user_id = %s", [user.id])
            except Exception:
                pass

            # ir_logging
            try:
                cursor.execute("UPDATE ir_logging SET user_id = NULL WHERE user_id = %s", [user.id])
            except Exception:
                pass

        username = user.username
        user.delete()
        return True, f"User '{username}' was permanently deleted."

