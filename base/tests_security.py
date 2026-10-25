"""Regression tests: batch-action authorization, export safety, debug/diagnostic leaks, media login."""
import csv
import io
import json
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from base import permissions
from base.permissions import can_batch, is_sensitive_field, spreadsheet_safe


def user(uid=5, admin=False, **extra):
    """A signed-in user.  Admin status is explicit (read from _is_admin_cached)."""
    return SimpleNamespace(id=uid, username=f'user{uid}', email=f'u{uid}@x.test', is_active=True,
                           _is_admin_cached=admin, **extra)


class FakeRecord(SimpleNamespace):
    pass


def fake_model(rows):
    fields = [
        SimpleNamespace(name='id', verbose_name='id'),
        SimpleNamespace(name='name', verbose_name='name'),
        SimpleNamespace(name='password_hash', verbose_name='password hash'),
        SimpleNamespace(name='smtp_pass', verbose_name='smtp pass'),
    ]

    class _Manager:
        def all(self_inner):
            return rows

        def filter(self_inner, **kw):
            return rows

    class FakeModel:
        _meta = SimpleNamespace(fields=fields)
        objects = _Manager()
    return FakeModel


class SensitiveFieldHelpersTests(SimpleTestCase):
    def test_sensitive_field_detection(self):
        for name in ('password_hash', 'smtp_pass', 'api_key', 'client_secret', 'auth_token'):
            self.assertTrue(is_sensitive_field(name), name)
        for name in ('name', 'email', 'username', 'pan_number'):
            self.assertFalse(is_sensitive_field(name), name)

    def test_spreadsheet_formula_injection_is_neutralised(self):
        for evil in ('=1+1', '+SUM(A1)', '-2+3', '@cmd', '=HYPERLINK("http://evil")'):
            self.assertTrue(spreadsheet_safe(evil).startswith("'"), evil)
        self.assertEqual(spreadsheet_safe('Alice'), 'Alice')
        self.assertEqual(spreadsheet_safe(None), '')
        self.assertEqual(spreadsheet_safe(42), '42')


class CanBatchMatrixTests(SimpleTestCase):
    """Fix #1: who may run which batch action on which model."""

    def test_admin_can_do_everything(self):
        admin = user(1, admin=True)
        for model in ('res.users', 'ir.mail_server', 'hr.employee', 'anything'):
            for action in ('export', 'import', 'duplicate', 'archive', 'unarchive', 'delete'):
                self.assertTrue(can_batch(admin, model, action), (model, action))

    def test_regular_user_is_blocked_everywhere_sensitive(self):
        u = user()
        sensitive = ('res.users', 'res.users.groups', 'res.groups', 'res.privilege', 'ir.mail_server',
                     'ir.config_parameter', 'ir.rule', 'ir.model.access', 'ir.cron', 'ir.logging')
        with patch('base.permissions.is_hr_officer_or_admin', return_value=True), \
             patch('base.permissions.is_leave_officer_or_admin', return_value=True), \
             patch('base.permissions.is_attendance_officer_or_admin', return_value=True):
            # even module officers can never touch the sensitive/technical models
            for model in sensitive:
                for action in ('export', 'import', 'duplicate', 'archive', 'unarchive', 'delete'):
                    self.assertFalse(can_batch(u, model, action), (model, action))

    def test_module_officers_only_for_their_module(self):
        u = user()
        with patch('base.permissions.is_hr_officer_or_admin', return_value=True), \
             patch('base.permissions.is_leave_officer_or_admin', return_value=False), \
             patch('base.permissions.is_attendance_officer_or_admin', return_value=False):
            self.assertTrue(can_batch(u, 'hr.employee', 'export'))
            self.assertFalse(can_batch(u, 'hr.leave', 'export'))
            self.assertFalse(can_batch(u, 'hr.attendance', 'export'))

    def test_plain_employee_cannot_export_employees(self):
        with patch('base.permissions.is_hr_officer_or_admin', return_value=False):
            self.assertFalse(can_batch(user(), 'hr.employee', 'export'))

    def test_other_models_follow_ir_model_access(self):
        u = user()
        with patch('base.permissions._ir_model_access_allows', return_value=True) as allowed:
            self.assertTrue(can_batch(u, 'res.partner', 'export'))
            allowed.assert_called_with(u, 'res.partner', 'export')
        with patch('base.permissions._ir_model_access_allows', return_value=False):
            self.assertFalse(can_batch(u, 'res.partner', 'export'))

    def test_inactive_or_missing_user_and_unknown_action(self):
        self.assertFalse(can_batch(None, 'res.partner', 'export'))
        self.assertFalse(can_batch(SimpleNamespace(is_active=False, _is_admin_cached=True), 'x', 'export'))
        self.assertFalse(can_batch(user(1, admin=True), 'x', 'drop_table'))


class BatchActionViewSecurityTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _call(self, request, current_user, model_map=None):
        from base.views import batch_action
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        with patch('base.views.get_current_ir_user', return_value=current_user), \
             patch.dict('base.views.MODEL_CLASS_MAP', model_map or {}):
            return batch_action(request)

    def test_regular_user_cannot_export_mail_server_credentials(self):
        model = fake_model([FakeRecord(id=1, name='SMTP', password_hash='h', smtp_pass='hunter2')])
        request = self.factory.get('/batch-action/?action=export_csv&model_key=ir.mail_server')
        response = self._call(request, user(), {'ir.mail_server': model})
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(b'hunter2', response.content)

    def test_regular_user_cannot_export_users_or_employees(self):
        for key in ('res.users', 'hr.employee'):
            model = fake_model([FakeRecord(id=1, name='x', password_hash='h', smtp_pass='')])
            request = self.factory.get(f'/batch-action/?action=export_xlsx&model_key={key}')
            with patch('base.permissions.is_hr_officer_or_admin', return_value=False):
                response = self._call(request, user(), {key: model})
            self.assertEqual(response.status_code, 403, key)

    def test_regular_user_cannot_import_into_group_membership_to_become_admin(self):
        """The privilege-escalation path: importing rows into res.users.groups / res.users."""
        for key in ('res.users.groups', 'res.users', 'ir.model.access', 'ir.rule'):
            upload = SimpleUploadedFile('x.csv', b'user,group\n5,1\n', content_type='text/csv')
            request = self.factory.post('/batch-action/', {'action': 'import_records', 'model_key': key,
                                                           'has_header': 'true', 'import_file': upload})
            model = fake_model([])
            model.objects.create = lambda **kw: self.fail('a record was created by a non-admin!')
            response = self._call(request, user(), {key: model})
            self.assertEqual(response.status_code, 403, key)

    def test_regular_user_cannot_archive_unarchive_duplicate_or_delete(self):
        for action in ('archive', 'unarchive', 'duplicate', 'delete'):
            request = self.factory.post('/batch-action/', {'action': action, 'model_key': 'res.users', 'ids': ['1']})
            response = self._call(request, user(), {'res.users': fake_model([])})
            self.assertEqual(response.status_code, 403, action)

    def test_unauthenticated_gets_401(self):
        request = self.factory.get('/batch-action/?action=export_csv&model_key=res.users')
        self.assertEqual(self._call(request, None).status_code, 401)

    def test_admin_export_never_contains_password_or_smtp_columns(self):
        rec = FakeRecord(id=1, name='=cmd|calc', password_hash='pbkdf2$secret', smtp_pass='hunter2')
        model = fake_model([rec])
        request = self.factory.get('/batch-action/?action=export_csv&model_key=fake.model')
        with patch('base.permissions.is_admin_user', return_value=True):
            response = self._call(request, user(1, admin=True), {'fake.model': model})
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertNotIn('hunter2', body)
        self.assertNotIn('pbkdf2$secret', body)
        rows = list(csv.reader(io.StringIO(body)))
        self.assertNotIn('Password Hash', rows[0])
        self.assertNotIn('Smtp Pass', rows[0])
        self.assertTrue(rows[1][1].startswith("'="), 'formula must be neutralised in the export')

    def test_officer_can_export_their_own_module(self):
        model = fake_model([FakeRecord(id=1, name='Asha', password_hash='', smtp_pass='')])
        request = self.factory.get('/batch-action/?action=export_csv&model_key=hr.employee')
        with patch('base.permissions.is_hr_officer_or_admin', return_value=True):
            response = self._call(request, user(), {'hr.employee': model})
        self.assertEqual(response.status_code, 200)

    def test_import_size_limit(self):
        big = SimpleUploadedFile('x.csv', b'a' * (permissions.MAX_IMPORT_BYTES + 1), content_type='text/csv')
        request = self.factory.post('/batch-action/', {'action': 'import_records', 'model_key': 'fake.model',
                                                       'import_file': big})
        with patch('base.permissions.is_admin_user', return_value=True):
            response = self._call(request, user(1, admin=True), {'fake.model': fake_model([])})
        self.assertEqual(response.status_code, 400)


