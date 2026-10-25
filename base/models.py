from django.db import models
from django.utils import timezone


from base.fields import EncryptedCharField

class ResPrivilege(models.Model):
    _name = 'res.privilege'
    _description = 'Privileges'

    name = models.CharField(max_length=150, unique=True)
    sequence = models.IntegerField(default=10)
    category = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='sub_privileges')
    is_placeholder = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'res_privilege'
        ordering = ['sequence', 'name']

    def __str__(self):
        return self.name

    @property
    def groups_list(self):
        if hasattr(self, 'groups'):
            return self.groups.filter(is_active=True).order_by('sequence', 'name')
        return []


class ResCompany(models.Model):
    _name = 'res.company'
    _description = 'Company'

    name = models.CharField(max_length=150)
    partner = models.ForeignKey('ResPartner', on_delete=models.SET_NULL, blank=True, null=True, related_name='companies')
    email = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    street2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    gstin = models.CharField(max_length=50, blank=True, null=True)
    company_registry = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=20, default='INR')
    parent_company = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='branches')
    email_domain = models.CharField(max_length=150, blank=True, null=True)
    bounce_email = models.CharField(max_length=150, blank=True, null=True)
    catchall_email = models.CharField(max_length=150, blank=True, null=True)
    default_from_email = models.CharField(max_length=150, blank=True, null=True)
    color = models.CharField(max_length=50, default='#714b67', blank=True, null=True)
    x_account = models.CharField(max_length=150, blank=True, null=True)
    facebook_account = models.CharField(max_length=150, blank=True, null=True)
    github_account = models.CharField(max_length=150, blank=True, null=True)
    linkedin_account = models.CharField(max_length=150, blank=True, null=True)
    logo_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'res_company'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def branches_count(self):
        return self.branches.filter(is_active=True).count()


class ResGroups(models.Model):
    _name = 'res.groups'
    _description = 'Access Groups'

    name = models.CharField(max_length=100)
    privilege = models.CharField(max_length=100, default='General')
    privilege_ref = models.ForeignKey(ResPrivilege, on_delete=models.SET_NULL, blank=True, null=True, related_name='groups')
    description = models.TextField(blank=True, null=True)
    is_share = models.BooleanField(default=False)
    api_keys_max_days = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    sequence = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'res_groups'
        ordering = ['privilege', 'sequence', 'name']

    def __str__(self):
        return f"{self.privilege} / {self.name}" if self.privilege else self.name


class MailActivityType(models.Model):
    _name = 'mail.activity.type'
    _description = 'Activity Type'

    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='📝')
    category = models.CharField(max_length=50, default='default')
    sequence = models.IntegerField(default=10)
    default_next_days = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_activity_type'
        ordering = ['sequence', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}"


class MailChannel(models.Model):
    _name = 'mail.channel'
    _description = 'Mail Channel / Direct Chat'

    name = models.CharField(max_length=150, blank=True, null=True)
    channel_type = models.CharField(max_length=30, default='chat', choices=[
        ('chat', 'Direct Message'),
        ('channel', 'Group Channel'),
    ])
    members = models.ManyToManyField('ResUsers', blank=True, related_name='mail_channels')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_channel'
        ordering = ['-updated_at']

    def __str__(self):
        return self.name or f"Chat #{self.id}"


class MailMessage(models.Model):
    _name = 'mail.message'
    _description = 'Mail Message'

    model_name = models.CharField(max_length=100, default='general', blank=True, null=True)
    record_id = models.IntegerField(default=0, blank=True, null=True)
    author = models.ForeignKey('ResUsers', on_delete=models.SET_NULL, blank=True, null=True, related_name='sent_messages')
    recipient = models.ForeignKey('ResUsers', on_delete=models.SET_NULL, blank=True, null=True, related_name='received_messages')
    channel = models.ForeignKey(MailChannel, on_delete=models.SET_NULL, blank=True, null=True, related_name='messages')
    subject = models.CharField(max_length=255, blank=True, null=True)
    message_type = models.CharField(max_length=30, default='comment', choices=[
        ('comment', 'Message'),
        ('note', 'Log Note'),
        ('notification', 'Notification'),
    ])
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mail_message'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.message_type} on {self.model_name}:{self.record_id}"


