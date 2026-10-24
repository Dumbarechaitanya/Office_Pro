import uuid
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from base.models import extract_diagnostics_from_exception, IrLogging

# In-memory unique ID generated on every server startup / reboot
SERVER_BOOT_ID = uuid.uuid4().hex


class DebugModeMiddleware:
    """
    Middleware that manages Odoo-style Developer Mode (?debug=1):
    - Debug mode persists across page navigations in session and in URL query path.
    - If the server is rebooted (restarted), SERVER_BOOT_ID changes and debug mode is automatically reset.
    - If ?debug=1 is visited, debug mode is activated for the session.
    - If ?debug=0 (or false) is visited, debug mode is deactivated and cleanly removed from the URL.
    - While debug mode is active, any standard GET page navigation without '?debug=' is automatically
      redirected to maintain '?debug=1' in the browser address bar.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'session'):
            # Check for server reboot
            if request.session.get('server_boot_id') != SERVER_BOOT_ID:
                request.session['debug'] = False
                request.session['server_boot_id'] = SERVER_BOOT_ID

            # Check for explicit debug param in query string
            debug_param = request.GET.get('debug')
            if debug_param is not None:
                if debug_param in ('1', 'true', 'assets', ''):
                    request.session['debug'] = True
                    request.session['server_boot_id'] = SERVER_BOOT_ID
                elif debug_param in ('0', 'false', 'no'):
                    request.session['debug'] = False
                    # Cleanly redirect to remove ?debug=0 from browser address bar
                    if request.method == 'GET':
                        query = request.GET.copy()
                        del query['debug']
                        target_url = request.path
                        if query:
                            target_url += f"?{query.urlencode()}"
                        return HttpResponseRedirect(target_url)

            # Check if debug mode is currently active
            is_debug = bool(request.session.get('debug', False))

            # If debug mode is active, ensure '?debug=1' remains in the URL path for HTML GET navigations
            if is_debug and request.method == 'GET':
                # Skip AJAX, static files, media files, and API endpoints
                is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', '')
                is_static_or_media = request.path.startswith(settings.STATIC_URL) or (settings.MEDIA_URL and request.path.startswith(settings.MEDIA_URL))
                is_api_or_action = request.path in ('/batch-action/', '/technical/relation-search/', '/auth/send-otp/') or request.path.startswith('/auth/send-otp')

                if not is_ajax and not is_static_or_media and not is_api_or_action and 'debug' not in request.GET:
                    query = request.GET.copy()
                    query['debug'] = '1'
                    target_url = f"{request.path}?{query.urlencode()}"
                    return HttpResponseRedirect(target_url)

        return self.get_response(request)


class GlobalExceptionDiagnosticMiddleware:
    """
    Global exception diagnostic middleware:
    - Catches unhandled exceptions across all HTTP and AJAX requests
    - Extracts the exact error type, file, line number, module, and formatted stack frames
    - Logs the exception to the database in `ir.logging` (IrLogging)
    - If request is AJAX/JSON, returns a structured JSON error response (HTTP 500)
    - If request is standard HTML navigation, renders the high-fidelity 500 error page with diagnostics
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        diag = extract_diagnostics_from_exception(exception, request=request)
        # Persistent database log
        IrLogging.log_exception(exception, request=request, level='ERROR', log_type='server')

        # Check if AJAX / JSON request
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            'application/json' in request.headers.get('accept', '') or
            request.path.endswith('/test-connection/') or
            request.path.endswith('-live/') or
            request.path.startswith('/batch-action/')
        )

        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': True,
                'error_type': diag['error_type'],
                'message': diag['message'],
                'file': diag['file'],
                'line': diag['line'],
                'function': diag['function'],
                'details': f"Execution Point: {diag['file']}:L{diag['line']} in {diag['function']}()\nError: {diag['error_type']}: {diag['message']}" + (f"\n\nHint: {diag['hint']}" if diag['hint'] else ""),
                'traceback': diag['traceback'],
                'hint': diag['hint'],
            }, status=500)

        is_debug = False
        if hasattr(request, 'session'):
            is_debug = bool(request.session.get('debug', False))
        if not is_debug:
            is_debug = getattr(settings, 'DEBUG', False)

        return render(request, 'base/500.html', {
            'exception': exception,
            'diag': diag,
            'is_debug': is_debug,
            'request_url': request.build_absolute_uri() if hasattr(request, 'build_absolute_uri') else request.path,
            'request_method': request.method,
            'request_user': getattr(request, 'user', None),
        }, status=500)


class EnforceLoginMiddleware:
    """
    Enterprise Security Middleware:
    Guarantees that unauthenticated visitors cannot view or access the home page,
    apps, settings, or any internal ERP module.
    Redirects all unauthenticated requests directly to the login screen (/login/).
    """
    EXEMPT_PREFIXES = (
        '/login',
        '/logout',
        '/forgot-password',
        '/reset-password',
        '/auth/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/admin/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        if any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return self.get_response(request)

        from base.auth_helpers import get_current_ir_user
        user = get_current_ir_user(request)
        if not user or not getattr(user, 'is_active', False):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
                return JsonResponse({'error': 'Authentication required. Please log in.'}, status=401)
            next_url = request.get_full_path()
            return HttpResponseRedirect(f"/login/?next={next_url}")

        return self.get_response(request)

