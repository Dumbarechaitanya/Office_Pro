import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase, RequestFactory
from django.utils import timezone
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.contrib.messages.storage.fallback import FallbackStorage

from base.models import ResUsers, ResCompany, IrMailServer
from mail.models import MailAttachment, MailMail
from mail.views import (
    mail_app,
    mail_api_emails,
    mail_api_email_detail,
    mail_api_compose,
    mail_api_reply,
    mail_api_star_toggle,
    mail_api_batch_action,
    mail_api_attachment_upload,
)


class MailModelUnitTests(SimpleTestCase):
    def test_mail_attachment_formatted_size_and_icons(self):
        att_small = MailAttachment(name='doc.pdf', file_size=500, content_type='application/pdf')
        att_med = MailAttachment(name='sheet.xlsx', file_size=204800, content_type='application/vnd.ms-excel')
        att_large = MailAttachment(name='archive.zip', file_size=3145728, content_type='application/zip')
        att_img = MailAttachment(name='photo.png', file_size=1024, content_type='image/png')
        att_text = MailAttachment(name='notes.txt', file_size=1024, content_type='text/plain')
        att_empty = MailAttachment(name='binary.bin', file_size=0)

        self.assertEqual(str(att_small), 'doc.pdf')
        self.assertEqual(att_small.formatted_size, '500 B')
        self.assertEqual(att_med.formatted_size, '200.0 KB')
        self.assertEqual(att_large.formatted_size, '3.0 MB')
        self.assertEqual(att_empty.formatted_size, '0 KB')

        self.assertEqual(att_small.file_icon, '📄')
        self.assertEqual(att_med.file_icon, '📊')
        self.assertEqual(att_large.file_icon, '📦')
        self.assertEqual(att_img.file_icon, '🖼️')
        self.assertEqual(att_text.file_icon, '📝')
        self.assertEqual(att_empty.file_icon, '📁')

    def test_mail_mail_properties_and_urls(self):
        fixed_date = timezone.now()
        mail = MailMail(
            id=1,
            email_from='Sarah Jenkins <sarah.jenkins@officepro.io>',
            email_to='admin@officepro.io',
            subject='Product Launch Roadmap',
            body_html='<p>Hello <strong>Team</strong>, here is the updated plan.</p>',
            body_text='',
            folder='inbox',
            date=fixed_date,
            res_model='res.company',
            res_id=42
        )

        self.assertIn('Product Launch Roadmap', str(mail))
        self.assertEqual(mail.sender_name, 'Sarah Jenkins')
        self.assertEqual(mail.sender_email, 'sarah.jenkins@officepro.io')
        self.assertEqual(mail.avatar_initial, 'S')
        self.assertTrue(len(mail.avatar_color) > 0)
        self.assertIn('Hello Team', mail.snippet)
        self.assertEqual(mail.record_url, '/settings/companies/42/')

        # URL routing for various ERP models
        mail.res_model = 'res.users'
        mail.res_id = 10
        self.assertEqual(mail.record_url, '/settings/users/10/')

        mail.res_model = 'res.groups'
        mail.res_id = 5
        self.assertEqual(mail.record_url, '/settings/groups/5/')

        mail.res_model = 'ir.mail_server'
        mail.res_id = 2
        self.assertEqual(mail.record_url, '/settings/technical/outgoing-mail/2/')

        mail.res_model = 'ir.actions.act_window'
        mail.res_id = 7
        self.assertEqual(mail.record_url, '/settings/technical/actions/7/')

        # Plain email sender
        mail_plain = MailMail(
            email_from='plain@example.com',
            body_text='Raw plain text body for snippet testing.'
        )
        self.assertEqual(mail_plain.sender_name, 'plain@example.com')
        self.assertEqual(mail_plain.sender_email, 'plain@example.com')
        self.assertEqual(mail_plain.avatar_initial, 'P')
        self.assertIn('Raw plain text body', mail_plain.snippet)


