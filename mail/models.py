from django.db import models
from django.utils import timezone


class MailAttachment(models.Model):
    _name = 'mail.attachment'
    _description = 'Mail Attachment'

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='mail_attachments/', blank=True, null=True)
    file_size = models.IntegerField(default=0, help_text="Size in bytes")
    content_type = models.CharField(max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mail_attachment'
        ordering = ['created_at']

    def __str__(self):
        return self.name

    @property
    def formatted_size(self):
        if not self.file_size:
            return "0 KB"
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    @property
    def file_icon(self):
        ext = self.name.split('.')[-1].lower() if '.' in self.name else ''
        if ext in ['pdf']:
            return '📄'
        if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp']:
            return '🖼️'
        if ext in ['csv', 'xlsx', 'xls']:
            return '📊'
        if ext in ['doc', 'docx', 'txt', 'rtf', 'md']:
            return '📝'
        if ext in ['zip', 'rar', 'tar', 'gz', '7z']:
            return '📦'
        return '📁'


class MailMail(models.Model):
    _name = 'mail.mail'
    _description = 'Outgoing and Incoming Webmail'

    FOLDER_CHOICES = [
        ('inbox', 'Inbox'),
        ('starred', 'Starred'),
        ('sent', 'Sent'),
        ('drafts', 'Drafts'),
        ('archive', 'Archive'),
        ('trash', 'Trash'),
        ('spam', 'Spam'),
    ]

    LABEL_CHOICES = [
        ('work', 'Work'),
        ('internal', 'Internal'),
        ('clients', 'Clients'),
        ('finance', 'Finance'),
        ('support', 'Support'),
        ('system', 'System'),
        ('personal', 'Personal'),
    ]

    STATE_CHOICES = [
        ('outgoing', 'Outgoing'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('exception', 'Failed'),
        ('draft', 'Draft'),
    ]

    # Mailbox Owner (the user in whose mailbox this message lives)
    user = models.ForeignKey('base.ResUsers', on_delete=models.CASCADE, related_name='mailbox_emails', blank=True, null=True)
    sender_user = models.ForeignKey('base.ResUsers', on_delete=models.SET_NULL, blank=True, null=True, related_name='sent_webmails')
    recipient_user = models.ForeignKey('base.ResUsers', on_delete=models.SET_NULL, blank=True, null=True, related_name='received_webmails')

    # Addressing
    email_from = models.CharField(max_length=255, help_text="Sender display and email, e.g. John Doe <john@company.com>")
    email_to = models.TextField(help_text="Primary recipients (comma or semicolon separated)")
    email_cc = models.TextField(blank=True, null=True, help_text="Carbon copy recipients")
    email_bcc = models.TextField(blank=True, null=True, help_text="Blind carbon copy recipients")
    reply_to = models.CharField(max_length=255, blank=True, null=True)

    # Content
    subject = models.CharField(max_length=255, default='(No Subject)')
    body_html = models.TextField(blank=True, default='')
    body_text = models.TextField(blank=True, default='')

    # Mailbox status
    folder = models.CharField(max_length=30, choices=FOLDER_CHOICES, default='inbox')
    is_starred = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    label = models.CharField(max_length=30, choices=LABEL_CHOICES, default='work')

    # ERP Document Integration (link directly to Sales, Invoices, Partners, etc.)
    res_model = models.CharField(max_length=100, blank=True, null=True)
    res_id = models.IntegerField(default=0, blank=True, null=True)
    res_name = models.CharField(max_length=255, blank=True, null=True)

    # Threading
    parent_mail = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='replies')

    # Attachments & Server
    attachments = models.ManyToManyField(MailAttachment, blank=True, related_name='mails')
    mail_server = models.ForeignKey('base.IrMailServer', on_delete=models.SET_NULL, blank=True, null=True, related_name='dispatched_mails')
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='received')

    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_mail'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.subject} ({self.email_from})"

    @property
    def snippet(self):
        import re
        if self.body_text:
            text = self.body_text
        elif self.body_html:
            text = re.sub(r'<[^>]+>', ' ', self.body_html)
            text = re.sub(r'\s+', ' ', text).strip()
        else:
            text = ""
        return (text[:110] + '...') if len(text) > 110 else text

    @property
    def avatar_initial(self):
        name = self.sender_name
        return name[:1].upper() if name else 'M'

    @property
    def sender_name(self):
        if '<' in self.email_from:
            return self.email_from.split('<')[0].strip(' "\'')
        return self.email_from or 'Unknown'

    @property
    def sender_email(self):
        if '<' in self.email_from and '>' in self.email_from:
            return self.email_from.split('<')[1].split('>')[0].strip()
        return self.email_from or ''

    @property
    def avatar_color(self):
        colors = [
            '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#ef4444',
            '#f97316', '#f59e0b', '#10b981', '#06b6d4', '#0ea5e9',
            '#714b67', '#3b82f6', '#14b8a6'
        ]
        s = self.email_from or 'user'
        idx = sum(ord(c) for c in s) % len(colors)
        return colors[idx]

    @property
    def formatted_date(self):
        now = timezone.now()
        local_date = timezone.localtime(self.date) if timezone.is_aware(self.date) else self.date
        if local_date.date() == now.date():
            return local_date.strftime('%I:%M %p')
        elif local_date.year == now.year:
            return local_date.strftime('%b %d')
        return local_date.strftime('%b %d, %Y')

    @property
    def formatted_full_date(self):
        local_date = timezone.localtime(self.date) if timezone.is_aware(self.date) else self.date
        return local_date.strftime('%a, %b %d, %Y, %I:%M %p')

    @property
    def has_attachments(self):
        return self.attachments.exists()

    @property
    def record_url(self):
        if not self.res_model or not self.res_id:
            return None
        if self.res_model == 'res.company':
            return f"/settings/companies/{self.res_id}/"
        if self.res_model == 'res.users':
            return f"/settings/users/{self.res_id}/"
        if self.res_model == 'res.groups':
            return f"/settings/groups/{self.res_id}/"
        if self.res_model == 'res.privilege':
            return f"/settings/privileges/{self.res_id}/"
        if self.res_model in ['ir.actions.act_window', 'ir.actions']:
            return f"/settings/technical/actions/{self.res_id}/"
        if self.res_model == 'ir.model':
            return f"/settings/technical/models/{self.res_id}/"
        if self.res_model == 'ir.ui.view':
            return f"/settings/technical/views/{self.res_id}/"
        if self.res_model == 'ir.mail_server':
            return f"/settings/technical/outgoing-mail/{self.res_id}/"
        return f"/settings/technical/models/{self.res_id}/"
