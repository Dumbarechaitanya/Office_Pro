import json
from django.contrib import messages
from django.contrib.auth import authenticate
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from base.models import ResUsers, ResUsersGroups
from authentication.auth_helpers import (
    get_current_ir_user, login_user, logout_user,
    hash_password, verify_password, login_required_ir,
    generate_otp, send_otp_email, store_otp, verify_otp, clear_otp, mask_email,
    get_user_linked_employee, safe_next_url, validate_new_password,
    uses_known_weak_password,
)
from authentication import throttle


def login_view(request):
    """
    Handles user login using Django's authentication system and custom ResUsersBackend.
    Allows authenticating and switching users on POST or when ?switch=1 is provided.

    Security: failed attempts are throttled per username + IP, redirects after login are
    restricted to this site, and accounts still using a default password are forced to
    change it (ForcePasswordChangeMiddleware).
    """
    error = None

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        locked, remaining = throttle.is_locked(request, identifier, scope='login')
        if locked:
            minutes = max(1, remaining // 60 + (1 if remaining % 60 else 0))
            error = f'Too many failed sign-in attempts. Please try again in {minutes} minute(s).'
        elif not identifier or not password:
            error = 'Please provide both username/email and password.'
        else:
            # Authenticate through Django's authentication framework
            user = authenticate(request, username=identifier, password=password)
            if user and user.is_active:
                throttle.reset(request, identifier, scope='login')
                first_login = user.last_login is None   # read BEFORE login_user() stamps it
                login_user(request, user)
                if first_login or uses_known_weak_password(user):
                    request.session['force_pw_change'] = True
                    messages.warning(request, 'Please choose a new password to continue (temporary or default password detected).')
                    return redirect('change_password')
                return redirect(safe_next_url(request, reverse('home')))
            else:
                throttle.register_failure(request, identifier, scope='login')
                error = 'Invalid username/email or password.'
    else:
        # If already logged in on GET, redirect directly unless user switch is requested
        current_user = get_current_ir_user(request)
        if current_user and not request.GET.get('switch'):
            return redirect(safe_next_url(request, reverse('home')))

    return render(request, 'authentication/login.html', {
        'error': error,
        'next': request.GET.get('next', ''),
        'switch_user': bool(request.GET.get('switch')),
    })


def logout_view(request):
    """
    Logs out the user and clears the session.
    """
    logout_user(request)
    return redirect('login')


def forgot_password_view(request):
    """
    Handles self-service Forgot Password flow via email OTP verification.
    Step 1: User provides registered email or username -> System sends 6-digit OTP.
    Step 2: User provides OTP + New Password + Confirm Password -> Password is updated.
    """
    current_user = get_current_ir_user(request)
    if current_user:
        return redirect('profile')

    error = None
    info = None
    step = 'request'  # 'request' or 'verify'
    target_email = request.session.get('auth_otp', {}).get('email', '') if 'auth_otp' in request.session else ''
    masked = mask_email(target_email)

    # Check if there is an active OTP in session
    if 'auth_otp' in request.session and request.session['auth_otp'].get('purpose') == 'reset':
        step = 'verify'

    if request.method == 'POST':
        action = request.POST.get('action', 'request_otp')

        if action == 'request_otp':
            identifier = request.POST.get('identifier', '').strip()
            if not identifier:
                error = 'Please enter your registered email address or username.'
            else:
                user = ResUsers.objects.filter(
                    models.Q(email__iexact=identifier) | models.Q(username__iexact=identifier),
                    is_active=True
                ).first()

                # Same answer whether or not the account exists (no account enumeration),
                # and at most one code per minute per identifier.
                generic_info = 'If an account matches, a 6-digit verification code has been sent to its registered email address.'
                if user and user.email and throttle.allow_once_per(request, identifier, 'otp-send', 60):
                    otp = generate_otp(6)
                    send_otp_email(user.email, otp, username=user.username, purpose='Password Reset')
                    store_otp(request, user.email, otp, purpose='reset', user_id=user.id)
                    target_email = user.email
                    masked = mask_email(target_email)
                    step = 'verify'
                    info = f'A 6-digit verification code has been sent to {masked}.'
                elif user and user.email:
                    error = 'Please wait a minute before requesting another code.'
                else:
                    # Show the verify step anyway so the response looks identical.
                    step = 'request'
                    info = generic_info

        elif action == 'verify_and_reset':
            otp = request.POST.get('otp', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            otp_data = request.session.get('auth_otp')
            if not otp_data or otp_data.get('purpose') != 'reset':
                error = 'Your session has expired. Please request a new verification code.'
                step = 'request'
            else:
                ok, err_msg = verify_otp(request, otp_data.get('email'), otp, purpose='reset')
                if not ok:
                    error = err_msg
                    step = 'verify'
                elif new_password != confirm_password:
                    error = 'New passwords do not match.'
                    step = 'verify'
                elif validate_new_password(new_password):
                    error = validate_new_password(new_password)
                    step = 'verify'
                else:
                    user_id = otp_data.get('user_id')
                    user = ResUsers.objects.filter(id=user_id, is_active=True).first()
                    if not user:
                        error = 'User account could not be found.'
                        step = 'request'
                    else:
                        user.password_hash = hash_password(new_password)
                        user.save(update_fields=['password_hash', 'updated_at'])
                        clear_otp(request)
                        messages.success(request, 'Your password has been successfully reset! You can now log in.')
                        return redirect('login')

        elif action == 'cancel':
            clear_otp(request)
            return redirect('login')

    return render(request, 'authentication/forgot_password.html', {
        'error': error,
        'info': info,
        'step': step,
        'target_email': target_email,
        'masked_email': masked,
    })


@require_POST
def send_otp_ajax(request):
    """
    AJAX endpoint for requesting an OTP verification code via email.
    Supports purpose: 'forgot_password' or 'change_password'.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    purpose_type = data.get('purpose', 'change_password')
    email = data.get('email', '').strip()

    if purpose_type == 'change_password':
        user = get_current_ir_user(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
        target_email = user.email
        target_user = user
        purpose_label = 'Password Change'
        session_purpose = 'change'
    else:
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email or username is required.'}, status=400)
        target_user = ResUsers.objects.filter(
            models.Q(email__iexact=email) | models.Q(username__iexact=email),
            is_active=True
        ).first()
        if not target_user or not target_user.email:
            # Identical response for unknown accounts -> no account enumeration.
            return JsonResponse({
                'status': 'success',
                'message': 'If an account matches, a verification code has been sent.',
            })
        target_email = target_user.email
        purpose_label = 'Password Reset'
        session_purpose = 'reset'

    if not throttle.allow_once_per(request, target_email, 'otp-send', 60):
        return JsonResponse({'status': 'error', 'message': 'Please wait a minute before requesting another code.'}, status=429)

    otp = generate_otp(6)
    send_otp_email(target_email, otp, username=target_user.username, purpose=purpose_label)
    store_otp(request, target_email, otp, purpose=session_purpose, user_id=target_user.id)

    return JsonResponse({
        'status': 'success',
        'message': f'Verification code sent to {mask_email(target_email)}.',
        'masked_email': mask_email(target_email),
    })


@login_required_ir
def profile_view(request):
    """
    Renders the authenticated user's profile, user credentials, linked employee profile, and security groups.
    """
    user = get_current_ir_user(request)
    if not user:
        return redirect('login')

    user_groups = ResUsersGroups.objects.filter(user=user, is_active=True).select_related('group')
    employee = get_user_linked_employee(user)

    return render(request, 'authentication/profile.html', {
        'profile_user': user,
        'user_groups': user_groups,
        'employee': employee,
    })


@login_required_ir
def change_password_view(request):
    """
    Allows the logged-in user to securely update their password either using their
    Current Password OR an Email OTP verification code.
    """
    user = get_current_ir_user(request)
    if not user:
        return redirect('login')

    error = None
    success = None
    masked = mask_email(user.email)

    if request.method == 'POST':
        method = request.POST.get('method', 'current_password')  # 'current_password' or 'email_otp'
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        pw_error = validate_new_password(new_password, user=user)
        if pw_error:
            error = pw_error
        elif new_password != confirm_password:
            error = 'New passwords do not match.'
        elif method == 'current_password':
            current_password = request.POST.get('current_password', '').strip()
            locked, _remaining = throttle.is_locked(request, str(user.id), scope='chgpw')
            if locked:
                error = 'Too many incorrect attempts. Please try again later.'
            elif not verify_password(current_password, user.password_hash):
                throttle.register_failure(request, str(user.id), scope='chgpw')
                error = 'Current password is incorrect.'
            else:
                throttle.reset(request, str(user.id), scope='chgpw')
                user.password_hash = hash_password(new_password)
                user.save(update_fields=['password_hash', 'updated_at'])
                request.session.pop('force_pw_change', None)
                login_user(request, user)
                messages.success(request, 'Password updated successfully.')
                return redirect('profile')
        elif method == 'email_otp':
            otp = request.POST.get('otp', '').strip()
            ok, err_msg = verify_otp(request, user.email, otp, purpose='change')
            if not ok:
                error = err_msg
            else:
                user.password_hash = hash_password(new_password)
                user.save(update_fields=['password_hash', 'updated_at'])
                clear_otp(request)
                request.session.pop('force_pw_change', None)
                login_user(request, user)
                messages.success(request, 'Password updated successfully via email OTP verification.')
                return redirect('profile')

    return render(request, 'authentication/change_password.html', {
        'profile_user': user,
        'masked_email': masked,
        'error': error,
        'success': success,
    })