class DiagnosticLeakTests(SimpleTestCase):
    """Fix #7: no stack traces / file paths for normal users, in production."""

    def setUp(self):
        self.factory = RequestFactory()

    def _session(self, request, debug=False):
        request.session = SessionStore()
        if debug:
            request.session['debug'] = True
        return request

    @override_settings(DEBUG=False)
    @patch('base.models.IrLogging.log_exception')
    def test_ajax_error_has_no_traceback_or_paths_in_production(self, _log):
        from base.middleware import GlobalExceptionDiagnosticMiddleware
        mw = GlobalExceptionDiagnosticMiddleware(lambda r: None)
        request = self._session(self.factory.get('/x/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'))
        try:
            raise ValueError('secret internals /srv/app/base/views.py')
        except Exception as exc:
            response = mw.process_exception(request, exc)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 500)
        for leaked in ('traceback', 'file', 'line', 'function', 'error_type'):
            self.assertNotIn(leaked, data)
        self.assertNotIn('secret internals', response.content.decode())

    @override_settings(DEBUG=False)
    @patch('base.middleware._session_user_is_admin', return_value=False)
    @patch('base.models.IrLogging.log_exception')
    def test_session_debug_flag_alone_is_not_enough(self, _log, _admin):
        from base.middleware import GlobalExceptionDiagnosticMiddleware
        mw = GlobalExceptionDiagnosticMiddleware(lambda r: None)
        request = self._session(self.factory.get('/x/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'), debug=True)
        try:
            raise ValueError('boom')
        except Exception as exc:
            response = mw.process_exception(request, exc)
        self.assertNotIn('traceback', json.loads(response.content))

    @override_settings(DEBUG=False)
    @patch('base.middleware._session_user_is_admin', return_value=True)
    @patch('base.models.IrLogging.log_exception')
    def test_admin_in_developer_mode_still_gets_details(self, _log, _admin):
        from base.middleware import GlobalExceptionDiagnosticMiddleware
        mw = GlobalExceptionDiagnosticMiddleware(lambda r: None)
        request = self._session(self.factory.get('/x/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'), debug=True)
        try:
            raise ValueError('boom')
        except Exception as exc:
            response = mw.process_exception(request, exc)
        self.assertIn('traceback', json.loads(response.content))

    @override_settings(DEBUG=False)
    @patch('base.models.IrLogging.log_exception')
    @patch('base.middleware.render')
    def test_html_500_page_hides_diagnostics_in_production(self, mock_render, _log):
        from base.middleware import GlobalExceptionDiagnosticMiddleware
        mw = GlobalExceptionDiagnosticMiddleware(lambda r: None)
        request = self._session(self.factory.get('/page/'))
        try:
            raise TypeError('boom')
        except Exception as exc:
            mw.process_exception(request, exc)
        context = mock_render.call_args[0][2]
        self.assertFalse(context['diag'])
        self.assertFalse(context['is_debug'])
        self.assertIsNone(context['exception'])

    @override_settings(DEBUG=False)
    @patch('base.views.render')
    def test_handler500_hides_diagnostics_in_production(self, mock_render):
        from base.views import error_500_view
        request = self._session(self.factory.get('/page/'))
        try:
            raise TypeError('boom')
        except Exception:
            error_500_view(request)
        self.assertIsNone(mock_render.call_args[0][2]['diag'])


class LoginEnforcementTests(SimpleTestCase):
    """Fix #8: /media/ no longer public; ?next= is URL-encoded."""

    def setUp(self):
        self.factory = RequestFactory()

    def _run(self, path):
        from base.middleware import EnforceLoginMiddleware
        mw = EnforceLoginMiddleware(lambda r: HttpResponse('OK'))
        request = self.factory.get(path)
        request.session = SessionStore()
        with patch('base.auth_helpers.get_current_ir_user', return_value=None):
            return mw(request)

    def test_media_requires_login(self):
        response = self._run('/media/employee/avatar.png')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/?next='))

    def test_static_login_and_health_remain_public(self):
        for path in ('/static/base/css/layout.css', '/login/', '/healthz/', '/forgot-password/'):
            self.assertEqual(self._run(path).status_code, 200, path)

    def test_next_parameter_is_encoded(self):
        response = self._run('/time-off/?a=1&b=2')
        self.assertIn('%3Fa%3D1%26b%3D2', response.url)
        self.assertNotIn('&b=2', response.url)


class EncryptedFieldTests(SimpleTestCase):
    """SMTP password is encrypted at rest."""

    def test_roundtrip_and_ciphertext_differs(self):
        from base.fields import EncryptedCharField, PREFIX
        f = EncryptedCharField(max_length=512)
        stored = f.get_prep_value('hunter2-app-password')
        self.assertTrue(stored.startswith(PREFIX))
        self.assertNotIn('hunter2', stored)
        self.assertEqual(f.from_db_value(stored, None, None), 'hunter2-app-password')

    def test_not_double_encrypted(self):
        from base.fields import EncryptedCharField
        f = EncryptedCharField(max_length=512)
        once = f.get_prep_value('secret')
        self.assertEqual(f.get_prep_value(once), once)

    def test_legacy_plaintext_still_readable(self):
        from base.fields import EncryptedCharField
        self.assertEqual(EncryptedCharField(max_length=512).from_db_value('old-plain', None, None), 'old-plain')

    def test_empty_and_none_untouched(self):
        from base.fields import EncryptedCharField
        f = EncryptedCharField(max_length=512)
        self.assertIsNone(f.get_prep_value(None))
        self.assertEqual(f.get_prep_value(''), '')

    def test_wrong_key_reads_back_empty_instead_of_crashing(self):
        from base.fields import EncryptedCharField
        f = EncryptedCharField(max_length=512)
        stored = f.get_prep_value('secret')
        with patch.dict('os.environ', {'FIELD_ENCRYPTION_KEY': 'Zm9v' * 8 + '='}):
            from cryptography.fernet import Fernet
            key = Fernet.generate_key().decode()
            with patch.dict('os.environ', {'FIELD_ENCRYPTION_KEY': key}):
                self.assertEqual(f.from_db_value(stored, None, None), '')

    def test_longest_expected_password_fits_column(self):
        from base.fields import EncryptedCharField
        self.assertLess(len(EncryptedCharField(max_length=512).get_prep_value('p' * 150)), 512)
