"""
End-to-end tests of the leave approval view and the harden_accounts command against a real
(test) database.  The leave / user tables are `managed = False`, so we create them here.
"""
import unittest
from datetime import date, timedelta
from io import StringIO

from django.apps import apps
from django.conf import settings

from django.contrib.auth.hashers import identify_hasher, make_password
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.core.management import call_command
from django.db import connection
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from base.models import ResGroups, ResUsers, ResUsersGroups
from employee.models import Employee
from leave.models import LeaveRequest, LeaveType, LeaveAllocation, MandatoryDay

if not getattr(settings, 'TESTS_WITHOUT_MIGRATIONS', False):
    # Skip the whole module at import time so that plain `manage.py test` does not try to build
    # a test database (the project's migrations cannot run on an empty database).
    raise unittest.SkipTest('run with --settings=config.settings_test')


def _existing_tables():
    return set(connection.introspection.table_names())


class DbTestCase(TestCase):
    """Creates every `managed = False` table of the project apps for the duration of the class."""

    @classmethod
    def setUpClass(cls):
        cls._created = []
        project_apps = {'base', 'employee', 'leave', 'attendance', 'mail', 'authentication'}
        unmanaged = [m for m in apps.get_models()
                     if not m._meta.managed and m._meta.app_label in project_apps]
        connection.disable_constraint_checking()
        with connection.schema_editor() as editor:
            for model in unmanaged:
                if model._meta.db_table not in _existing_tables():
                    editor.create_model(model)
                    cls._created.append(model)
        connection.enable_constraint_checking()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        connection.disable_constraint_checking()
        with connection.schema_editor() as editor:
            for model in reversed(cls._created):
                editor.delete_model(model)
        connection.enable_constraint_checking()


class LeaveApprovalViewTests(DbTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.manager = Employee.objects.create(name='Mona Manager', email='mona@x.test', employee_code='E1', date_joined=date(2024, 1, 1))
        self.exec_ = Employee.objects.create(name='Eli Exec', email='eli@x.test', employee_code='E2', date_joined=date(2024, 1, 1))
        self.worker = Employee.objects.create(name='Wes Worker', email='wes@x.test', employee_code='E3', date_joined=date(2024, 1, 1),
                                              manager=self.manager, leave_approver_l1=self.manager,
                                              leave_approver_l2=self.exec_)
        self.stranger = Employee.objects.create(name='Sam Stranger', email='sam@x.test', employee_code='E4', date_joined=date(2024, 1, 1))
        self.single = LeaveType.objects.create(name='Casual', approval_type='officer')
        self.double = LeaveType.objects.create(name='Long', approval_type='both')
        d = date.today() + timedelta(days=14)
        self.req_single = LeaveRequest.objects.create(employee=self.worker, leave_type=self.single, start_date=d,
                                                      end_date=d, duration_days=1, status='confirm')
        self.req_double = LeaveRequest.objects.create(employee=self.worker, leave_type=self.double, start_date=d,
                                                      end_date=d, duration_days=1, status='confirm')

    def _act(self, req, as_emp, action, *, officer=False, admin=False, method='post'):
        from leave.views import leave_request_action
        request = getattr(self.factory, method)(f'/time-off/request/{req.id}/action/', {'action': action})
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        user = ResUsers(id=900 + as_emp.id, username=as_emp.name, email=as_emp.email, is_active=True)
        with patch('authentication.auth_helpers.get_current_ir_user', return_value=user), \
             patch('base.auth_helpers.get_current_ir_user', return_value=user), \
             patch('leave.views.get_current_ir_user', return_value=user), \
             patch('leave.views.get_user_linked_employee', return_value=as_emp), \
             patch('leave.views.is_leave_officer_or_admin', return_value=officer or admin), \
             patch('leave.views.is_admin_user', return_value=admin), \
             patch('leave.views.is_approving_manager', return_value=True):
            response = leave_request_action(request, req.id)
        req.refresh_from_db()
        return response

    def test_manager_approves_single_step_request(self):
        self._act(self.req_single, self.manager, 'validate')
        self.assertEqual(self.req_single.status, 'validate')
        self.assertEqual(self.req_single.approved_by_id, self.manager.id)

    def test_stranger_cannot_approve(self):
        self._act(self.req_single, self.stranger, 'validate')
        self.assertEqual(self.req_single.status, 'confirm')

    def test_get_request_cannot_approve(self):
        response = self._act(self.req_single, self.manager, 'validate', method='get')
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.req_single.status, 'confirm')

    def test_refused_request_cannot_be_reapproved(self):
        self._act(self.req_single, self.manager, 'refuse')
        self.assertEqual(self.req_single.status, 'refuse')
        self._act(self.req_single, self.manager, 'validate')
        self.assertEqual(self.req_single.status, 'refuse')

    def test_nobody_approves_their_own_leave(self):
        own = LeaveRequest.objects.create(employee=self.manager, leave_type=self.single,
                                          start_date=date.today() + timedelta(days=20),
                                          end_date=date.today() + timedelta(days=20), duration_days=1, status='confirm')
        self._act(own, self.manager, 'validate', admin=True)
        self.assertEqual(own.status, 'confirm')

    def test_two_level_flow_end_to_end(self):
        # step 1: manager (L1) -> still waiting, label changes
        self._act(self.req_double, self.manager, 'validate')
        self.assertEqual(self.req_double.status, 'confirm')
        self.assertEqual(self.req_double.first_approved_by_id, self.manager.id)
        self.assertEqual(self.req_double.status_label, 'Waiting Final Approval')
        # the same manager cannot also give the final approval
        self._act(self.req_double, self.manager, 'validate')
        self.assertEqual(self.req_double.status, 'confirm')
        # step 2: executive (L2) finalises
        self._act(self.req_double, self.exec_, 'validate')
        self.assertEqual(self.req_double.status, 'validate')
        self.assertEqual(self.req_double.approved_by_id, self.exec_.id)

    def test_l2_cannot_skip_step_one(self):
        self._act(self.req_double, self.exec_, 'validate')
        self.assertEqual(self.req_double.status, 'confirm')
        self.assertIsNone(self.req_double.first_approved_by_id)