class MailActivity(models.Model):
    _name = 'mail.activity'
    _description = 'Activity / Scheduled Action'

    STATE_CHOICES = [
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]

    activity_type = models.ForeignKey(MailActivityType, on_delete=models.CASCADE, related_name='activities')
    summary = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)
    date_deadline = models.DateField()
    user = models.ForeignKey('ResUsers', on_delete=models.CASCADE, related_name='assigned_activities')
    created_by = models.ForeignKey('ResUsers', on_delete=models.SET_NULL, blank=True, null=True, related_name='created_activities')
    res_model = models.CharField(max_length=100, default='general')
    res_id = models.IntegerField(default=0)
    res_name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='planned')
    feedback = models.TextField(blank=True, null=True)
    done_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mail_activity'
        ordering = ['date_deadline', '-created_at']

    def __str__(self):
        return f"{self.activity_type.name}: {self.summary}"

    @property
    def is_overdue(self):
        from datetime import date
        return self.state == 'planned' and self.date_deadline < date.today()

    @property
    def is_today(self):
        from datetime import date
        return self.state == 'planned' and self.date_deadline == date.today()

    @property
    def is_future(self):
        from datetime import date
        return self.state == 'planned' and self.date_deadline > date.today()

    @property
    def status_label(self):
        if self.state == 'done':
            return 'Done'
        if self.state == 'cancelled':
            return 'Cancelled'
        if self.is_overdue:
            return 'Overdue'
        if self.is_today:
            return 'Today'
        return 'Planned'

    @property
    def record_url(self):
        if not self.res_model or not self.res_id:
            return '#'
        if self.res_model == 'res.company':
            return f"/settings/companies/{self.res_id}/"
        if self.res_model == 'res.users':
            return f"/settings/users/{self.res_id}/"
        if self.res_model == 'res.groups':
            return f"/settings/groups/{self.res_id}/"
        if self.res_model == 'res.privilege':
            return f"/settings/privileges/{self.res_id}/"
        if self.res_model == 'ir.actions.act_window' or self.res_model == 'ir.actions':
            return f"/settings/technical/actions/{self.res_id}/"
        if self.res_model == 'ir.model':
            return f"/settings/technical/models/{self.res_id}/"
        if self.res_model == 'ir.ui.view':
            return f"/settings/technical/views/{self.res_id}/"
        if self.res_model == 'ir.cron':
            return f"/settings/technical/cron/{self.res_id}/"
        if self.res_model == 'ir.actions.report':
            return f"/settings/technical/reports/{self.res_id}/"
        if self.res_model == 'report.paperformat':
            return f"/settings/technical/paper-formats/{self.res_id}/"
        return '#'


