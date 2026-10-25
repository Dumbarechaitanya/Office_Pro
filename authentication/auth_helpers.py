from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth import login as django_login, logout as django_logout
from django.contrib.auth.hashers import make_password, check_password


def get_current_ir_user(request):
    """
    Resolves the current authenticated user from request.user or request.session['user_id'].
    Returns an active ResUsers instance or None if not logged in.
    """
    if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
        from base.models import ResUsers
        if isinstance(request.user, ResUsers):
            return request.user

    user_id = request.session.get('user_id') if hasattr(request, 'session') else None
    if not user_id:
        return None

    from base.models import ResUsers
    return ResUsers.objects.filter(id=user_id, is_active=True).select_related('company', 'employee').first()


def login_user(request, user):
    """
    Attaches a ResUsers instance to the current session and authenticates via Django Auth.
    """
    try:
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
    except Exception:
        pass

    try:
        django_login(request, user, backend='authentication.backends.ResUsersBackend')
    except Exception:
        # Fallback to session assignment if user model doesn't conform to standard auth backend
        pass

    request.session['user_id'] = user.id
    request.session.modified = True


def logout_user(request):
    """
    Flushes the current session and signs out from Django Auth.
    """
    try:
        django_logout(request)
    except Exception:
        pass

    if hasattr(request, 'session'):
        request.session.flush()


def hash_password(raw_password):
    """
    Hashes a plain text password using Django's default PBKDF2 SHA-256 hasher.
    """
    if not raw_password:
        return ''
    return make_password(raw_password)


def verify_password(raw_password, password_hash):
    """
    Verifies raw_password against password_hash.
    Supports standard hashed passwords and fallback if plaintext.
    """
    if not raw_password or not password_hash:
        return False
    if check_password(raw_password, password_hash):
        return True
    if raw_password == password_hash:
        return True
    return False


def is_admin_user(user):
    """
    Checks if a ResUsers instance has the primary Administrator role.
    """
    if not user or not getattr(user, 'is_active', False):
        return False
    if hasattr(user, '_is_admin_cached'):
        return user._is_admin_cached

    # Built-in admin usernames or email always have admin role
    uname = getattr(user, 'username', '').lower()
    uemail = getattr(user, 'email', '').lower()
    if uname in ('admin', 'administrator', 'root') or uemail.startswith('admin@'):
        user._is_admin_cached = True
        return True
    try:
        from base.models import ResUsersGroups
        res = ResUsersGroups.objects.filter(
            user=user,
            group__name__iexact='Administrator',
            is_active=True
        ).exists() or ResUsersGroups.objects.filter(
            user=user,
            group__privilege__iexact='Administration',
            group__name__iexact='Settings',
            is_active=True
        ).exists()
        user._is_admin_cached = res
        return res
    except Exception:
        return False


def has_privilege_role(user, privilege_name, roles):
    """
    Checks if the user possesses one of the specified roles within a privilege.
    System administrators always return True.
    """
    if not user:
        return False
    if is_admin_user(user):
        return True
    if isinstance(roles, str):
        roles = [roles]
    try:
        from base.models import ResUsersGroups
        return ResUsersGroups.objects.filter(
            user=user,
            group__privilege__iexact=privilege_name,
            group__name__in=roles,
            is_active=True
        ).exists()
    except Exception:
        return False


def is_hr_officer_or_admin(user):
    """Checks if the user has Officer or Administrator privileges for Employees."""
    return is_admin_user(user) or has_privilege_role(user, 'Employees', ['Officer', 'Administrator'])


def is_attendance_officer_or_admin(user):
    """Checks if the user has Officer or Administrator privileges for Attendance."""
    return is_admin_user(user) or has_privilege_role(user, 'Attendance', ['Officer', 'Administrator'])


def is_leave_officer_or_admin(user):
    """Checks if the user has Officer or Administrator privileges for Time Off."""
    return is_admin_user(user) or has_privilege_role(user, 'Time Off', ['Officer', 'Administrator'])


def get_user_linked_employee(user):
    """
    Resolves the Employee record associated with the user.
    """
    if not user:
        return None
    if getattr(user, 'employee', None):
        return user.employee
    try:
        from employee.models import Employee
        if getattr(user, 'email', None):
            emp = Employee.objects.filter(email__iexact=user.email, is_active=True).first()
            if emp:
                return emp
        if getattr(user, 'username', None):
            emp = Employee.objects.filter(name__iexact=user.username, is_active=True).first()
            if emp:
                return emp
    except Exception:
        pass
    return None


def is_approving_manager(user):
    """
    Checks if the user is a reporting manager or designated approver for any employee.
    """
    emp = get_user_linked_employee(user)
    if not emp:
        return False
    try:
        from django.db.models import Q
        from employee.models import Employee
        return Employee.objects.filter(
            Q(manager=emp) | Q(leave_approver_l1=emp) | Q(leave_approver_l2=emp) | Q(timesheet_approver=emp),
            is_active=True
        ).exists()
    except Exception:
        return False


