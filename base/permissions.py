"""
Central permission rules for the generic list-view "batch actions"
(export / import / duplicate / archive / unarchive / delete).

Before this module existed, ANY logged-in user could export, import, archive or duplicate
rows of ANY model (including res.users, res.groups, ir.mail_server ...) simply by calling
/batch-action/ with a model name.  Rules now are:

* Administrators: everything, except that password / secret columns are never exported or imported.
* Sensitive models (users, groups, privileges, every ir.* technical model): administrators only.
* Module models: only the matching module officer (HR, Attendance, Time Off) or an administrator.
* Any other model: the user must hold the matching right in ir.model.access
  (read -> export, create -> import / duplicate, write -> archive / unarchive, delete -> delete).
"""
from base.auth_helpers import (
    is_admin_user,
    is_hr_officer_or_admin,
    is_attendance_officer_or_admin,
    is_leave_officer_or_admin,
)

# Model keys that only administrators may touch through batch actions.
ADMIN_ONLY_PREFIXES = (
    'res.users',      # also covers res.users.groups
    'res_users',
    'res.groups',
    'res.privilege',
    'ir.',
    'ir_',
    'report.',
)

EMPLOYEE_MODELS = {'hr.employee', 'employee'}
ATTENDANCE_MODELS = {'hr.attendance', 'attendance'}
LEAVE_MODELS = {
    'hr.leave', 'leave', 'hr.leave.allocation', 'leave.allocation',
    'hr.leave.type', 'leave.type', 'hr.leave.mandatory.day',
}

# action -> column of ir.model.access that must be granted
ACTION_TO_ACCESS_FLAG = {
    'export': 'can_read',
    'import': 'can_create',
    'duplicate': 'can_create',
    'archive': 'can_write',
    'unarchive': 'can_write',
    'delete': 'can_delete',
}

# Column names (or fragments) that must never leave the system / be written from a file.
_SENSITIVE_FRAGMENTS = ('password', 'passwd', 'smtp_pass', 'secret', 'token', 'api_key', 'apikey', 'private_key')


def is_sensitive_field(field_name):
    name = (field_name or '').lower()
    return any(fragment in name for fragment in _SENSITIVE_FRAGMENTS)


def is_admin_only_model(model_key):
    key = (model_key or '').lower()
    return any(key.startswith(prefix) for prefix in ADMIN_ONLY_PREFIXES)


def _ir_model_access_allows(user, model_key, action):
    """Fallback for models that have no dedicated officer role: consult ir.model.access."""
    flag = ACTION_TO_ACCESS_FLAG.get(action)
    if not flag:
        return False
    try:
        from base.models import IrModel, IrModelAccess, ResUsersGroups
        ir_model = IrModel.objects.filter(model_name=model_key).first()
        if not ir_model:
            return False
        group_ids = ResUsersGroups.objects.filter(user=user, is_active=True).values_list('group_id', flat=True)
        return IrModelAccess.objects.filter(
            model=ir_model, group_id__in=list(group_ids), is_active=True, **{flag: True}
        ).exists()
    except Exception:
        return False


def can_batch(user, model_key, action):
    """Return True if `user` may run batch `action` on `model_key`."""
    if not user or not getattr(user, 'is_active', False):
        return False
    if action not in ACTION_TO_ACCESS_FLAG:
        return False
    if is_admin_user(user):
        return True
    if is_admin_only_model(model_key):
        return False
    if model_key in EMPLOYEE_MODELS:
        return is_hr_officer_or_admin(user)
    if model_key in ATTENDANCE_MODELS:
        return is_attendance_officer_or_admin(user)
    if model_key in LEAVE_MODELS:
        return is_leave_officer_or_admin(user)
    if model_key.startswith('mail.'):
        return False
    return _ir_model_access_allows(user, model_key, action)


def spreadsheet_safe(value):
    """
    Neutralise CSV / Excel formula injection: a cell that starts with = + - @ (or a control
    character) would be executed as a formula when the export is opened in Excel.
    """
    text = '' if value is None else str(value)
    if text and text[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + text
    return text


MAX_IMPORT_BYTES = 5 * 1024 * 1024   # 5 MB
MAX_IMPORT_ROWS = 5000