class ResUsers(models.Model):
    _name = 'res.users'
    _description = 'User'

    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    company = models.ForeignKey(ResCompany, on_delete=models.DO_NOTHING, db_column='company_id', blank=True, null=True)
    employee = models.ForeignKey('employee.Employee', on_delete=models.DO_NOTHING, db_column='employee_id', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        managed = False
        db_table = 'res_users'

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.username

    def natural_key(self):
        return (self.username,)

    def get_session_auth_hash(self):
        return self.password_hash or ''

    @property
    def is_admin(self):
        if hasattr(self, '_is_admin_cached'):
            return self._is_admin_cached
        from authentication.auth_helpers import is_admin_user
        res = is_admin_user(self)
        self._is_admin_cached = res
        return res

    @property
    def name(self):
        if self.employee_id and self.employee:
            return self.employee.name
        return self.username

    @property
    def login(self):
        return self.email or self.username

    @property
    def lang(self):
        return 'English (US)'

    @property
    def latest_login(self):
        if hasattr(self, 'updated_at') and self.updated_at:
            return self.updated_at.strftime('%b %d, %I:%M %p')
        return 'Active'

    @property
    def role(self):
        return 'Administrator' if self.is_admin else 'User'

    @property
    def avatar_color(self):
        if self.employee and hasattr(self.employee, 'avatar_color'):
            return self.employee.avatar_color
        PALETTE = [
            '#4f46e5', '#7c3aed', '#059669', '#d97706', '#dc2626',
            '#0284c7', '#0891b2', '#be185d', '#9333ea', '#ea580c',
            '#15803d', '#4338ca', '#b45309', '#0f766e', '#a21caf',
            '#047857', '#b91c1c', '#6d28d9', '#1d4ed8', '#c2410c'
        ]
        seed = ((self.id or 1) * 37 + sum(ord(c) for c in (self.username or ''))) % len(PALETTE)
        return PALETTE[seed]




class ResPartner(models.Model):
    _name = 'res.partner'
    _description = 'Partner / Contact'

    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_company = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, db_column='parent_id', blank=True, null=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'res_partner'

    def __str__(self):
        return self.name

    @property
    def display_company_name(self):
        if self.parent and self.parent.is_company:
            return self.parent.name
        return "Office Pro Solutions Ltd"

    @property
    def display_address(self):
        return self.address or "Office No. 3052, P Wing, Akshar Business Park, Janata Market Road, Sector 25\nNavi Mumbai 400024 Maharashtra (India)"

    @property
    def job_position(self):
        return getattr(self, '_job_position', 'Sales Director')

    @property
    def gstin(self):
        return getattr(self, '_gstin', '27AHKPN6854C2Z3')

    @property
    def pan(self):
        return getattr(self, '_pan', 'AHKPN6854C')

    @property
    def website(self):
        return getattr(self, '_website', 'https://www.odoo.com')

    @property
    def gst_treatment(self):
        return getattr(self, '_gst_treatment', 'Registered Business - Regular')

    @property
    def language(self):
        return getattr(self, '_language', 'English (US)')

    @property
    def tags_list(self):
        return ['B2B', 'VIP', 'Consulting']


class ResUsersGroups(models.Model):
    _name = 'res.users.groups'
    _description = 'User Groups Rel'

    user = models.ForeignKey(ResUsers, on_delete=models.DO_NOTHING, db_column='user_id', default=1)
    group = models.ForeignKey(ResGroups, on_delete=models.DO_NOTHING, db_column='group_id', default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'res_users_groups'
        unique_together = (('user', 'group'),)


class IrUiMenu(models.Model):
    _name = 'ir.ui.menu'
    _description = 'UI Menu'

    name = models.CharField(max_length=150)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, db_column='parent_id', blank=True, null=True, related_name='children')
    sequence = models.IntegerField(default=10)
    url_path = models.CharField(max_length=255, blank=True, null=True)
    action_model = models.CharField(max_length=100, blank=True, null=True)
    web_icon = models.CharField(max_length=255, blank=True, null=True)
    visibility_group = models.ForeignKey(ResGroups, on_delete=models.DO_NOTHING, db_column='visibility_group_id', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'ir_ui_menu'

    def __str__(self):
        return self.name


class IrModule(models.Model):
    _name = 'ir.module'
    _description = 'Module'

    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=20, default='uninstalled')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'ir_module'

    def __str__(self):
        return self.name


class IrModel(models.Model):
    _name = 'ir.model'
    _description = 'Model'

    model_name = models.CharField(max_length=100, unique=True)
    table_name = models.CharField(max_length=100)
    module = models.ForeignKey(IrModule, on_delete=models.DO_NOTHING, db_column='module_id', blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    abstract = models.BooleanField(default=False)
    transient = models.BooleanField(default=False)
    is_mail_thread = models.BooleanField(default=False)
    is_mail_activity = models.BooleanField(default=False)
    is_mail_blacklist = models.BooleanField(default=False)
    model_order = models.CharField(max_length=255, default='id')
    STATE_CHOICES = [('base', 'Base Object'), ('manual', 'Custom Object')]
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='manual')

    class Meta:
        managed = False
        db_table = 'ir_model'

    def __str__(self):
        return self.model_name

    @property
    def name(self):
        return self.description or self.model_name


class IrModelFields(models.Model):
    _name = 'ir.model.fields'
    _description = 'Model Fields'

    model = models.ForeignKey(IrModel, on_delete=models.DO_NOTHING, db_column='model_id')
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=50)
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    relation_model = models.ForeignKey(
        'IrModel', on_delete=models.DO_NOTHING, db_column='relation_model_id',
        blank=True, null=True, related_name='+',
    )

    class Meta:
        managed = False
        db_table = 'ir_model_fields'
        unique_together = (('model', 'field_name'),)

    def __str__(self):
        m = self.model.model_name if self.model_id and self.model else ''
        return f"{m}.{self.field_name}" if m else self.field_name

    @property
    def name(self):
        return self.field_name


class IrModelAccess(models.Model):
    _name = 'ir.model.access'
    _description = 'Model Access Rights'

    model = models.ForeignKey(IrModel, on_delete=models.DO_NOTHING, db_column='model_id')
    group = models.ForeignKey(ResGroups, on_delete=models.DO_NOTHING, db_column='group_id')
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'ir_model_access'
        unique_together = (('model', 'group'),)

    def __str__(self):
        m = self.model.model_name if self.model_id and self.model else 'All Models'
        g = self.group.name if self.group_id and self.group else 'Global'
        return f"{m} ({g})"

    @property
    def name(self):
        return str(self)


