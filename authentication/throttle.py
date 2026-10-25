"""
Brute-force protection for login and one-time-password (OTP) endpoints.

Counters live in Django's cache (configured as a shared DatabaseCache in settings so the
counters are visible to every gunicorn worker).  If the cache is unavailable the helpers
"fail open" and log a warning -- a broken cache must not lock every user out of the ERP --
so make sure `python manage.py createcachetable` has been run (build.sh does this).
"""
import logging
import time

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def client_ip(request):
    """Best-effort client IP.  Render puts the real client first in X-Forwarded-For."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _key(scope, identifier, ip):
    ident = (identifier or '').strip().lower()[:150]
    return f"throttle:{scope}:{ident}:{ip}"


def _gkey(scope, identifier):
    """Per-username key that does NOT depend on the client IP (X-Forwarded-For can be spoofed)."""
    return f"throttle:{scope}:{(identifier or '').strip().lower()[:150]}:*"


def _max_failures():
    return int(getattr(settings, 'LOGIN_MAX_FAILURES', 5))


def _global_max_failures():
    """Hard cap per username across ALL IPs, so rotating a spoofed X-Forwarded-For does not help."""
    return _max_failures() * 4


def _lockout_seconds():
    return int(getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 900))


def _remaining(data):
    if not data:
        return 0
    return int(data.get('locked_until', 0) - time.time())


def is_locked(request, identifier, scope='login'):
    """Return (locked: bool, seconds_remaining: int)."""
    try:
        per_ip = _remaining(cache.get(_key(scope, identifier, client_ip(request))))
        overall = _remaining(cache.get(_gkey(scope, identifier)))
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning('Throttle cache read failed (failing open): %s', exc)
        return False, 0
    remaining = max(per_ip, overall)
    if remaining > 0:
        return True, remaining
    return False, 0


def _bump(key, limit):
    data = cache.get(key) or {'count': 0, 'locked_until': 0}
    # A previous lock that already expired starts a fresh count.
    if data.get('locked_until', 0) and data['locked_until'] <= time.time():
        data = {'count': 0, 'locked_until': 0}
    data['count'] += 1
    if data['count'] >= limit:
        data['locked_until'] = time.time() + _lockout_seconds()
    cache.set(key, data, timeout=_lockout_seconds() * 2)


def register_failure(request, identifier, scope='login'):
    """Record one failed attempt; lock the identifier(+IP) once the limits are hit."""
    try:
        _bump(_key(scope, identifier, client_ip(request)), _max_failures())
        _bump(_gkey(scope, identifier), _global_max_failures())
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning('Throttle cache write failed (failing open): %s', exc)


def reset(request, identifier, scope='login'):
    try:
        cache.delete(_key(scope, identifier, client_ip(request)))
        cache.delete(_gkey(scope, identifier))
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning('Throttle cache delete failed: %s', exc)


def allow_once_per(request, identifier, scope, seconds):
    """Cool-down helper (e.g. one OTP e-mail per 60 s).  Returns True if the action may run."""
    key = _key(scope, identifier, client_ip(request))
    try:
        if cache.get(key):
            return False
        cache.set(key, 1, timeout=seconds)
        return True
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning('Throttle cooldown failed (failing open): %s', exc)
        return True
