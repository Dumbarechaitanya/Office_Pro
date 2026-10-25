"""Regression tests for the security fixes (backdoor, brute force, OTP, open redirect ...)."""
import time
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from django.contrib.auth.hashers import make_password
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from authentication import throttle
from authentication.auth_helpers import (
    OTP_MAX_ATTEMPTS, clear_otp, generate_temp_password, safe_next_url, store_otp,
    uses_known_weak_password, validate_new_password, verify_otp, verify_password,
)
from authentication.backends import ResUsersBackend
from base.models import ResUsers

LOCMEM = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'sec-tests'}}


def make_request(factory, method='get', path='/', data=None, **extra):
    request = getattr(factory, method)(path, data or {}, **extra)
    request.session = SessionStore()
    request._messages = FallbackStorage(request)
    return request


class BackdoorAndPlaintextRemovedTests(SimpleTestCase):
    """Fix #2: hardcoded admin passwords and plaintext fallback are gone."""

    def setUp(self):
        self.backend = ResUsersBackend()
        self.factory = RequestFactory()

    def _auth(self, user, password):
        with patch('base.models.ResUsers.objects.filter') as mock_filter:
            mock_filter.return_value.select_related.return_value.first.return_value = user
            return self.backend.authenticate(self.factory.post('/login/'), username=user.username, password=password)

    def test_admin_does_not_accept_hardcoded_passwords(self):
        admin = ResUsers(id=1, username='admin', email='admin@x.test', is_active=True,
                         password_hash=make_password('A-Really-Long-Secret-1!'))
        for pwd in ('admin', '123', 'admin123', 'Admin@123'):
            self.assertIsNone(self._auth(admin, pwd), f'backdoor password {pwd!r} must not work')
        self.assertIsNotNone(self._auth(admin, 'A-Really-Long-Secret-1!'))

    def test_plaintext_password_in_database_never_authenticates(self):
        user = ResUsers(id=2, username='bob', email='bob@x.test', is_active=True, password_hash='plaintext-pass')
        self.assertIsNone(self._auth(user, 'plaintext-pass'))
        self.assertFalse(verify_password('plaintext-pass', 'plaintext-pass'))

    def test_unknown_hash_format_is_rejected_not_crashing(self):
        self.assertFalse(verify_password('x', 'not$a$real$hash'))


class WeakPasswordTests(SimpleTestCase):
    def test_detects_default_123(self):
        user = SimpleNamespace(password_hash=make_password('123'))
        self.assertTrue(uses_known_weak_password(user))
        self.assertFalse(uses_known_weak_password(SimpleNamespace(password_hash=make_password('Tr0ub4dor&3-horse'))))

    def test_validate_new_password_rejects_weak(self):
        self.assertIsNotNone(validate_new_password('123'))
        self.assertIsNotNone(validate_new_password('short'))
        self.assertIsNotNone(validate_new_password('12345678'))
        self.assertIsNone(validate_new_password('Correct-Horse-Battery-9'))

    def test_generated_temp_password_is_strong(self):
        for _ in range(20):
            pwd = generate_temp_password()
            self.assertGreaterEqual(len(pwd), 12)
            self.assertIsNone(validate_new_password(pwd))


class SafeRedirectTests(SimpleTestCase):
    """Fix #5: open redirect via ?next="""

    def setUp(self):
        self.factory = RequestFactory()

    def test_external_and_scheme_tricks_are_rejected(self):
        for evil in ('https://evil.example/phish', '//evil.example', 'javascript:alert(1)',
                     'http://testserver.evil.example/', '/\\evil.example'):
            request = self.factory.get('/login/', {'next': evil})
            self.assertEqual(safe_next_url(request, '/home/'), '/home/', evil)

    def test_local_paths_are_allowed(self):
        request = self.factory.get('/login/', {'next': '/time-off/?x=1'})
        self.assertEqual(safe_next_url(request, '/home/'), '/time-off/?x=1')

    def test_post_value_is_checked_too(self):
        request = self.factory.post('/login/', {'next': 'https://evil.example'})
        self.assertEqual(safe_next_url(request, '/home/'), '/home/')


