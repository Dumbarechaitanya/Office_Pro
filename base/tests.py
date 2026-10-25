import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from django.test import RequestFactory, SimpleTestCase
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage

from base.views import technical_menu_items


class TechnicalMenuItemsViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.views.IrUiMenu.objects.filter')
    @patch('base.views.render')
    def test_technical_menu_items_includes_toolbar_context(self, mock_render, mock_filter, mock_get_user):
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user
        menu_a = SimpleNamespace(name='Settings', parent=None, sequence=10)
        menu_b = SimpleNamespace(name='Users', parent=menu_a, sequence=20)
        mock_filter.return_value.order_by.return_value = [menu_a, menu_b]

        request = self.factory.get('/settings/technical/menu-items/', {'q': 'user'})
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        technical_menu_items(request)

        mock_render.assert_called_once()
        _, _, context = mock_render.call_args[0]
        self.assertEqual(context['total_count'], 2)
        self.assertEqual(context['create_url'], '#')
        self.assertEqual(len(context['menu_list']), 2)


class BatchActionsViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('base.views.get_current_ir_user')
    @patch('base.models.ResUsers.objects.filter')
    def test_batch_action_export_csv(self, mock_filter, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user

        u1 = SimpleNamespace(id=1, username='u1', email='u1@test.com', is_active=True)
        u2 = SimpleNamespace(id=2, username='u2', email='u2@test.com', is_active=True)
        mock_filter.return_value = [u1, u2]

        request = self.factory.get('/batch-action/?action=export_csv&model_key=res.users&ids=1,2')
        response = batch_action(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('res_users_export.csv', response['Content-Disposition'])

    @patch('base.views.get_current_ir_user')
    @patch('base.models.ResUsers.objects.filter')
    def test_batch_action_export_xlsx(self, mock_filter, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user

        u1 = SimpleNamespace(id=1, username='u1', email='u1@test.com', is_active=True)
        mock_filter.return_value = [u1]

        request = self.factory.get('/batch-action/?action=export_xlsx&model_key=res.users&ids=1')
        response = batch_action(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('res_users_export.xlsx', response['Content-Disposition'])

    @patch('base.views.get_current_ir_user')
    @patch('base.models.ResUsers.objects.filter')
    def test_batch_action_archive_and_unarchive(self, mock_filter, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user

        # Archive
        request = self.factory.post('/batch-action/', {'action': 'archive', 'model_key': 'res.users', 'ids': ['1', '2']})
        response = batch_action(request)
        self.assertEqual(response.status_code, 200)
        mock_filter.return_value.update.assert_called_with(is_active=False)

        # Unarchive
        request = self.factory.post('/batch-action/', {'action': 'unarchive', 'model_key': 'res.users', 'ids': ['1', '2']})
        response = batch_action(request)
        self.assertEqual(response.status_code, 200)
        mock_filter.return_value.update.assert_called_with(is_active=True)

    @patch('base.views.get_current_ir_user')
    @patch('base.views.user_can_delete_model')
    def test_batch_action_delete_permission_denied_for_level1_user(self, mock_can_delete, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=5, username='lvl1_user', is_active=True, is_admin=False)
        mock_get_user.return_value = mock_user
        mock_can_delete.return_value = False  # Level 1 role without delete rights

        request = self.factory.post('/batch-action/', {'action': 'delete', 'model_key': 'res.users', 'ids': ['1']})
        response = batch_action(request)

        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Permission Denied', response.content)

    @patch('base.views.get_current_ir_user')
    @patch('base.module_manager.delete_user_safely')
    @patch('base.views.user_can_delete_model')
    def test_batch_action_delete_allowed_for_admin(self, mock_can_delete, mock_delete_user, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user
        mock_can_delete.return_value = True
        mock_delete_user.return_value = (True, "User deleted.")

        request = self.factory.post('/batch-action/', {'action': 'delete', 'model_key': 'res.users', 'ids': ['2']})
        response = batch_action(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'deleted successfully', response.content)

    @patch('base.views.get_current_ir_user')
    @patch('base.models.ResUsers.objects.all')
    def test_batch_action_export_all(self, mock_all, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user

        u1 = SimpleNamespace(id=1, username='u1', email='u1@test.com', is_active=True)
        mock_all.return_value = [u1]

        request = self.factory.get('/batch-action/?action=export_csv&model_key=res.users')
        response = batch_action(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        mock_all.assert_called_once()

    @patch('base.views.get_current_ir_user')
    @patch('base.models.ResUsers.objects.create')
    def test_batch_action_import_csv(self, mock_create, mock_get_user):
        from base.views import batch_action
        from django.core.files.uploadedfile import SimpleUploadedFile
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user

        csv_content = b"username,email\nimported_user,imported@test.com\n"
        uploaded_file = SimpleUploadedFile("users.csv", csv_content, content_type="text/csv")

        request = self.factory.post('/batch-action/', {
            'action': 'import_records',
            'model_key': 'res.users',
            'has_header': 'true',
            'import_file': uploaded_file
        })
        response = batch_action(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'imported successfully', response.content)
        mock_create.assert_called_once_with(username='imported_user', email='imported@test.com')

    @patch('base.views.get_current_ir_user')
    def test_batch_action_export_denied_for_non_admin_on_system_models(self, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=99, username='standard_user', is_active=True, is_admin=False)
        mock_get_user.return_value = mock_user

        request = self.factory.get('/batch-action/?action=export_csv&model_key=res.users&ids=1')
        response = batch_action(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Administrator role required', response.content)

    @patch('base.views.get_current_ir_user')
    def test_batch_action_import_denied_for_non_admin(self, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=99, username='standard_user', is_active=True, is_admin=False)
        mock_get_user.return_value = mock_user

        request = self.factory.post('/batch-action/', {'action': 'import_records', 'model_key': 'res.users'})
        response = batch_action(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Permission Denied', response.content)

    @patch('base.views.get_current_ir_user')
    def test_batch_action_unauthorized_model_denied(self, mock_get_user):
        from base.views import batch_action
        mock_user = SimpleNamespace(id=99, username='standard_user', is_active=True, is_admin=False)
        mock_get_user.return_value = mock_user

        request = self.factory.get('/batch-action/?action=export_csv&model_key=dangerous.model&ids=1')
        response = batch_action(request)
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'not permitted', response.content)


class DebugModeMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_debug_mode_activation(self):
        from base.middleware import DebugModeMiddleware, SERVER_BOOT_ID
        from django.http import HttpResponse

        middleware = DebugModeMiddleware(lambda req: HttpResponse('OK'))
        request = self.factory.get('/settings/users/?debug=1')
        request.session = SessionStore()

        response = middleware(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(request.session.get('debug'))
        self.assertEqual(request.session.get('server_boot_id'), SERVER_BOOT_ID)

    def test_debug_mode_persists_in_path_across_page_navigation(self):
        from base.middleware import DebugModeMiddleware, SERVER_BOOT_ID
        from django.http import HttpResponse

        middleware = DebugModeMiddleware(lambda req: HttpResponse('OK'))
        request = self.factory.get('/settings/users/')
        request.session = SessionStore()
        request.session['debug'] = True
        request.session['server_boot_id'] = SERVER_BOOT_ID

        response = middleware(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings/users/?debug=1')

    def test_debug_mode_deactivation_redirects_to_clean_url(self):
        from base.middleware import DebugModeMiddleware, SERVER_BOOT_ID
        from django.http import HttpResponse

        middleware = DebugModeMiddleware(lambda req: HttpResponse('OK'))
        request = self.factory.get('/settings/users/?debug=0')
        request.session = SessionStore()
        request.session['debug'] = True
        request.session['server_boot_id'] = SERVER_BOOT_ID

        response = middleware(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings/users/')
        self.assertFalse(request.session.get('debug'))

    def test_debug_mode_resets_on_server_reboot(self):
        from base.middleware import DebugModeMiddleware
        from django.http import HttpResponse

        middleware = DebugModeMiddleware(lambda req: HttpResponse('OK'))
        request = self.factory.get('/settings/users/')
        request.session = SessionStore()
        request.session['debug'] = True
        request.session['server_boot_id'] = 'old_reboot_uuid_123'  # Prior server run

        response = middleware(request)
        # Should not redirect to ?debug=1 because server rebooted, so debug mode was reset
        self.assertEqual(response.status_code, 200)
        self.assertFalse(request.session.get('debug'))


class PrivilegesAndCompaniesTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _add_session(self, request, is_admin=True):
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=is_admin)
        return request, user

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.views.ensure_default_privileges')
    @patch('base.models.ResPrivilege.objects.filter')
    def test_privileges_list_view(self, mock_filter, mock_ensure, mock_get_user):
        from base.views import settings_privileges
        request, user = self._add_session(self.factory.get('/settings/privileges/'))
        mock_get_user.return_value = user

        p1 = SimpleNamespace(id=1, name='Sales', sequence=10, groups=SimpleNamespace(all=lambda: []))
        p2 = SimpleNamespace(id=2, name='Office', sequence=70, groups=SimpleNamespace(all=lambda: []))
        mock_filter.return_value.prefetch_related.return_value.order_by.return_value = [p1, p2]

        response = settings_privileges(request)
        self.assertEqual(response.status_code, 200)
        mock_ensure.assert_called_once()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.ResPrivilege.objects.create')
    def test_privilege_create_post(self, mock_create, mock_get_user):
        from base.views import settings_privilege_create
        request, user = self._add_session(self.factory.post('/settings/privileges/new/', {
            'name': 'Custom Privilege',
            'sequence': '15',
            'is_placeholder': 'false',
            'notes': 'Custom notes'
        }))
        mock_get_user.return_value = user
        mock_create.return_value = SimpleNamespace(id=99, name='Custom Privilege')

        response = settings_privilege_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings/privileges/99/')
        mock_create.assert_called_once()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.ResCompany.objects.filter')
    def test_companies_list_view(self, mock_filter, mock_get_user):
        from base.views import settings_companies
        request, user = self._add_session(self.factory.get('/settings/companies/'))
        mock_get_user.return_value = user

        c1 = SimpleNamespace(id=1, name='Main HQ', partner=None, branches_count=2, color='#714b67')
        mock_filter.return_value.select_related.return_value.prefetch_related.return_value.order_by.return_value = [c1]

        response = settings_companies(request)
        self.assertEqual(response.status_code, 200)

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.ResCompany.objects.create')
    @patch('base.models.MailMessage.objects.create')
    def test_company_create_post(self, mock_mail_create, mock_comp_create, mock_get_user):
        from base.views import settings_company_create
        request, user = self._add_session(self.factory.post('/settings/companies/new/', {
            'name': 'Office Pro Solutions Ltd',
            'street': 'Main Street 1',
            'city': 'Mumbai',
            'country': 'India',
            'currency': 'INR',
            'phone': '+91 9876543210',
            'email': 'info@officepro.internal',
            'color': '#714b67'
        }))
        mock_get_user.return_value = user
        mock_comp_create.return_value = SimpleNamespace(id=50, name='Office Pro Solutions Ltd')

        response = settings_company_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings/companies/50/')
        mock_comp_create.assert_called_once()
        mock_mail_create.assert_called_once()

    @patch('base.views.get_current_ir_user')
    @patch('base.models.MailMessage.objects.create')
    def test_mail_post_message_api(self, mock_mail_create, mock_get_user):
        import json
        from django.utils import timezone
        from base.views import mail_post_message
        request, user = self._add_session(self.factory.post('/mail/post-message/', {
            'model_name': 'res.company',
            'record_id': '1',
            'message_type': 'note',
            'body': 'Audit check completed'
        }))
        mock_get_user.return_value = user
        mock_msg = SimpleNamespace(
            id=101,
            author=user,
            message_type='note',
            body='Audit check completed',
            created_at=timezone.now()
        )
        mock_mail_create.return_value = mock_msg

        response = mail_post_message(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message']['body'], 'Audit check completed')


class PaperFormatsAndReportsTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _add_session(self, request, is_admin=True):
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=is_admin)
        return request, user

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.IrModel.objects.filter')
    @patch('base.views.ensure_default_paperformats')
    @patch('base.models.ReportPaperformat.objects.filter')
    def test_paperformats_list_view(self, mock_filter, mock_ensure, mock_model_filter, mock_get_user):
        from base.views import technical_paperformats
        request, user = self._add_session(self.factory.get('/settings/technical/paper-formats/'))
        mock_get_user.return_value = user
        mock_model_filter.return_value.first.return_value = None

        pf1 = SimpleNamespace(id=1, name='A4', format_size='A4', orientation='Portrait', margin_top=52.0, margin_bottom=32.0, margin_left=0.0, margin_right=0.0, dpi=90, get_format_size_display=lambda: 'A4')
        mock_filter.return_value.order_by.return_value = [pf1]

        response = technical_paperformats(request)
        self.assertEqual(response.status_code, 200)
        mock_ensure.assert_called_once()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.ReportPaperformat.objects.create')
    def test_paperformat_create_post(self, mock_create, mock_get_user):
        from base.views import technical_paperformat_create
        request, user = self._add_session(self.factory.post('/settings/technical/paper-formats/new/', {
            'name': 'Custom Format',
            'format_size': 'A4',
            'orientation': 'Portrait',
            'margin_top': '50.00',
            'margin_bottom': '30.00',
            'margin_left': '5.00',
            'margin_right': '5.00',
            'header_spacing': '40',
            'dpi': '90',
        }))
        mock_get_user.return_value = user
        mock_create.return_value = SimpleNamespace(id=12, name='Custom Format')

        response = technical_paperformat_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings/technical/paper-formats/12/')
        mock_create.assert_called_once()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.IrModel.objects.filter')
    @patch('base.views.ensure_default_paperformats')
    @patch('base.models.IrActionsReport.objects.filter')
    def test_reports_list_view(self, mock_filter, mock_ensure, mock_model_filter, mock_get_user):
        from base.views import technical_reports
        request, user = self._add_session(self.factory.get('/settings/technical/reports/'))
        mock_get_user.return_value = user
        mock_model_filter.return_value.first.return_value = None

        r1 = SimpleNamespace(id=1, name='Invoices', report_type='qweb-pdf', model=SimpleNamespace(description='Invoices', model_name='account.move'), paperformat=SimpleNamespace(name='A4'), report_name='account.report_invoice', report_file='account.report_invoice', get_report_type_display=lambda: 'PDF')
        mock_filter.return_value.select_related.return_value.order_by.return_value = [r1]

        response = technical_reports(request)
        self.assertEqual(response.status_code, 200)
        mock_ensure.assert_called_once()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.IrModel.objects.filter')
    @patch('base.models.ReportPaperformat.objects.filter')
    @patch('base.models.ResGroups.objects.filter')
    def test_report_create_validation_missing_fields(self, mock_groups, mock_paperformats, mock_models, mock_get_user):
        from base.views import technical_report_create
        request, user = self._add_session(self.factory.post('/settings/technical/reports/new/', {
            'name': '',
            'model': '',
            'report_name': '',
        }))
        mock_get_user.return_value = user
        mock_models.return_value.order_by.return_value = []
        mock_paperformats.return_value.order_by.return_value = []
        mock_groups.return_value.order_by.return_value = []

        response = technical_report_create(request)
        self.assertEqual(response.status_code, 200)

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.IrActionsReport.objects.create')
    @patch('base.models.IrModel.objects.filter')
    @patch('base.models.ReportPaperformat.objects.filter')
    @patch('base.models.ResGroups.objects.filter')
    def test_report_create_post_success(self, mock_groups, mock_paperformats, mock_models, mock_create, mock_get_user):
        from base.views import technical_report_create
        request, user = self._add_session(self.factory.post('/settings/technical/reports/new/', {
            'name': 'Invoice Report',
            'model': '5',
            'report_name': 'account.report_invoice',
            'report_type': 'qweb-pdf',
            'paperformat': '1',
        }))
        mock_get_user.return_value = user
        created_rep = SimpleNamespace(id=25, name='Invoice Report', groups=SimpleNamespace(set=lambda x: None))
        mock_create.return_value = created_rep

        response = technical_report_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings/technical/reports/25/')
        mock_create.assert_called_once()


class MailTopbarPopoversAndActivitiesTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _add_session(self, request, is_admin=True, user_id=1, username='admin'):
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        user = SimpleNamespace(
            id=user_id,
            username=username,
            name=username.capitalize(),
            email=f'{username}@example.com',
            is_active=True,
            is_admin=is_admin,
            role='Administrator' if is_admin else 'User'
        )
        return request, user

    @patch('base.views.seed_sample_activities_and_notifications')
    @patch('base.views.ResUsers.objects.filter')
    @patch('base.views.MailMessage.objects.exclude')
    @patch('base.views.MailMessage.objects.filter')
    @patch('base.views.get_current_ir_user')
    def test_mail_conversations_endpoint(self, mock_get_user, mock_msg_filter, mock_msg_exclude, mock_users_filter, mock_seed):
        from base.views import mail_conversations
        from datetime import datetime
        request, user = self._add_session(self.factory.get('/mail/conversations/'))
        mock_get_user.return_value = user

        # unread count
        mock_msg_filter.return_value.count.return_value = 2

        # inbox messages
        msg1 = SimpleNamespace(
            id=10, author_id=2, author=SimpleNamespace(username='marcdemo'),
            recipient=user, channel=None, subject='Hello', body='Welcome to Office Pro',
            message_type='comment', is_read=False, model_name='res.users', record_id=1,
            created_at=datetime(2026, 9, 5, 12, 0, 0)
        )
        mock_msg_filter.return_value.select_related.return_value.order_by.return_value = [msg1]

        # chatter stream
        cmsg = SimpleNamespace(
            id=11, author=SimpleNamespace(username='admin'),
            model_name='res.company', record_id=1, message_type='note',
            body='Updated company tax registration ID',
            created_at=datetime(2026, 9, 5, 12, 30, 0)
        )
        mock_msg_exclude.return_value.select_related.return_value.order_by.return_value = [cmsg]

        # users list
        u2 = SimpleNamespace(id=2, username='marcdemo', name='Marc Demo', email='marc@demo.com', role='User', is_active=True)
        mock_users_filter.return_value.exclude.return_value.order_by.return_value = [u2]

        response = mail_conversations(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['unread_count'], 2)
        self.assertEqual(len(data['inbox']), 1)
        self.assertEqual(len(data['chatter_stream']), 1)
        self.assertEqual(len(data['users']), 1)

    @patch('base.views.ResUsers.objects.filter')
    @patch('base.views.MailMessage.objects.create')
    @patch('base.views.get_current_ir_user')
    def test_mail_send_direct_message(self, mock_get_user, mock_create, mock_users_filter):
        from base.views import mail_send_direct_message
        from datetime import datetime
        request, user = self._add_session(self.factory.post('/mail/direct-message/send/', {
            'recipient_id': '2',
            'body': 'Meeting at 3 PM today',
            'subject': 'Daily Sync'
        }))
        mock_get_user.return_value = user
        rec_user = SimpleNamespace(id=2, username='marcdemo', is_active=True)
        mock_users_filter.return_value.first.return_value = rec_user

        created_msg = SimpleNamespace(
            id=50, author=user, recipient=rec_user,
            subject='Daily Sync', body='Meeting at 3 PM today',
            created_at=datetime(2026, 9, 5, 14, 0, 0)
        )
        mock_create.return_value = created_msg

        response = mail_send_direct_message(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message']['author_name'], 'admin')
        self.assertEqual(data['message']['recipient_name'], 'marcdemo')
        mock_create.assert_called_once()

    @patch('base.views.MailMessage.objects.filter')
    @patch('base.views.get_current_ir_user')
    def test_mail_mark_message_read(self, mock_get_user, mock_msg_filter):
        from base.views import mail_mark_message_read
        request, user = self._add_session(self.factory.post('/mail/messages/10/mark-read/'))
        mock_get_user.return_value = user
        msg_obj = SimpleNamespace(id=10, is_read=False, save=lambda update_fields: None)
        mock_msg_filter.return_value.first.return_value = msg_obj
        mock_msg_filter.return_value.count.return_value = 0

        response = mail_mark_message_read(request, 10)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['unread_count'], 0)

    @patch('base.views.MailActivityType.objects.get')
    @patch('base.views.ResUsers.objects.get')
    @patch('base.views.MailActivity.objects.create')
    @patch('base.views.MailMessage.objects.create')
    @patch('base.views.get_current_ir_user')
    def test_mail_activity_create(self, mock_get_user, mock_msg_create, mock_act_create, mock_user_get, mock_type_get):
        from base.views import mail_activity_create
        request, user = self._add_session(self.factory.post('/mail/activities/create/', {
            'activity_type_id': '1',
            'summary': 'Call vendor regarding quote',
            'date_deadline': '2026-09-10',
            'user_id': '1',
            'res_model': 'res.company',
            'res_id': '1',
            'res_name': 'My Company',
            'note': 'Negotiate discount terms',
        }))
        mock_get_user.return_value = user
        act_type = SimpleNamespace(id=1, name='Phone Call', icon='📞')
        mock_type_get.return_value = act_type
        mock_user_get.return_value = user
        created_act = SimpleNamespace(id=77)
        mock_act_create.return_value = created_act

        response = mail_activity_create(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['activity_id'], 77)
        mock_act_create.assert_called_once()
        mock_msg_create.assert_called_once()

    @patch('base.views.MailActivity.objects.get')
    @patch('base.views.MailMessage.objects.create')
    @patch('base.views.get_current_ir_user')
    def test_mail_activity_done(self, mock_get_user, mock_msg_create, mock_act_get):
        from base.views import mail_activity_done
        request, user = self._add_session(self.factory.post('/mail/activities/77/done/', {
            'feedback': 'Completed the call, 10% discount approved.'
        }))
        mock_get_user.return_value = user
        act_obj = SimpleNamespace(
            id=77, summary='Call vendor',
            activity_type=SimpleNamespace(name='Phone Call', icon='📞'),
            res_model='res.company', res_id=1,
            state='planned', feedback=None, done_date=None,
            save=lambda update_fields: None
        )
        mock_act_get.return_value = act_obj

        response = mail_activity_done(request, 77)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(act_obj.state, 'done')
        self.assertEqual(act_obj.feedback, 'Completed the call, 10% discount approved.')
        mock_msg_create.assert_called_once()

    @patch('base.views.MailActivity.objects.get')
    @patch('base.views.MailMessage.objects.create')
    @patch('base.views.get_current_ir_user')
    def test_mail_activity_cancel(self, mock_get_user, mock_msg_create, mock_act_get):
        from base.views import mail_activity_cancel
        request, user = self._add_session(self.factory.post('/mail/activities/77/cancel/'))
        mock_get_user.return_value = user
        act_obj = SimpleNamespace(
            id=77, summary='Call vendor',
            activity_type=SimpleNamespace(name='Phone Call', icon='📞'),
            res_model='res.company', res_id=1,
            state='planned',
            save=lambda update_fields: None
        )
        mock_act_get.return_value = act_obj

        response = mail_activity_cancel(request, 77)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(act_obj.state, 'cancelled')
        mock_msg_create.assert_called_once()

    @patch('base.views.ensure_default_activity_types')
    @patch('base.views.MailActivityType.objects.filter')
    def test_mail_activity_types(self, mock_type_filter, mock_ensure):
        from base.views import mail_activity_types
        request = self.factory.get('/mail/activities/types/')
        t1 = SimpleNamespace(id=1, name='Email', icon='📧', default_next_days=1)
        t2 = SimpleNamespace(id=2, name='To-Do', icon='📝', default_next_days=0)
        mock_type_filter.return_value.order_by.return_value = [t1, t2]

        response = mail_activity_types(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['activity_types']), 2)

    def test_mail_activity_model_properties_and_str(self):
        from datetime import date, timedelta
        from base.models import MailActivity, MailActivityType, MailChannel

        act_type = MailActivityType(name='Phone Call', icon='📞')
        self.assertEqual(str(act_type), '📞 Phone Call')

        channel = MailChannel(name='General Discussion', channel_type='channel')
        self.assertEqual(str(channel), 'General Discussion')

        today = date.today()
        # Overdue activity
        act_overdue = MailActivity(
            activity_type=act_type,
            summary='Call client',
            date_deadline=today - timedelta(days=3),
            state='planned',
            res_model='res.company',
            res_id=5
        )
        self.assertTrue(act_overdue.is_overdue)
        self.assertFalse(act_overdue.is_today)
        self.assertFalse(act_overdue.is_future)
        self.assertEqual(act_overdue.status_label, 'Overdue')
        self.assertEqual(act_overdue.record_url, '/settings/companies/5/')

        # Today activity
        act_today = MailActivity(
            activity_type=act_type,
            summary='Daily standup',
            date_deadline=today,
            state='planned',
            res_model='res.users',
            res_id=2
        )
        self.assertFalse(act_today.is_overdue)
        self.assertTrue(act_today.is_today)
        self.assertFalse(act_today.is_future)
        self.assertEqual(act_today.status_label, 'Today')
        self.assertEqual(act_today.record_url, '/settings/users/2/')

        # Future activity
        act_future = MailActivity(
            activity_type=act_type,
            summary='Quarterly review',
            date_deadline=today + timedelta(days=10),
            state='planned',
            res_model='res.groups',
            res_id=3
        )
        self.assertFalse(act_future.is_overdue)
        self.assertFalse(act_future.is_today)
        self.assertTrue(act_future.is_future)
        self.assertEqual(act_future.status_label, 'Planned')
        self.assertEqual(act_future.record_url, '/settings/groups/3/')

        # Completed activity
        act_done = MailActivity(
            activity_type=act_type,
            summary='Signed NDA',
            date_deadline=today,
            state='done'
        )
        self.assertEqual(act_done.status_label, 'Done')
        self.assertEqual(act_done.record_url, '#')


class TechnicalOutgoingMailAndParametersTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _add_session(self, request, is_admin=True, user_id=1, username='admin'):
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        user = SimpleNamespace(
            id=user_id,
            username=username,
            name=username.capitalize(),
            email=f'{username}@example.com',
            is_active=True,
            is_admin=is_admin,
            role='Administrator' if is_admin else 'User'
        )
        return request, user

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.views.ensure_default_outgoing_mail_servers')
    @patch('base.models.IrMailServer.objects.filter')
    def test_technical_outgoing_mail_list(self, mock_filter, mock_ensure, mock_get_user):
        from base.views import technical_outgoing_mail
        request, user = self._add_session(self.factory.get('/settings/technical/outgoing-mail/'))
        mock_get_user.return_value = user
        s1 = SimpleNamespace(id=1, name='Gmail SMTP', smtp_host='smtp.gmail.com', smtp_port=587, smtp_encryption='starttls', get_smtp_encryption_display=lambda: 'TLS (STARTTLS)', smtp_user='admin@gmail.com', sequence=10, is_active=True)
        mock_filter.return_value.order_by.return_value = [s1]

        response = technical_outgoing_mail(request)
        self.assertEqual(response.status_code, 200)
        mock_ensure.assert_called_once()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.IrMailServer.objects.create')
    def test_technical_outgoing_mail_create(self, mock_create, mock_get_user):
        from base.views import technical_outgoing_mail_create
        request, user = self._add_session(self.factory.post('/settings/technical/outgoing-mail/new/', {
            'name': 'Production SendGrid',
            'smtp_host': 'smtp.sendgrid.net',
            'smtp_port': '587',
            'smtp_encryption': 'starttls',
            'smtp_user': 'apikey',
            'smtp_pass': 'secret123',
            'sequence': '5',
        }))
        mock_get_user.return_value = user
        created_server = SimpleNamespace(id=12, name='Production SendGrid')
        mock_create.return_value = created_server

        response = technical_outgoing_mail_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings/technical/outgoing-mail/12/')
        mock_create.assert_called_once()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.views.get_object_or_404')
    def test_technical_outgoing_mail_test_connection_handler(self, mock_get, mock_get_user):
        from base.views import technical_outgoing_mail_test_connection
        request, user = self._add_session(self.factory.post('/settings/technical/outgoing-mail/1/test-connection/'))
        mock_get_user.return_value = user
        server_mock = SimpleNamespace(
            id=1,
            test_connection=lambda: {'success': True, 'message': 'Connected OK', 'banner': '250 OK', 'latency_ms': 45}
        )
        mock_get.return_value = server_mock

        response = technical_outgoing_mail_test_connection(request, 1)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['latency_ms'], 45)

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.IrMailServer.test_connection')
    def test_technical_outgoing_mail_test_live_handler(self, mock_test, mock_get_user):
        from base.views import technical_outgoing_mail_test_live
        request, user = self._add_session(self.factory.post('/settings/technical/outgoing-mail/test-connection-live/', {
            'smtp_host': 'smtp.office365.com',
            'smtp_port': '587',
            'smtp_encryption': 'starttls',
            'smtp_user': 'user@office.com',
            'smtp_pass': 'pass',
        }))
        mock_get_user.return_value = user
        mock_test.return_value = {'success': True, 'message': 'Live test successful!', 'banner': '250 smtp.office365.com', 'latency_ms': 50}

        response = technical_outgoing_mail_test_live(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.views.ensure_default_config_parameters')
    @patch('base.models.IrConfigParameter.objects.filter')
    def test_technical_parameters_list(self, mock_filter, mock_ensure, mock_get_user):
        from base.views import technical_parameters
        request, user = self._add_session(self.factory.get('/settings/technical/parameters/'))
        mock_get_user.return_value = user
        p1 = SimpleNamespace(id=1, key='web.base.url', value='http://localhost:8000', description='Base URL', is_system=True)
        mock_filter.return_value.order_by.return_value = [p1]

        response = technical_parameters(request)
        self.assertEqual(response.status_code, 200)
        mock_ensure.assert_called_once()

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.IrConfigParameter.objects.filter')
    @patch('base.models.IrConfigParameter.objects.create')
    def test_technical_parameter_create(self, mock_create, mock_filter, mock_get_user):
        from base.views import technical_parameter_create
        request, user = self._add_session(self.factory.post('/settings/technical/parameters/new/', {
            'key': 'auth.jwt.secret',
            'value': 'super-secret-jwt-key-2026',
            'description': 'Secret key for JWT generation',
        }))
        mock_get_user.return_value = user
        mock_filter.return_value.exists.return_value = False
        created_p = SimpleNamespace(id=8, key='auth.jwt.secret')
        mock_create.return_value = created_p

        response = technical_parameter_create(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/settings/technical/parameters/8/')
        mock_create.assert_called_once()

    def test_parameter_model_get_and_set_param(self):
        from base.models import IrConfigParameter
        with patch('base.models.IrConfigParameter.objects.filter') as mock_filter, \
             patch('base.models.IrConfigParameter.objects.get_or_create') as mock_goc:
            
            p_obj = SimpleNamespace(value='http://erp.mycompany.com')
            mock_filter.return_value.first.return_value = p_obj
            val = IrConfigParameter.get_param('web.base.url')
            self.assertEqual(val, 'http://erp.mycompany.com')

            mock_filter.return_value.first.return_value = None
            val_def = IrConfigParameter.get_param('non.existent.key', default='fallback_val')
            self.assertEqual(val_def, 'fallback_val')

            param_instance = SimpleNamespace(key='custom.key', value='old', description=None, save=lambda update_fields: None)
            mock_goc.return_value = (param_instance, False)
            res = IrConfigParameter.set_param('custom.key', 'new_value', description='Custom Desc')
            self.assertEqual(res.value, 'new_value')
            self.assertEqual(res.description, 'Custom Desc')


class DiagnosticsAndLoggingTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _add_session(self, request):
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        request.session['ir_user_id'] = user.id
        return request, user

    def test_extract_diagnostics_from_exception(self):
        from base.models import extract_diagnostics_from_exception

        def failing_sample_function():
            raise KeyError("test_param_missing")

        try:
            failing_sample_function()
        except Exception as e:
            diag = extract_diagnostics_from_exception(e)
            self.assertEqual(diag['error_type'], 'KeyError')
            self.assertIn('test_param_missing', diag['message'])
            self.assertIn('tests.py', diag['file'])
            self.assertGreater(diag['line'], 0)
            self.assertEqual(diag['function'], 'failing_sample_function')
            self.assertIn('required dictionary key', diag['hint'].lower())

    @patch('base.models.IrLogging.objects.create')
    def test_ir_logging_log_exception(self, mock_create):
        from base.models import IrLogging
        try:
            1 / 0
        except ZeroDivisionError as e:
            IrLogging.log_exception(e, level='CRITICAL', log_type='server')
            mock_create.assert_called_once()
            _, kwargs = mock_create.call_args
            self.assertEqual(kwargs['level'], 'CRITICAL')
            self.assertEqual(kwargs['type'], 'server')
            self.assertIn('division by zero', kwargs['message'])

    @patch('base.models.IrLogging.log_exception')
    def test_global_exception_middleware_ajax_response(self, mock_log):
        from base.middleware import GlobalExceptionDiagnosticMiddleware
        middleware = GlobalExceptionDiagnosticMiddleware(lambda req: None)

        request, _ = self._add_session(self.factory.get('/some-ajax-api/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'))

        try:
            raise ValueError("Test AJAX failure")
        except Exception as exc:
            response = middleware.process_exception(request, exc)

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data['success'])
        self.assertTrue(data['error'])
        self.assertEqual(data['error_type'], 'ValueError')
        self.assertEqual(data['message'], 'Test AJAX failure')
        self.assertIn('tests.py', data['file'])
        self.assertGreater(data['line'], 0)
        mock_log.assert_called_once()

    @patch('base.models.IrLogging.log_exception')
    @patch('base.middleware.render')
    def test_global_exception_middleware_html_response(self, mock_render, mock_log):
        from base.middleware import GlobalExceptionDiagnosticMiddleware
        middleware = GlobalExceptionDiagnosticMiddleware(lambda req: None)

        request, _ = self._add_session(self.factory.get('/some-html-page/'))

        try:
            raise TypeError("Test HTML failure")
        except Exception as exc:
            middleware.process_exception(request, exc)

        mock_render.assert_called_once()
        _, template_name, context = mock_render.call_args[0]
        self.assertEqual(template_name, 'base/500.html')
        self.assertEqual(context['diag']['error_type'], 'TypeError')
        self.assertIn('tests.py', context['diag']['file'])

    def test_custom_error_handlers(self):
        from base.views import error_400_view, error_403_view, error_404_view, error_500_view
        with patch('base.views.render') as mock_render:
            req, _ = self._add_session(self.factory.get('/test-400/'))
            error_400_view(req)
            self.assertEqual(mock_render.call_args[0][1], 'base/400.html')

            req, _ = self._add_session(self.factory.get('/test-403/'))
            error_403_view(req)
            self.assertEqual(mock_render.call_args[0][1], 'base/403.html')

            req, _ = self._add_session(self.factory.get('/test-404/'))
            error_404_view(req)
            self.assertEqual(mock_render.call_args[0][1], 'base/404.html')

            req, _ = self._add_session(self.factory.get('/test-500/'))
            error_500_view(req)
            self.assertEqual(mock_render.call_args[0][1], 'base/500.html')

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.IrLogging.objects.filter')
    def test_technical_logging_list_and_clear_views(self, mock_filter, mock_get_user):
        from django.utils import timezone
        from base.views import technical_logging, technical_logging_clear
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user

        mock_log = SimpleNamespace(id=1, level='ERROR', type='server', message='Err', path='a.py', line_no=10, func_name='fn', created_at=timezone.now(), user=mock_user)
        qs_mock = mock_filter.return_value.select_related.return_value
        qs_mock.filter.return_value = qs_mock
        qs_mock.order_by.return_value = [mock_log]

        with patch('base.views.render') as mock_render:
            req, _ = self._add_session(self.factory.get('/settings/technical/logging/?level=ERROR'))
            technical_logging(req)
            mock_render.assert_called_once()
            _, template, ctx = mock_render.call_args[0]
            self.assertEqual(template, 'base/technical_logging.html')
            self.assertEqual(ctx['level_filter'], 'ERROR')

        with patch('base.models.IrLogging.objects.all') as mock_all:
            mock_all.return_value.delete.return_value = (5, {})
            req, _ = self._add_session(self.factory.post('/settings/technical/logging/clear/'))
            res = technical_logging_clear(req)
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.url, '/settings/technical/logging/')

    @patch('authentication.auth_helpers.get_current_ir_user')
    @patch('base.models.ResCompany.objects.filter')
    @patch('base.models.ResUsers.objects.filter')
    @patch('base.models.ResPartner.objects.filter')
    @patch('base.models.ResPartner.objects.get_or_create')
    def test_partner_detail_and_list_views(self, mock_goc, mock_filter, mock_u_filter, mock_c_filter, mock_get_user):
        from base.views import settings_partner_detail, settings_partners
        mock_user = SimpleNamespace(id=1, username='admin', is_active=True, is_admin=True)
        mock_get_user.return_value = mock_user

        mock_c_filter.return_value.order_by.return_value = []
        mock_u_filter.return_value.first.return_value = None

        p = SimpleNamespace(
            id=1, name='Alex Morgan', email='alex.morgan@officepro.internal', phone='9876543210',
            address='Office 3052, Navi Mumbai', is_company=False, display_company_name='Office Pro Solutions Ltd',
            display_address='Office 3052, Navi Mumbai', job_position='Sales Director', gstin='27AHKPN6854C2Z3',
            pan='AHKPN6854C', website='https://www.odoo.com', save=lambda: None
        )
        mock_qs = MagicMock()
        mock_qs.first.return_value = p
        mock_qs.count.return_value = 1
        mock_qs.order_by.return_value = mock_qs
        mock_qs.values_list.return_value = [1]
        mock_qs.__getitem__.return_value = [p]
        mock_filter.return_value = mock_qs

        with patch('base.views.render') as mock_render, patch('base.views.get_object_or_404', return_value=p):
            req, _ = self._add_session(self.factory.get('/settings/contacts/1/'))
            settings_partner_detail(req, 1)
            mock_render.assert_called_once()
            _, template, ctx = mock_render.call_args[0]
            self.assertEqual(template, 'base/settings_partner_detail.html')
            self.assertEqual(ctx['partner_obj'].name, 'Alex Morgan')

        with patch('base.views.render') as mock_render:
            req, _ = self._add_session(self.factory.get('/settings/contacts/'))
            settings_partners(req)
            mock_render.assert_called_once()
            _, template, ctx = mock_render.call_args[0]
            self.assertEqual(template, 'base/settings_partners.html')












