from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser

from base.models import ResUsers
from authentication.backends import ResUsersBackend
from authentication.auth_helpers import (
    hash_password, verify_password, get_current_ir_user,
    login_user, logout_user, login_required_ir
)
from authentication.views import login_view, logout_view, profile_view, change_password_view


class AuthenticationTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.backend = ResUsersBackend()
        self.raw_password = 'SecretPassword123!'
        self.password_hash = hash_password(self.raw_password)

    def _add_session(self, request):
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        return request


    def test_password_hashing_and_verification(self):
        hashed = hash_password('TestPass')
        self.assertTrue(verify_password('TestPass', hashed))
        self.assertFalse(verify_password('WrongPass', hashed))
        # Plaintext passwords must NOT be accepted
        self.assertFalse(verify_password('plain', 'plain'))

    @patch('base.models.ResUsers.objects.filter')
    def test_backend_authenticate_with_username(self, mock_filter):
        mock_user = ResUsers(id=1, username='admin', email='admin@example.com', password_hash=self.password_hash, is_active=True)
        mock_filter.return_value.select_related.return_value.first.return_value = mock_user

        request = self.factory.post('/login/')
        user = self.backend.authenticate(request, username='admin', password=self.raw_password)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'admin')

    @patch('base.models.ResUsers.objects.filter')
    def test_backend_authenticate_with_email(self, mock_filter):
        mock_user = ResUsers(id=1, username='admin', email='admin@example.com', password_hash=self.password_hash, is_active=True)
        mock_filter.return_value.select_related.return_value.first.return_value = mock_user

        request = self.factory.post('/login/')
        user = self.backend.authenticate(request, username='admin@example.com', password=self.raw_password)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'admin@example.com')

    @patch('base.models.ResUsers.objects.filter')
    def test_backend_authenticate_invalid_password(self, mock_filter):
        mock_user = ResUsers(id=1, username='admin', email='admin@example.com', password_hash=self.password_hash, is_active=True)
        mock_filter.return_value.select_related.return_value.first.return_value = mock_user

        request = self.factory.post('/login/')
        user = self.backend.authenticate(request, username='admin', password='WrongPassword!')
        self.assertIsNone(user)

    @patch('base.models.ResUsers.objects.filter')
    def test_backend_rejects_backdoor_and_plaintext(self, mock_filter):
        mock_user = ResUsers(id=1, username='admin', email='admin@example.com', password_hash=self.password_hash, is_active=True)
        mock_filter.return_value.select_related.return_value.first.return_value = mock_user

        request = self.factory.post('/login/')
        for backdoor in ('admin', '123', 'admin123', 'Admin@123'):
            self.assertIsNone(self.backend.authenticate(request, username='admin', password=backdoor))
        self.assertIsNone(self.backend.authenticate(request, username='admin', password=self.password_hash))

    def test_auth_helpers_session_login_logout(self):
        mock_user = ResUsers(id=42, username='tester', email='tester@example.com', is_active=True)
        request = self.factory.get('/')
        self._add_session(request)

        login_user(request, mock_user)
        self.assertEqual(request.session.get('user_id'), 42)

        logout_user(request)
        self.assertIsNone(request.session.get('user_id'))

    @patch('authentication.views.authenticate')
    def test_login_view_post_success(self, mock_auth):
        mock_user = ResUsers(id=1, username='admin', email='admin@example.com', is_active=True)
        mock_auth.return_value = mock_user

        request = self.factory.post('/login/', {'username': 'admin', 'password': 'password'})
        self._add_session(request)
        request.user = AnonymousUser()

        response = login_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(request.session.get('user_id'), 1)

    @patch('authentication.views.authenticate')
    def test_login_open_redirect_prevented(self, mock_auth):
        mock_user = ResUsers(id=1, username='admin', email='admin@example.com', password_hash=self.password_hash, is_active=True)
        mock_auth.return_value = mock_user

        request = self.factory.post('/login/?next=https://malicious-site.com/steal', {'username': 'admin', 'password': 'ValidSecretPass123!'})
        self._add_session(request)
        request.user = AnonymousUser()

        response = login_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    @patch('authentication.views.authenticate')
    def test_login_with_default_password_forces_change(self, mock_auth):
        mock_user = ResUsers(id=1, username='admin', email='admin@example.com', password_hash=hash_password('123'), is_active=True)
        mock_auth.return_value = mock_user

        request = self.factory.post('/login/', {'username': 'admin', 'password': '123'})
        self._add_session(request)
        request.user = AnonymousUser()

        response = login_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profile/password/')
        self.assertTrue(request.session.get('force_password_change'))

    @patch('authentication.views.authenticate')
    def test_login_view_post_invalid(self, mock_auth):
        mock_auth.return_value = None

        request = self.factory.post('/login/', {'username': 'admin', 'password': 'wrong'})
        self._add_session(request)
        request.user = AnonymousUser()

        response = login_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(request.session.get('user_id'))

    @patch('authentication.views.logout_user')
    def test_logout_view(self, mock_logout):
        request = self.factory.get('/logout/')
        self._add_session(request)
        response = logout_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')
        mock_logout.assert_called_once_with(request)

    def test_home_view_unauthenticated(self):
        from base.views import home
        request = self.factory.get('/')
        self._add_session(request)
        request.user = AnonymousUser()
        response = home(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    @patch('base.models.ResUsers.objects.filter')
    def test_home_view_authenticated(self, mock_filter):
        from base.views import home
        mock_user = ResUsers(id=1, username='admin', email='admin@example.com', is_active=True)
        mock_filter.return_value.select_related.return_value.first.return_value = mock_user

        request = self.factory.get('/')
        self._add_session(request)
        login_user(request, mock_user)

        response = home(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'admin', response.content)
        self.assertIn(b'Signed in as', response.content)

    @patch('base.models.ResUsersGroups.objects.filter')
    def test_is_admin_user_role_check(self, mock_groups_filter):
        from authentication.auth_helpers import is_admin_user
        mock_groups_filter.return_value.exists.side_effect = [True, False, False]
        admin_user = ResUsers(id=1, username='admin', is_active=True)
        regular_user = ResUsers(id=2, username='johndoe', is_active=True)

        self.assertTrue(is_admin_user(admin_user))
        self.assertFalse(is_admin_user(regular_user))
        self.assertFalse(is_admin_user(None))

    @patch('base.models.ResUsers.objects.filter')
    def test_non_admin_cannot_access_settings(self, mock_filter):
        from base.views import settings_home
        mock_user = ResUsers(id=2, username='regular_user', email='user@example.com', is_active=True)
        mock_filter.return_value.select_related.return_value.first.return_value = mock_user

        request = self.factory.get('/settings/')
        self._add_session(request)
        login_user(request, mock_user)

        response = settings_home(request)
        # Regular user is redirected to home with error notice
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    @patch('base.models.ResUsers.objects.filter')
    def test_non_admin_can_save_personal_theme_to_session(self, mock_filter):
        from base.views import settings_home
        mock_user = ResUsers(id=2, username='regular_user', email='user@example.com', is_active=True)
        mock_filter.return_value.select_related.return_value.first.return_value = mock_user

        request = self.factory.post('/settings/general/', {
            'action_type': 'theme',
            'preset': 'dark_slate',
            'primary_color': '#0f766e',
            'primary_hover': '#115e59',
            'navbar_bg': '#0f172a',
            'wallpaper': 'dark_slate',
        })
        self._add_session(request)
        login_user(request, mock_user)

        response = settings_home(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('theme_settings', request.session)
        self.assertEqual(request.session['theme_settings']['preset'], 'dark_slate')
        self.assertEqual(request.session['theme_settings']['primary_color'], '#0f766e')

    @patch('base.models.ResUsers.objects.filter')
    @patch('authentication.auth_helpers.send_mail')
    def test_forgot_password_request_otp_success(self, mock_send_mail, mock_filter):
        from authentication.views import forgot_password_view
        mock_user = ResUsers(id=5, username='ajay', email='ajay@example.com', is_active=True)
        mock_filter.return_value.first.return_value = mock_user

        request = self.factory.post('/forgot-password/', {
            'action': 'request_otp',
            'identifier': 'ajay@example.com'
        })
        self._add_session(request)
        request.user = AnonymousUser()

        response = forgot_password_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_otp', request.session)
        self.assertEqual(request.session['auth_otp']['email'], 'ajay@example.com')
        self.assertEqual(request.session['auth_otp']['purpose'], 'reset')

    @patch('base.models.ResUsers.objects.filter')
    def test_forgot_password_verify_and_reset_success(self, mock_filter):
        from authentication.views import forgot_password_view
        mock_user = MagicMock()
        mock_user.id = 5
        mock_user.email = 'ajay@example.com'
        mock_user.is_active = True
        mock_filter.return_value.first.return_value = mock_user

        request = self.factory.post('/forgot-password/', {
            'action': 'verify_and_reset',
            'otp': '123456',
            'new_password': 'NewSecurePassword123!',
            'confirm_password': 'NewSecurePassword123!'
        })
        self._add_session(request)
        request.user = AnonymousUser()

        # Set valid OTP in session
        from authentication.auth_helpers import store_otp
        store_otp(request, 'ajay@example.com', '123456', purpose='reset', user_id=5)

        response = forgot_password_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')
        self.assertNotIn('auth_otp', request.session)
        mock_user.save.assert_called_once()

    @patch('base.models.ResUsers.objects.filter')
    def test_forgot_password_verify_invalid_otp(self, mock_filter):
        from authentication.views import forgot_password_view
        mock_user = MagicMock()
        mock_user.id = 5
        mock_user.email = 'ajay@example.com'
        mock_user.is_active = True
        mock_filter.return_value.first.return_value = mock_user

        request = self.factory.post('/forgot-password/', {
            'action': 'verify_and_reset',
            'otp': '999999',
            'new_password': 'NewSecurePassword123!',
            'confirm_password': 'NewSecurePassword123!'
        })
        self._add_session(request)
        request.user = AnonymousUser()

        from authentication.auth_helpers import store_otp
        store_otp(request, 'ajay@example.com', '123456', purpose='reset', user_id=5)

        response = forgot_password_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_otp', request.session)
        mock_user.save.assert_not_called()

    @patch('base.models.ResUsers.objects.filter')
    def test_change_password_with_email_otp(self, mock_filter):
        mock_user = MagicMock()
        mock_user.id = 10
        mock_user.username = 'loggeduser'
        mock_user.email = 'logged@example.com'
        mock_user.is_active = True
        mock_filter.return_value.select_related.return_value.first.return_value = mock_user

        request = self.factory.post('/profile/password/', {
            'method': 'email_otp',
            'otp': '654321',
            'new_password': 'UpdatedPass999!',
            'confirm_password': 'UpdatedPass999!'
        })
        self._add_session(request)
        login_user(request, mock_user)

        from authentication.auth_helpers import store_otp
        store_otp(request, 'logged@example.com', '654321', purpose='change', user_id=10)

        response = change_password_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profile/')
        self.assertNotIn('auth_otp', request.session)
        mock_user.save.assert_any_call(update_fields=['password_hash', 'updated_at'])



