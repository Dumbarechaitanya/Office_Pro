from django import template
from django.db.models import Model
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_attr(obj, attr_name):
    """
    Look up obj.attr_name dynamically where attr_name is a variable
    (e.g. from a loop over columns). Supports callable methods and booleans.
    """
    try:
        value = obj
        for part in str(attr_name).split('.'):
            if hasattr(value, part):
                value = getattr(value, part)
                if callable(value) and not isinstance(value, type):
                    value = value()
            else:
                return ''

        if str(attr_name).lower() == 'role' and isinstance(value, str):
            badge_cls = 'op-badge-role admin' if 'admin' in value.lower() else 'op-badge-role'
            return mark_safe(f'<span class="{badge_cls}">{value}</span>')

        # FK / model instances -> plain string
        if isinstance(value, Model):
            return str(value)
        if isinstance(value, bool):
            return '✓' if value else ''
        return value if value is not None else ''
    except Exception:
        return ''


@register.filter
def record_initial(row, col_name=None):
    """
    Safely extract a single initial letter for avatar badges from any object/model/dict.
    Tries standard attributes (name, username, model_name, code, title),
    or the specified column value, or str(row).
    Never raises VariableDoesNotExist or AttributeError.
    """
    if row is None:
        return '?'

    # Check dictionary
    if isinstance(row, dict):
        for key in ('name', 'username', 'model_name', 'code', 'title'):
            val = row.get(key)
            if val and str(val).strip():
                return str(val).strip()[0].upper()
        if col_name and row.get(col_name):
            val = row.get(col_name)
            if val and str(val).strip():
                return str(val).strip()[0].upper()

    # Check object attributes
    for attr in ('name', 'username', 'model_name', 'code', 'title', 'subject'):
        try:
            val = getattr(row, attr, None)
            if callable(val) and not isinstance(val, type):
                val = val()
            if val and str(val).strip():
                s = str(val).strip()
                if not s.startswith('<'):
                    return s[0].upper()
        except Exception:
            pass

    # If a specific column name was passed, try resolving it
    if col_name:
        try:
            val = get_attr(row, col_name)
            if val and str(val).strip():
                s = str(val).strip()
                if s.startswith('<'):
                    import re
                    s = re.sub(r'<[^>]+>', '', s).strip()
                if s and not s.startswith('<'):
                    return s[0].upper()
        except Exception:
            pass

    # Fallback to string representation of row
    try:
        s = str(row).strip()
        if s.startswith('<') and ':' in s:
            s = s.split(':', 1)[1].strip().strip('>')
        for ch in s:
            if ch.isalnum():
                return ch.upper()
    except Exception:
        pass

    return '•'


@register.filter
def record_name(row):
    """
    Safely extract a display name from any object/model/dict.
    Checks name, username, model_name, code, title, or str(row).
    """
    if row is None:
        return ''
    if isinstance(row, dict):
        for k in ('name', 'username', 'model_name', 'code', 'title'):
            if row.get(k):
                return str(row[k])
    for attr in ('name', 'username', 'model_name', 'code', 'title', 'subject'):
        try:
            val = getattr(row, attr, None)
            if callable(val) and not isinstance(val, type):
                val = val()
            if val:
                return str(val)
        except Exception:
            pass
    return str(row)


@register.filter
def record_login(row):
    """
    Safely extract login/email for user-like cards.
    """
    if row is None:
        return ''
    if isinstance(row, dict):
        return row.get('login') or row.get('email') or ''
    return getattr(row, 'login', None) or getattr(row, 'email', None) or ''


@register.filter
def avatar_color_num(val):
    """
    Returns an integer from 1 to 7 based on the ID or hash of val for avatar colors.
    """
    try:
        n = int(val)
        return (n % 7) + 1
    except (ValueError, TypeError):
        try:
            return (abs(hash(str(val))) % 7) + 1
        except Exception:
            return 1