class HardenAccountsCommandTests(DbTestCase):
    def test_hashes_plaintext_grandfathers_admin_and_reports_weak(self):
        ResUsers.objects.create(username='alice', email='alice@x.test', password_hash='plain-secret')
        ResUsers.objects.create(username='admin', email='boss@x.test', password_hash=make_password('Str0ng-Admin-Pass!'))
        ResUsers.objects.create(username='bob', email='bob@x.test', password_hash=make_password('123'))
        out = StringIO()
        call_command('harden_accounts', stdout=out)

        alice = ResUsers.objects.get(username='alice')
        identify_hasher(alice.password_hash)                      # no longer plaintext
        from authentication.auth_helpers import verify_password
        self.assertTrue(verify_password('plain-secret', alice.password_hash))

        admin = ResUsers.objects.get(username='admin')
        self.assertTrue(ResUsersGroups.objects.filter(user=admin, group__name='Administrator').exists())
        self.assertFalse(ResUsersGroups.objects.filter(user=alice).exists())
        self.assertIn('"bob" still uses a known default password', out.getvalue())

    def test_dry_run_changes_nothing(self):
        ResUsers.objects.create(username='alice', email='alice@x.test', password_hash='plain-secret')
        call_command('harden_accounts', '--dry-run', stdout=StringIO())
        self.assertEqual(ResUsers.objects.get(username='alice').password_hash, 'plain-secret')


class MailServerEncryptionDbTests(DbTestCase):
    def test_smtp_password_encrypted_in_db_and_decrypted_on_read(self):
        from base.models import IrMailServer
        server = IrMailServer.objects.create(name='Test SMTP', smtp_host='smtp.test', smtp_pass='hunter2')
        with connection.cursor() as cur:
            cur.execute('SELECT smtp_pass FROM ir_mail_server WHERE id = %s', [server.id])
            raw = cur.fetchone()[0]
        self.assertTrue(raw.startswith('enc1:'))
        self.assertNotIn('hunter2', raw)
        self.assertEqual(IrMailServer.objects.get(id=server.id).smtp_pass, 'hunter2')

    def test_harden_accounts_encrypts_legacy_plaintext_mail_password(self):
        from base.models import IrMailServer
        server = IrMailServer.objects.create(name='Legacy', smtp_host='smtp.test')
        with connection.cursor() as cur:
            cur.execute("UPDATE ir_mail_server SET smtp_pass = 'legacy-plain' WHERE id = %s", [server.id])
        call_command('harden_accounts', stdout=StringIO())
        with connection.cursor() as cur:
            cur.execute('SELECT smtp_pass FROM ir_mail_server WHERE id = %s', [server.id])
            self.assertTrue(cur.fetchone()[0].startswith('enc1:'))
        self.assertEqual(IrMailServer.objects.get(id=server.id).smtp_pass, 'legacy-plain')
