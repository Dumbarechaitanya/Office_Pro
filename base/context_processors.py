from authentication.auth_helpers import (
    get_current_ir_user,
    is_admin_user,
    get_user_linked_employee,
    is_hr_officer_or_admin,
    is_attendance_officer_or_admin,
    is_leave_officer_or_admin,
    is_approving_manager,
)
from base.middleware import SERVER_BOOT_ID


def auth_context(request):
    """
    Injects the active ResUsers instance, role flags, linked employee, and debug mode into template contexts.
    """
    if hasattr(request, 'session'):
        if request.session.get('server_boot_id') != SERVER_BOOT_ID:
            request.session['debug'] = False
            request.session['server_boot_id'] = SERVER_BOOT_ID
        is_debug = bool(request.session.get('debug', False))
    else:
        is_debug = bool(request.GET.get('debug') in ('1', 'true', 'assets', ''))

    user = get_current_ir_user(request)
    is_admin = is_admin_user(user) if user else False
    current_emp = get_user_linked_employee(user) if user else None
    
    is_hr_officer = is_hr_officer_or_admin(user) if user else False
    is_att_officer = is_attendance_officer_or_admin(user) if user else False
    is_lv_officer = is_leave_officer_or_admin(user) if user else False
    is_mgr = is_approving_manager(user) if user else False

    return {
        'current_user': user,
        'current_emp': current_emp,
        'is_admin': is_admin,
        'is_debug': is_debug,
        'is_hr_officer': is_hr_officer,
        'is_attendance_officer': is_att_officer,
        'is_leave_officer': is_lv_officer,
        'is_officer': is_att_officer or is_lv_officer or is_hr_officer,
        'is_manager': is_mgr,
        'is_officer_or_manager': is_att_officer or is_lv_officer or is_hr_officer or is_mgr,
        'is_leave_officer_or_manager': is_lv_officer or is_mgr,
    }


def theme_context(request):
    """
    Injects the active theme settings and static asset cache version into all template contexts.
    Uses clean, sleek corporate slate/blue aesthetics (zero purple).
    """
    default_theme = {
        'preset': 'corporate_blue',
        'primary_color': '#2563eb',
        'primary_hover': '#1d4ed8',
        'navbar_bg': '#0f172a',
        'wallpaper': 'corporate_clean',
    }
    theme = request.session.get('theme_settings', default_theme)
    return {
        'active_theme': theme,
        'static_version': SERVER_BOOT_ID[:8] if SERVER_BOOT_ID else '1.0',
    }


def installed_modules_context(request):
    """
    Provides installed_modules set to all templates so UI elements (tabs, smart buttons, menus)
    can render conditionally based on active apps.
    """
    try:
        from base.module_manager import get_installed_modules
        installed = get_installed_modules()
    except Exception:
        installed = {'base', 'res', 'hr', 'mail'}
    return {
        'installed_modules': installed,
    }