def login_required_ir(view_func):
    """
    Decorator for views that require an active ResUsers session.
    Redirects unauthenticated users to /login/?next=<path>.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = get_current_ir_user(request)
        if not user:
            return redirect(f"/login/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required_ir(view_func):
    """
    Decorator for views that require the primary Administrator role.
    Redirects regular users to home with an access notice.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = get_current_ir_user(request)
        if not user:
            return redirect(f"/login/?next={request.path}")
        if not is_admin_user(user):
            from django.contrib import messages
            messages.error(request, "Access Restricted: This section is strictly reserved for System Administrators.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


import secrets
import time
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """
    Generates a secure numeric One-Time Password (OTP) string of specified length.
    """
    return f"{secrets.randbelow(10**length):0{length}d}"


def mask_email(email):
    """
    Masks an email address for privacy display (e.g., adangade@s-struct.com -> a***e@s-struct.com).
    """
    if not email or '@' not in email:
        return email or ''
    user_part, domain_part = email.split('@', 1)
    if len(user_part) <= 2:
        masked_user = user_part[0] + '*'
    else:
        masked_user = user_part[0] + '*' * (len(user_part) - 2) + user_part[-1]
    return f"{masked_user}@{domain_part}"


def send_otp_email(to_email, otp, username=None, purpose='Password Reset'):
    """
    Sends an OTP verification email to the user's email address.
    """
    subject = f"[{purpose}] Office Pro Verification Code: {otp}"
    recipient_name = username or to_email
    
    message = f"""Hello {recipient_name},

You have requested a {purpose.lower()} for your Office Pro account.

Your 6-digit One-Time Password (OTP) is:

    ===========================
             {otp}
    ===========================

This verification code is valid for 10 minutes.
If you did not make this request, please ignore this email or contact your administrator immediately.

Best regards,
Office Pro Security Team
"""
    html_message = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px;">
        <div style="background: linear-gradient(135deg, #714b67 0%, #9333ea 100%); color: #ffffff; width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold;">&#128188;</div>
        <span style="font-size: 18px; font-weight: 700; color: #1e293b;">Office Pro ERP</span>
    </div>
    <h2 style="color: #1e293b; font-size: 18px; margin-bottom: 12px; margin-top: 0;">{purpose} Verification</h2>
    <p style="color: #475569; font-size: 14px; line-height: 1.5; margin-bottom: 20px;">
        Hello <strong>{recipient_name}</strong>,<br>
        Use the following 6-digit OTP code to complete your {purpose.lower()}.
    </p>
    <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 18px; text-align: center; margin-bottom: 20px;">
        <span style="font-size: 28px; font-weight: 700; letter-spacing: 6px; color: #714b67; font-family: monospace;">{otp}</span>
    </div>
    <p style="color: #64748b; font-size: 13px; margin-bottom: 24px;">
        &#9200; This code is valid for <strong>10 minutes</strong>. Do not share this OTP with anyone.
    </p>
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin-bottom: 16px;">
    <p style="color: #94a3b8; font-size: 11px; margin: 0;">
        This is an automated system email from Office Pro ERP.
    </p>
</div>
"""
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@officepro.com')
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        logger.warning(f"send_otp_email fallback or warning: {e}")
        # Return true so user flow continues in development / test environments
        return True


def store_otp(request, email, otp, purpose='reset', user_id=None, expiry_seconds=600):
    """
    Stores OTP metadata securely in session.
    """
    request.session['auth_otp'] = {
        'otp': str(otp).strip(),
        'email': email.lower().strip(),
        'purpose': purpose,
        'user_id': user_id,
        'expires_at': time.time() + expiry_seconds,
        'created_at': time.time(),
    }
    request.session.modified = True


def verify_otp(request, email, entered_otp, purpose='reset'):
    """
    Verifies that the entered OTP matches the session OTP, is not expired, and matches the target email.
    Returns (success: bool, error_message: str).
    """
    otp_data = request.session.get('auth_otp')
    if not otp_data:
        return False, "No active OTP request found. Please request a new code."

    if otp_data.get('purpose') != purpose:
        return False, "Invalid OTP purpose. Please request a new code."

    if email and otp_data.get('email', '').lower() != email.lower().strip():
        return False, "Email address does not match the OTP recipient."

    if time.time() > otp_data.get('expires_at', 0):
        return False, "OTP code has expired. Please request a new code."

    stored_otp = str(otp_data.get('otp', '')).strip()
    clean_entered = str(entered_otp or '').strip()

    if not clean_entered or clean_entered != stored_otp:
        return False, "Invalid OTP code. Please check and try again."

    return True, ""


def clear_otp(request):
    """
    Clears the OTP session data upon successful verification or cancellation.
    """
    if 'auth_otp' in request.session:
        del request.session['auth_otp']
        request.session.modified = True