class IrRule(models.Model):
    _name = 'ir.rule'
    _description = 'Record Rules'

    model = models.ForeignKey(IrModel, on_delete=models.DO_NOTHING, db_column='model_id', blank=True, null=True)
    group = models.ForeignKey(ResGroups, on_delete=models.DO_NOTHING, db_column='group_id', blank=True, null=True)
    rule_name = models.CharField(max_length=150)
    domain_force = models.TextField(blank=True, null=True)
    condition_field = models.CharField(max_length=100, blank=True, null=True)
    condition_value = models.CharField(max_length=100, blank=True, null=True)
    perm_read = models.BooleanField(default=True)
    perm_write = models.BooleanField(default=True)
    perm_create = models.BooleanField(default=True)
    perm_unlink = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'ir_rule'

    def __str__(self):
        return self.rule_name

    @property
    def name(self):
        return self.rule_name

    @property
    def domain_display(self):
        if self.domain_force:
            return self.domain_force
        if self.condition_field and self.condition_value:
            return f"[('{self.condition_field}', '=', '{self.condition_value}')]"
        return "[(1, '=', 1)]"


class IrSequence(models.Model):
    _name = 'ir.sequence'
    _description = 'Sequences'

    name = models.CharField(max_length=150, blank=True, null=True)
    code = models.CharField(max_length=100, unique=True)
    implementation = models.CharField(max_length=20, default='standard')
    prefix = models.CharField(max_length=100, blank=True, null=True)
    suffix = models.CharField(max_length=100, blank=True, null=True)
    use_date_range = models.BooleanField(default=False)
    next_number = models.IntegerField(default=1)
    step = models.IntegerField(default=1)
    padding = models.IntegerField(default=5)
    company = models.ForeignKey(ResCompany, on_delete=models.DO_NOTHING, db_column='company_id', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'ir_sequence'

    def __str__(self):
        return self.name or self.code



class IrFilters(models.Model):
    _name = 'ir.filters'
    _description = 'Filters / Favorites'

    name = models.CharField(max_length=150)
    model = models.ForeignKey(IrModel, on_delete=models.DO_NOTHING, db_column='model_id')
    user = models.ForeignKey(ResUsers, on_delete=models.DO_NOTHING, db_column='user_id',
                              blank=True, null=True, related_name='saved_filters')
    domain = models.JSONField(default=list, blank=True)
    context = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(default=False)
    sequence = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'ir_filters'
        unique_together = (('model', 'user', 'name'),)

    def __str__(self):
        return self.name


class IrUiView(models.Model):
    _name = 'ir.ui.view'
    _description = 'UI Views'

    name = models.CharField(max_length=150)
    view_type = models.CharField(max_length=20, default='list')
    model = models.ForeignKey(IrModel, on_delete=models.DO_NOTHING, db_column='model_id',
                               blank=True, null=True, related_name='+')
    key = models.CharField(max_length=150, blank=True, null=True)
    visibility = models.CharField(max_length=100, blank=True, null=True)
    inherit_id = models.ForeignKey('self', on_delete=models.DO_NOTHING, db_column='inherit_id',
                                   blank=True, null=True, related_name='inherited_views')
    mode = models.CharField(max_length=20, default='primary')
    model_data = models.CharField(max_length=255, blank=True, null=True)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    arch = models.TextField(blank=True, null=True)
    template_path = models.CharField(max_length=255, blank=True, null=True)
    priority = models.IntegerField(default=16)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'ir_ui_view'

    def __str__(self):
        return self.name


class IrActions(models.Model):
    _name = 'ir.actions.act_window'
    _description = 'Actions'

    ACTION_TYPE_CHOICES = [
        ('ir.actions.act_window', 'ir.actions.act_window'),
        ('ir.actions.server', 'ir.actions.server'),
        ('ir.actions.report', 'ir.actions.report'),
        ('ir.actions.act_url', 'ir.actions.act_url'),
        ('ir.actions.client', 'ir.actions.client'),
    ]

    name = models.CharField(max_length=150)
    action_type = models.CharField(max_length=100, choices=ACTION_TYPE_CHOICES, default='ir.actions.act_window')
    res_model = models.CharField(max_length=100, blank=True, null=True)
    view_mode = models.CharField(max_length=100, default='list,form')
    domain = models.CharField(max_length=255, blank=True, null=True)
    context = models.CharField(max_length=255, blank=True, null=True)
    target = models.CharField(max_length=50, default='current')
    usage = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'ir_actions'

    def __str__(self):
        return self.name


class ReportPaperformat(models.Model):
    _name = 'report.paperformat'
    _description = 'Paper Format General Configuration'

    name = models.CharField(max_length=150, unique=True)
    format_size = models.CharField(max_length=50, default='A4', choices=[
        ('A4', 'A4 0 210 x 297 mm, 8.26 x 11.69 inches'),
        ('Letter', 'US Letter 0 215.9 x 279.4 mm, 8.5 x 11 inches'),
        ('Legal', 'US Legal 0 215.9 x 355.6 mm, 8.5 x 14 inches'),
        ('A3', 'A3 0 297 x 420 mm, 11.69 x 16.54 inches'),
        ('A5', 'A5 0 148 x 210 mm, 5.83 x 8.27 inches'),
        ('custom', 'Custom Dimensions'),
    ])
    page_height = models.IntegerField(default=0, help_text="Page height in mm")
    page_width = models.IntegerField(default=0, help_text="Page width in mm")
    orientation = models.CharField(max_length=20, default='Portrait', choices=[
        ('Portrait', 'Portrait'),
        ('Landscape', 'Landscape'),
    ])
    margin_top = models.DecimalField(max_digits=6, decimal_places=2, default=52.00)
    margin_bottom = models.DecimalField(max_digits=6, decimal_places=2, default=32.00)
    margin_left = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    margin_right = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    header_line = models.BooleanField(default=False)
    header_spacing = models.IntegerField(default=52)
    disable_shrinking = models.BooleanField(default=False)
    dpi = models.IntegerField(default=90)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'report_paperformat'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def associated_reports(self):
        return self.reports.filter(is_active=True).order_by('name')


class IrActionsReport(models.Model):
    _name = 'ir.actions.report'
    _description = 'Report Actions'

    REPORT_TYPE_CHOICES = [
        ('qweb-pdf', 'PDF'),
        ('qweb-html', 'HTML'),
        ('qweb-text', 'Text'),
    ]

    name = models.CharField(max_length=150)
    model = models.ForeignKey('IrModel', on_delete=models.SET_NULL, blank=True, null=True, related_name='reports')
    report_type = models.CharField(max_length=50, default='qweb-pdf', choices=REPORT_TYPE_CHOICES)
    paperformat = models.ForeignKey(ReportPaperformat, on_delete=models.SET_NULL, blank=True, null=True, related_name='reports')
    report_name = models.CharField(max_length=255)
    report_file = models.CharField(max_length=255, blank=True, null=True)
    filter_domain = models.CharField(max_length=255, blank=True, null=True)
    print_report_name = models.CharField(max_length=255, blank=True, null=True)
    attachment_use = models.BooleanField(default=False)
    attachment_prefix = models.CharField(max_length=255, blank=True, null=True)
    groups = models.ManyToManyField('ResGroups', blank=True, related_name='visible_reports')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ir_actions_report'
        ordering = ['name']

    def __str__(self):
        return self.name


class IrModelRelation(models.Model):
    _name = 'ir.model.relation'
    _description = 'ManyToMany Relations'

    name = models.CharField(max_length=150, unique=True)
    model = models.ForeignKey(IrModel, on_delete=models.DO_NOTHING, db_column='model_id', blank=True, null=True)
    module = models.ForeignKey(IrModule, on_delete=models.DO_NOTHING, db_column='module_id', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'ir_model_relation'

    def __str__(self):
        return self.name


class IrCron(models.Model):
    _name = 'ir.cron'
    _description = 'Scheduled Actions'

    INTERVAL_TYPE_CHOICES = [
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]

    name = models.CharField(max_length=255)
    model = models.ForeignKey(IrModel, on_delete=models.DO_NOTHING, db_column='model_id', blank=True, null=True)
    user = models.ForeignKey(ResUsers, on_delete=models.DO_NOTHING, db_column='user_id', blank=True, null=True)
    interval_number = models.IntegerField(default=1)
    interval_type = models.CharField(max_length=20, choices=INTERVAL_TYPE_CHOICES, default='days')
    priority = models.IntegerField(default=5)
    next_execution_date = models.DateTimeField(blank=True, null=True)
    code = models.TextField(default='model.process()', blank=True)
    allowed_groups = models.ForeignKey(ResGroups, on_delete=models.DO_NOTHING, db_column='allowed_group_id', blank=True, null=True)
    numbercall = models.IntegerField(default=-1)
    doall = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'ir_cron'

    def __str__(self):
        return self.name


class IrMailServer(models.Model):
    _name = 'ir.mail_server'
    _description = 'Mail Server'

    ENCRYPTION_CHOICES = [
        ('none', 'Never (Plain TCP)'),
        ('starttls', 'TLS (STARTTLS)'),
        ('ssl', 'SSL/TLS'),
    ]

    name = models.CharField(max_length=150, help_text="Server Description / Friendly Name")
    sequence = models.IntegerField(default=10, help_text="Lower priority servers are used first")
    smtp_host = models.CharField(max_length=255, default='localhost', help_text="Hostname or IP of SMTP server (e.g. smtp.gmail.com)")
    smtp_port = models.IntegerField(default=587, help_text="SMTP Port (e.g. 587 for STARTTLS, 465 for SSL, 25 for plain)")
    smtp_encryption = models.CharField(max_length=20, choices=ENCRYPTION_CHOICES, default='starttls')
    smtp_user = models.CharField(max_length=150, blank=True, null=True, help_text="Username/Email for SMTP authentication")
    smtp_pass = EncryptedCharField(max_length=512, blank=True, null=True, help_text="Password/App Password for SMTP authentication (stored encrypted)")
    smtp_debug = models.BooleanField(default=False, help_text="Show full SMTP transcript in logs")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ir_mail_server'
        ordering = ['sequence', 'name']

    def __str__(self):
        return f"{self.name} ({self.smtp_host}:{self.smtp_port})"

    def test_connection(self):
        """
        Performs a diagnostic test of the SMTP connection settings with stage tracking.
        Returns a dict: {'success': bool, 'message': str, 'banner': str, 'stage': str, 'details': str, 'latency_ms': int}
        """
        import smtplib
        import ssl
        import time
        import sys

        start_time = time.time()
        stage = "1. Initializing TCP Socket Connection"
        server = None

        try:
            timeout = 10
            if self.smtp_encryption == 'ssl':
                stage = f"1. Connecting SSL/TLS Socket to {self.smtp_host}:{self.smtp_port}"
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=timeout, context=context)
            else:
                stage = f"1. Connecting Plain/STARTTLS Socket to {self.smtp_host}:{self.smtp_port}"
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=timeout)

            if self.smtp_debug:
                server.set_debuglevel(1)

            stage = f"2. Exchanging EHLO Greeting with {self.smtp_host}"
            code, resp = server.ehlo()
            banner = resp.decode('utf-8', errors='ignore') if isinstance(resp, bytes) else str(resp)

            if self.smtp_encryption == 'starttls':
                stage = f"3. Negotiating STARTTLS Cryptographic Handshake"
                if not server.has_extn('starttls'):
                    server.quit()
                    return {
                        'success': False,
                        'stage': stage,
                        'message': f"STARTTLS is required by your configuration, but server {self.smtp_host}:{self.smtp_port} does not support STARTTLS extension.",
                        'details': f"Server response banner:\n{banner}",
                        'banner': banner,
                        'latency_ms': int((time.time() - start_time) * 1000)
                    }
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()

            if self.smtp_user and self.smtp_pass:
                stage = f"4. Authenticating User '{self.smtp_user}'"
                server.login(self.smtp_user, self.smtp_pass)

            stage = "5. Verifying Connection (NOOP keepalive)"
            status_code, status_msg = server.noop()
            server.quit()
            latency = int((time.time() - start_time) * 1000)

            return {
                'success': True,
                'stage': 'All Diagnostics Passed',
                'message': f"Connection successful! Server responded with code {status_code} ({latency}ms).",
                'details': f"Connected to {self.smtp_host}:{self.smtp_port} ({self.get_smtp_encryption_display()})\nServer Banner: {banner.strip()}",
                'banner': banner,
                'latency_ms': latency
            }
        except smtplib.SMTPAuthenticationError as e:
            err_msg = e.smtp_error.decode('utf-8', errors='ignore') if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
            return {
                'success': False,
                'stage': stage,
                'message': f"Authentication Failed at {stage}: {err_msg}",
                'details': f"File: base/models.py (IrMailServer.test_connection)\nProvider rejected credentials for user '{self.smtp_user}'. If using Gmail, make sure to use a 16-character App Password with 2FA enabled.",
                'banner': '',
                'latency_ms': int((time.time() - start_time) * 1000)
            }
        except smtplib.SMTPConnectError as e:
            return {
                'success': False,
                'stage': stage,
                'message': f"Connection Failed at {stage}: {e}",
                'details': f"File: base/models.py (IrMailServer.test_connection)\nUnable to establish TCP connection to {self.smtp_host}:{self.smtp_port}. Check hostname, port, and outbound firewall rules.",
                'banner': '',
                'latency_ms': int((time.time() - start_time) * 1000)
            }
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            line_no = exc_tb.tb_lineno if exc_tb else 'N/A'
            latency = int((time.time() - start_time) * 1000)

            # Contextual troubleshooting guidance
            hint = ""
            if "timed out" in str(e).lower() or "unexpectedly closed" in str(e).lower():
                if self.smtp_port == 587 and self.smtp_encryption == 'ssl':
                    hint = "\nTip: Port 587 requires 'TLS (STARTTLS)', not 'SSL/TLS'."
                elif self.smtp_port == 465 and self.smtp_encryption == 'starttls':
                    hint = "\nTip: Port 465 requires 'SSL/TLS', not 'TLS (STARTTLS)'."
                else:
                    hint = "\nTip: Server or firewall timed out without responding. Check if port is blocked by your ISP/network or verify port/encryption match."

            return {
                'success': False,
                'stage': stage,
                'message': f"Connection test failed at {stage}: {str(e)}",
                'details': f"Execution Point: base/models.py:L{line_no} ({exc_type.__name__})\nHost: {self.smtp_host}:{self.smtp_port} | Encryption: {self.smtp_encryption}{hint}",
                'banner': '',
                'latency_ms': latency
            }