@patch('mail.views.get_current_ir_user')
@patch('authentication.auth_helpers.get_current_ir_user')
class MailViewAndApiTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = ResUsers(
            id=1,
            username='admin',
            email='admin@officepro.io',
            is_active=True
        )

    def _prepare_request(self, request):
        request.session = SessionStore()
        request.session['user_id'] = 1
        request._messages = FallbackStorage(request)
        request.user = self.user
        return request

    @patch('mail.views.MailMail.objects.filter')
    @patch('mail.views.ResUsers.objects.filter')
    @patch('mail.views.IrMailServer.objects.filter')
    @patch('mail.views.ResCompany.objects.all')
    @patch('mail.views.render')
    def test_mail_app_view_renders_template_with_context(
        self, mock_render, mock_companies, mock_servers, mock_users, mock_mail_filter, mock_auth_user, mock_mail_user
    ):
        mock_auth_user.return_value = self.user
        mock_mail_user.return_value = self.user

        qs_mock = MagicMock()
        qs_mock.filter.return_value = qs_mock
        qs_mock.exclude.return_value = qs_mock
        qs_mock.count.return_value = 0
        mock_mail_filter.return_value = qs_mock

        mock_users.return_value.order_by.return_value = [self.user]
        mock_servers.return_value.order_by.return_value = []
        mock_companies.return_value.order_by.return_value = []
        mock_render.return_value = MagicMock(status_code=200)

        request = self._prepare_request(self.factory.get('/mail/app/'))
        response = mail_app(request)

        self.assertEqual(response.status_code, 200)
        mock_render.assert_called_once()
        template_name = mock_render.call_args[0][1]
        context = mock_render.call_args[0][2]
        self.assertEqual(template_name, 'mail/mail_app.html')
        self.assertEqual(context['current_folder'], 'inbox')
        self.assertIn('folder_counts', context)
        self.assertIn('labels', context)

    @patch('mail.views.MailMail.objects.filter')
    def test_mail_api_emails_list_endpoint(self, mock_mail_filter, mock_auth_user, mock_mail_user):
        mock_auth_user.return_value = self.user
        mock_mail_user.return_value = self.user
        fake_mail = MagicMock()
        fake_mail.id = 101
        fake_mail.email_from = 'Alice <alice@test.com>'
        fake_mail.sender_name = 'Alice'
        fake_mail.sender_email = 'alice@test.com'
        fake_mail.avatar_initial = 'A'
        fake_mail.avatar_color = '#3b82f6'
        fake_mail.email_to = 'admin@officepro.io'
        fake_mail.subject = 'Project Discussion'
        fake_mail.snippet = 'Let us meet tomorrow.'
        fake_mail.folder = 'inbox'
        fake_mail.is_starred = True
        fake_mail.is_read = False
        fake_mail.is_important = True
        fake_mail.label = 'work'
        fake_mail.formatted_date = '10:30 AM'
        fake_mail.formatted_full_date = 'Today, 10:30 AM'
        fake_mail.has_attachments = False
        fake_mail.res_model = 'res.company'
        fake_mail.res_id = 1
        fake_mail.res_name = 'HQ'
        fake_mail.record_url = '/settings/companies/1/'

        mock_qs = MagicMock()
        mock_qs.exclude.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.order_by.return_value = [fake_mail]
        mock_qs.count.return_value = 1
        mock_mail_filter.return_value = mock_qs

        request = self._prepare_request(self.factory.get('/mail/api/emails/', {'folder': 'inbox'}))
        response = mail_api_emails(request)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(len(data['emails']), 1)
        self.assertEqual(data['emails'][0]['subject'], 'Project Discussion')

    @patch('mail.views.MailMail.objects.filter')
    @patch('mail.views.MailMail.objects.prefetch_related')
    def test_mail_api_email_detail_endpoint(self, mock_prefetch, mock_filter, mock_auth_user, mock_mail_user):
        mock_auth_user.return_value = self.user
        mock_mail_user.return_value = self.user
        fake_mail = MagicMock()
        fake_mail.id = 102
        fake_mail.email_from = 'Bob <bob@test.com>'
        fake_mail.sender_name = 'Bob'
        fake_mail.sender_email = 'bob@test.com'
        fake_mail.avatar_initial = 'B'
        fake_mail.avatar_color = '#10b981'
        fake_mail.email_to = 'admin@officepro.io'
        fake_mail.email_cc = ''
        fake_mail.email_bcc = ''
        fake_mail.reply_to = ''
        fake_mail.subject = 'Budget Approval'
        fake_mail.body_html = '<p>Approved.</p>'
        fake_mail.body_text = 'Approved.'
        fake_mail.folder = 'inbox'
        fake_mail.is_starred = False
        fake_mail.is_read = False
        fake_mail.is_important = False
        fake_mail.label = 'finance'
        fake_mail.formatted_date = '11:00 AM'
        fake_mail.formatted_full_date = 'Today, 11:00 AM'
        fake_mail.res_model = None
        fake_mail.res_id = 0
        fake_mail.res_name = None
        fake_mail.record_url = None
        fake_mail.attachments.all.return_value = []
        fake_mail.parent_mail = None
        fake_mail.parent_mail_id = None
        fake_mail.replies.all.return_value = []

        mock_prefetch.return_value.get.return_value = fake_mail
        mock_filter.return_value.order_by.return_value = [fake_mail]

        request = self._prepare_request(self.factory.get('/mail/api/emails/102/'))
        response = mail_api_email_detail(request, email_id=102)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertEqual(data['email']['subject'], 'Budget Approval')
        self.assertTrue(fake_mail.is_read)

    @patch('mail.views.ResUsers.objects.filter')
    @patch('mail.views.IrMailServer.objects.filter')
    @patch('mail.views.MailMail.objects.create')
    def test_mail_api_compose_endpoint(self, mock_create, mock_servers, mock_users_filter, mock_auth_user, mock_mail_user):
        mock_auth_user.return_value = self.user
        mock_mail_user.return_value = self.user
        mock_servers.return_value.first.return_value = None
        mock_users_filter.return_value.first.return_value = None
        fake_created = MagicMock()
        fake_created.id = 201
        fake_created.folder = 'sent'
        mock_create.return_value = fake_created

        payload = {
            'email_to': 'client@example.com',
            'subject': 'Service Agreement',
            'body_html': '<p>Here is your quote.</p>',
            'label': 'clients',
            'res_model': 'res.company',
            'res_name': 'Acme Corp',
            'is_draft': False
        }
        request = self._prepare_request(self.factory.post(
            '/mail/api/compose/',
            data=json.dumps(payload),
            content_type='application/json'
        ))
        response = mail_api_compose(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertEqual(data['email_id'], 201)
        mock_create.assert_called_once()

    @patch('mail.views.MailMail.objects.get')
    @patch('mail.views.MailMail.objects.create')
    def test_mail_api_reply_endpoint(self, mock_create, mock_get_mail, mock_auth_user, mock_mail_user):
        mock_auth_user.return_value = self.user
        mock_mail_user.return_value = self.user
        orig = MagicMock()
        orig.id = 301
        orig.email_from = 'client@example.com'
        orig.email_to = 'admin@officepro.io'
        orig.email_cc = ''
        orig.subject = 'Project Timeline'
        orig.label = 'clients'
        orig.res_model = None
        orig.res_id = 0
        orig.res_name = None
        orig.mail_server = None
        mock_get_mail.return_value = orig

        reply_obj = MagicMock()
        reply_obj.id = 302
        mock_create.return_value = reply_obj

        reply_payload = {'body_html': '<p>Got it, thanks!</p>', 'reply_all': False}
        request = self._prepare_request(self.factory.post(
            '/mail/api/emails/301/reply/',
            data=json.dumps(reply_payload),
            content_type='application/json'
        ))
        response = mail_api_reply(request, email_id=301)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertEqual(data['email_id'], 302)

    @patch('mail.views.MailMail.objects.get')
    def test_mail_api_star_toggle_endpoint(self, mock_get, mock_auth_user, mock_mail_user):
        mock_auth_user.return_value = self.user
        mock_mail_user.return_value = self.user
        fake_mail = MagicMock()
        fake_mail.id = 401
        fake_mail.is_starred = False
        mock_get.return_value = fake_mail

        request = self._prepare_request(self.factory.post(
            '/mail/api/emails/401/star/',
            data=json.dumps({}),
            content_type='application/json'
        ))
        response = mail_api_star_toggle(request, email_id=401)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertTrue(data['is_starred'])

    @patch('mail.views.MailMail.objects.filter')
    def test_mail_api_batch_actions_endpoint(self, mock_mail_filter, mock_auth_user, mock_mail_user):
        mock_auth_user.return_value = self.user
        mock_mail_user.return_value = self.user
        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.update.return_value = 2
        mock_mail_filter.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs

        # Batch Archive
        req = self._prepare_request(self.factory.post(
            '/mail/api/batch-action/',
            data=json.dumps({'action': 'archive', 'email_ids': [1, 2]}),
            content_type='application/json'
        ))
        res = json.loads(mail_api_batch_action(req).content.decode('utf-8'))
        self.assertTrue(res['success'])
        mock_qs.update.assert_called_with(folder='archive')

        # Batch Star
        req_star = self._prepare_request(self.factory.post(
            '/mail/api/batch-action/',
            data=json.dumps({'action': 'star', 'email_ids': [1, 2]}),
            content_type='application/json'
        ))
        res_star = json.loads(mail_api_batch_action(req_star).content.decode('utf-8'))
        self.assertTrue(res_star['success'])
        mock_qs.update.assert_called_with(is_starred=True)

        # Batch Set Label
        req_lbl = self._prepare_request(self.factory.post(
            '/mail/api/batch-action/',
            data=json.dumps({'action': 'set_label', 'email_ids': [1], 'value': 'finance'}),
            content_type='application/json'
        ))
        res_lbl = json.loads(mail_api_batch_action(req_lbl).content.decode('utf-8'))
        self.assertTrue(res_lbl['success'])
        mock_qs.update.assert_called_with(label='finance')

    @patch('mail.views.MailAttachment.objects.create')
    def test_mail_api_attachment_upload_endpoint(self, mock_create_att, mock_auth_user, mock_mail_user):
        mock_auth_user.return_value = self.user
        mock_mail_user.return_value = self.user
        fake_att = MagicMock()
        fake_att.id = 501
        fake_att.name = 'contract.pdf'
        fake_att.formatted_size = '1.2 MB'
        fake_att.file_icon = '📄'
        fake_att.file.url = '/media/mail_attachments/contract.pdf'
        mock_create_att.return_value = fake_att

        dummy_file = MagicMock()
        dummy_file.name = 'contract.pdf'
        dummy_file.size = 1258291
        dummy_file.content_type = 'application/pdf'

        request = self._prepare_request(self.factory.post(
            '/mail/api/upload-attachment/',
            {'file': dummy_file}
        ))
        response = mail_api_attachment_upload(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['name'], 'contract.pdf')
        self.assertEqual(data['id'], 501)