@override_settings(CACHES=LOCMEM, LOGIN_MAX_FAILURES=3, LOGIN_LOCKOUT_SECONDS=60)
class LoginThrottleTests(SimpleTestCase):
    """Fix #4: brute-force protection on login."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.factory = RequestFactory()

    def test_lock_after_max_failures_and_reset_on_success(self):
        request = make_request(self.factory, 'post', '/login/')
        for _ in range(2):
            throttle.register_failure(request, 'alice')
        self.assertFalse(throttle.is_locked(request, 'alice')[0])
        throttle.register_failure(request, 'alice')
        locked, remaining = throttle.is_locked(request, 'alice')
        self.assertTrue(locked)
        self.assertGreater(remaining, 0)
        throttle.reset(request, 'alice')
        self.assertFalse(throttle.is_locked(request, 'alice')[0])

    def test_lock_is_per_user_and_ip(self):
        r1 = make_request(self.factory, 'post', '/login/', REMOTE_ADDR='10.0.0.1')
        r2 = make_request(self.factory, 'post', '/login/', REMOTE_ADDR='10.0.0.2')
        for _ in range(3):
            throttle.register_failure(r1, 'alice')
        self.assertTrue(throttle.is_locked(r1, 'alice')[0])
        self.assertFalse(throttle.is_locked(r2, 'alice')[0])   # other IP unaffected
        self.assertFalse(throttle.is_locked(r1, 'bob')[0])      # other user unaffected

    def test_rotating_spoofed_ip_header_cannot_bypass_the_cap(self):
        """An attacker changing X-Forwarded-For on every guess still gets locked out (cap = 4x limit)."""
        locked = False
        for i in range(30):
            request = make_request(self.factory, 'post', '/login/', HTTP_X_FORWARDED_FOR=f'203.0.113.{i}')
            locked, _ = throttle.is_locked(request, 'victim')
            if locked:
                break
            throttle.register_failure(request, 'victim')
        self.assertTrue(locked)
        self.assertLessEqual(i, 3 * 4 + 5)   # LOGIN_MAX_FAILURES=3 -> global cap 12

    def test_cooldown_allows_once(self):
        request = make_request(self.factory, 'post', '/auth/send-otp/')
        self.assertTrue(throttle.allow_once_per(request, 'a@x.test', 'otp-send', 60))
        self.assertFalse(throttle.allow_once_per(request, 'a@x.test', 'otp-send', 60))

    @patch('authentication.views.login_user')
    @patch('authentication.views.authenticate', return_value=None)
    def test_login_view_blocks_even_correct_password_when_locked(self, mock_auth, mock_login):
        from authentication.views import login_view
        for _ in range(3):
            request = make_request(self.factory, 'post', '/login/', {'username': 'alice', 'password': 'wrong'})
            with patch('authentication.views.render') as mock_render:
                login_view(request)
        mock_auth.reset_mock()
        mock_auth.return_value = SimpleNamespace(is_active=True, last_login=1, password_hash='x')
        request = make_request(self.factory, 'post', '/login/', {'username': 'alice', 'password': 'right'})
        with patch('authentication.views.render') as mock_render:
            login_view(request)
        mock_auth.assert_not_called()                    # authentication is not even attempted
        mock_login.assert_not_called()
        self.assertIn('Too many failed', mock_render.call_args[0][2]['error'])


class OtpHardeningTests(SimpleTestCase):
    """Fix #4: OTP can't be brute-forced; only a hash is kept in the session."""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = make_request(self.factory, 'post', '/forgot-password/')

    def test_otp_is_not_stored_in_plaintext(self):
        store_otp(self.request, 'a@x.test', '123456', purpose='reset', user_id=1)
        self.assertNotIn('123456', str(self.request.session['auth_otp']))

    def test_correct_otp_passes(self):
        store_otp(self.request, 'a@x.test', '123456', purpose='reset', user_id=1)
        ok, _ = verify_otp(self.request, 'a@x.test', '123456', purpose='reset')
        self.assertTrue(ok)

    def test_otp_destroyed_after_max_wrong_attempts(self):
        store_otp(self.request, 'a@x.test', '123456', purpose='reset', user_id=1)
        for _ in range(OTP_MAX_ATTEMPTS):
            ok, _ = verify_otp(self.request, 'a@x.test', '000000', purpose='reset')
            self.assertFalse(ok)
        # even the CORRECT code no longer works -> attacker must request a new one
        ok, msg = verify_otp(self.request, 'a@x.test', '123456', purpose='reset')
        self.assertFalse(ok)
        self.assertNotIn('auth_otp', self.request.session)

    def test_expired_otp_rejected(self):
        store_otp(self.request, 'a@x.test', '123456', purpose='reset', user_id=1, expiry_seconds=-1)
        ok, msg = verify_otp(self.request, 'a@x.test', '123456', purpose='reset')
        self.assertFalse(ok)
        self.assertIn('expired', msg)


class ForcePasswordChangeTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _run(self, path, flagged=True):
        from base.middleware import ForcePasswordChangeMiddleware
        mw = ForcePasswordChangeMiddleware(lambda req: HttpResponse('OK'))
        request = make_request(self.factory, 'get', path)
        if flagged:
            request.session['force_pw_change'] = True
        return mw(request)

    def test_redirects_everything_to_change_password(self):
        response = self._run('/time-off/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profile/password/')

    def test_change_password_logout_and_static_stay_reachable(self):
        for path in ('/profile/password/', '/logout/', '/static/x.css'):
            self.assertEqual(self._run(path).status_code, 200, path)

    def test_unflagged_users_unaffected(self):
        self.assertEqual(self._run('/time-off/', flagged=False).status_code, 200)

    def test_json_requests_get_403_not_redirect(self):
        from base.middleware import ForcePasswordChangeMiddleware
        mw = ForcePasswordChangeMiddleware(lambda req: HttpResponse('OK'))
        request = make_request(self.factory, 'get', '/batch-action/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        request.session['force_pw_change'] = True
        self.assertEqual(mw(request).status_code, 403)