class IrConfigParameter(models.Model):
    _name = 'ir.config_parameter'
    _description = 'System Parameters'

    key = models.CharField(max_length=150, unique=True, help_text="Parameter Key (e.g. web.base.url, session.timeout)")
    value = models.TextField(help_text="Parameter Value")
    description = models.TextField(blank=True, null=True, help_text="Parameter Documentation / Purpose")
    is_system = models.BooleanField(default=False, help_text="System-reserved parameter (cannot be deleted)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ir_config_parameter'
        ordering = ['key']

    def __str__(self):
        return f"{self.key} = {self.value[:30]}"

    @classmethod
    def get_param(cls, key, default=None):
        """Retrieves a configuration parameter value by key."""
        param = cls.objects.filter(key=key, is_active=True).first()
        return param.value if param else default

    @classmethod
    def set_param(cls, key, value, description=None, is_system=False):
        """Sets or creates a configuration parameter."""
        obj, created = cls.objects.get_or_create(
            key=key,
            defaults={
                'value': str(value),
                'description': description,
                'is_system': is_system,
                'is_active': True,
            }
        )
        if not created:
            obj.value = str(value)
            if description is not None:
                obj.description = description
            obj.save(update_fields=['value', 'description', 'updated_at'])
        return obj


def extract_diagnostics_from_exception(exc, request=None):
    """
    Extracts high-resolution diagnostic information from an exception:
    - Finds the exact project file, module, function name, and line number
    - Formats stack frames with code context
    - Computes contextual troubleshooting hints
    """
    import sys
    import traceback
    import os
    from django.conf import settings

    exc_type, exc_obj, exc_tb = sys.exc_info()
    if exc_type is None:
        exc_type = type(exc)
        exc_obj = exc

    raw_tb = traceback.extract_tb(exc_tb) if exc_tb else []
    base_dir_str = str(settings.BASE_DIR)

    app_frames = []
    for frame in raw_tb:
        filename = frame.filename
        is_project = base_dir_str in filename and 'site-packages' not in filename and 'venv' not in filename
        rel_path = os.path.relpath(filename, base_dir_str) if is_project else filename
        app_frames.append({
            'filename': rel_path.replace('\\', '/'),
            'abs_filename': filename.replace('\\', '/'),
            'lineno': frame.lineno,
            'name': frame.name,
            'line': frame.line,
            'is_project': is_project,
        })

    target_frame = None
    for frame in reversed(app_frames):
        if frame['is_project']:
            target_frame = frame
            break
    if not target_frame and app_frames:
        target_frame = app_frames[-1]

    file_name = target_frame['filename'] if target_frame else 'N/A'
    line_no = target_frame['lineno'] if target_frame else 0
    func_name = target_frame['name'] if target_frame else 'N/A'
    code_line = target_frame['line'] if target_frame else ''
    exc_name = exc_type.__name__ if hasattr(exc_type, '__name__') else str(exc_type)
    exc_message = str(exc)

    hint = ""
    lower_msg = exc_message.lower()
    if issubclass(exc_type, KeyError):
        hint = f"A required dictionary key or parameter {exc_message} was not found in the payload/request."
    elif issubclass(exc_type, AttributeError) and "'nonetype' object has no attribute" in lower_msg:
        hint = "A database query or lookup returned None instead of an expected model instance. Verify database records or add a null-check."
    elif any(k in lower_msg for k in ['no such table', 'column', 'relation', 'does not exist']):
        hint = "Database schema mismatch detected. Try running database migrations ('python manage.py makemigrations' and 'python manage.py migrate')."
    elif "timed out" in lower_msg or "connection refused" in lower_msg or "unexpectedly closed" in lower_msg:
        hint = "Network connection failed or timed out. Check firewall settings, target host reachability, or port/encryption protocol configuration."
    elif issubclass(exc_type, PermissionError) or "permission denied" in lower_msg:
        hint = "Access was rejected due to insufficient system privileges, security record rules, or filesystem permissions."

    full_traceback = ''.join(traceback.format_exception(exc_type, exc_obj, exc_tb)) if exc_tb else str(exc)

    return {
        'error_type': exc_name,
        'message': exc_message,
        'file': file_name,
        'line': line_no,
        'function': func_name,
        'code_context': code_line,
        'frames': app_frames,
        'traceback': full_traceback,
        'hint': hint,
        'request_url': request.path if request else '',
        'request_method': request.method if request else '',
    }


class IrLogging(models.Model):
    _name = 'ir.logging'
    _description = 'Logging & Diagnostics'

    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    TYPE_CHOICES = [
        ('server', 'Server Exception'),
        ('client', 'Frontend / AJAX Error'),
        ('cron', 'Scheduled Action'),
        ('mail', 'Mail / SMTP'),
        ('security', 'Access Control / Security'),
    ]

    name = models.CharField(max_length=255, default='root', help_text="Logger or module name")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='server')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='ERROR')
    message = models.TextField(help_text="Error message / headline")
    path = models.CharField(max_length=500, blank=True, null=True, help_text="Source file relative path")
    func_name = models.CharField(max_length=150, blank=True, null=True, help_text="Function / method name")
    line_no = models.IntegerField(blank=True, null=True, help_text="Offending line number")
    traceback = models.TextField(blank=True, null=True, help_text="Full diagnostic stack trace")
    request_url = models.CharField(max_length=1000, blank=True, null=True)
    request_method = models.CharField(max_length=10, blank=True, null=True)
    user = models.ForeignKey('ResUsers', on_delete=models.SET_NULL, blank=True, null=True, related_name='ir_logs')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ir_logging'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"[{self.level}] {self.name}: {self.message[:60]} ({self.path}:{self.line_no})"

    @classmethod
    def log_exception(cls, exc, request=None, level='ERROR', log_type='server', name=None):
        """Creates a high-resolution diagnostic log entry from an exception."""
        diag = extract_diagnostics_from_exception(exc, request=request)
        user = None
        if request and hasattr(request, 'session'):
            from authentication.auth_helpers import get_current_ir_user
            try:
                user = get_current_ir_user(request)
            except Exception:
                user = None

        logger_name = name or diag['file'] or 'root'
        try:
            return cls.objects.create(
                name=logger_name[:255],
                type=log_type,
                level=level,
                message=diag['message'] or str(exc),
                path=diag['file'][:500] if diag['file'] else '',
                func_name=diag['function'][:150] if diag['function'] else '',
                line_no=diag['line'],
                traceback=diag['traceback'],
                request_url=diag['request_url'][:1000] if diag['request_url'] else '',
                request_method=diag['request_method'][:10] if diag['request_method'] else '',
                user=user if getattr(user, 'id', None) else None,
                is_active=True,
            )
        except Exception:
            return None


class Project(models.Model):
    _name = 'project.project'
    _description = 'Project'

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, default='In Progress')
    manager = models.ForeignKey('employee.Employee', on_delete=models.RESTRICT, db_column='manager_id', related_name='managed_projects')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'project'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProjectMember(models.Model):
    _name = 'project.member'
    _description = 'Project Member'

    project = models.ForeignKey(Project, on_delete=models.RESTRICT, db_column='project_id', related_name='members')
    employee = models.ForeignKey('employee.Employee', on_delete=models.RESTRICT, db_column='employee_id', related_name='project_memberships')
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'project_member'
        unique_together = (('project', 'employee'),)

    def __str__(self):
        return f"{self.employee.name} in {self.project.name}"


class Timesheet(models.Model):
    _name = 'account.analytic.line'
    _description = 'Timesheet Task'

    employee = models.ForeignKey('employee.Employee', on_delete=models.RESTRICT, db_column='employee_id', related_name='timesheets')
    project = models.ForeignKey(Project, on_delete=models.RESTRICT, db_column='project_id', related_name='timesheets')
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2)
    task_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Draft')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'timesheet'
        ordering = ['-date']

    def __str__(self):
        return f"{self.task_description} ({self.hours_worked}h)"