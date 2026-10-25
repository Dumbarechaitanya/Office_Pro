"""
Management command: seed_ir_views

Inserts list, form, and search view rows into ir_ui_view for every
active IrModel. Re-running is safe: uses update_or_create on name+model
so no duplicates -- avoids external_id until the column exists.

Run order:
    python manage.py sync_ir_models
    python manage.py seed_ir_views
"""
from django.core.management.base import BaseCommand
from base.models import IrModel, IrUiView

BASE_VIEW_TYPES = ['list', 'form', 'search']

KANBAN_MODELS = {
    'ir.model',
    'ir.ui.view',
    'ir.ui.menu',
    'hr.employee',
    'hr.department',
    'hr.leave',
    'res.partner',
    'mail.channel',
}

TEMPLATE_MAP = {
    ('ir.model',        'list'):   'base/technical_models.html',
    ('ir.model',        'form'):   'base/technical_model_detail.html',
    ('ir.model',        'search'): 'base/technical_models.html',
    ('ir.ui.view',      'list'):   'base/technical_views.html',
    ('ir.ui.view',      'form'):   'base/technical_view_detail.html',
    ('ir.ui.view',      'search'): 'base/technical_views.html',
    ('ir.ui.menu',      'list'):   'base/technical_menu_items.html',
    ('ir.ui.menu',      'form'):   'base/technical_menu_item_detail.html',
    ('ir.ui.menu',      'search'): 'base/technical_menu_items.html',
    ('ir.sequence',     'list'):   'base/technical_sequences.html',
    ('ir.sequence',     'form'):   'base/technical_sequence_detail.html',
    ('ir.sequence',     'search'): 'base/technical_sequences.html',
    ('ir.model.access', 'list'):   'base/technical_access_rights.html',
    ('ir.model.access', 'form'):   'base/technical_access_right_detail.html',
    ('ir.model.access', 'search'): 'base/technical_access_rights.html',
    ('ir.rule',         'list'):   'base/technical_record_rules.html',
    ('ir.rule',         'form'):   'base/technical_record_rule_detail.html',
    ('ir.rule',         'search'): 'base/technical_record_rules.html',
    ('res.users',       'list'):   'base/settings_users.html',
    ('res.users',       'form'):   'base/settings_user_detail.html',
    ('res.users',       'search'): 'base/settings_users.html',
    ('res.groups',      'list'):   'base/settings_groups.html',
    ('res.groups',      'form'):   'base/settings_group_detail.html',
    ('res.groups',      'search'): 'base/settings_groups.html',
    ('res.privilege',   'list'):   'base/settings_privileges.html',
    ('res.privilege',   'form'):   'base/settings_privilege_detail.html',
    ('res.privilege',   'search'): 'base/settings_privileges.html',
    ('res.company',     'list'):   'base/settings_companies.html',
    ('res.company',     'form'):   'base/settings_company_detail.html',
    ('res.company',     'search'): 'base/settings_companies.html',
    ('res.partner',     'list'):   'base/settings_partners.html',
    ('res.partner',     'form'):   'base/settings_partner_detail.html',
    ('res.partner',     'search'): 'base/settings_partners.html',
    ('hr.employee',     'list'):   'base/employee_list.html',
    ('hr.employee',     'form'):   'base/employee_detail.html',
    ('hr.employee',     'search'): 'base/employee_list.html',
    ('hr.department',   'list'):   'employee/department_list.html',
    ('hr.department',   'form'):   'employee/department_detail.html',
    ('hr.department',   'search'): 'employee/department_list.html',
    ('hr.leave',        'list'):   'leave/leave_management_requests.html',
    ('hr.leave',        'form'):   'leave/leave_request_detail.html',
    ('hr.leave',        'search'): 'leave/leave_management_requests.html',
    ('hr.leave.allocation', 'list'): 'leave/leave_management_allocations.html',
    ('hr.leave.allocation', 'form'): 'leave/leave_allocation_detail.html',
    ('hr.leave.allocation', 'search'): 'leave/leave_management_allocations.html',
    ('hr.leave.type',   'list'):   'leave/configuration_types.html',
    ('hr.leave.type',   'form'):   'leave/leave_type_detail.html',
    ('hr.leave.type',   'search'): 'leave/configuration_types.html',
    ('hr.leave.mandatory.day', 'list'): 'leave/configuration_mandatory_days.html',
    ('hr.leave.mandatory.day', 'form'): 'leave/mandatory_day_detail.html',
    ('hr.leave.mandatory.day', 'search'): 'leave/configuration_mandatory_days.html',
    ('attendance.attendance', 'list'): 'attendance/attendance_list.html',
    ('attendance.attendance', 'form'): 'attendance/attendance_detail.html',
    ('attendance.attendance', 'search'): 'attendance/attendance_list.html',
    ('ir.actions.act_window', 'list'): 'base/technical_actions.html',
    ('ir.actions.act_window', 'form'): 'base/technical_action_detail.html',
    ('ir.actions.act_window', 'search'): 'base/technical_actions.html',
    ('ir.cron',         'list'):   'base/technical_cron.html',
    ('ir.cron',         'form'):   'base/technical_cron_detail.html',
    ('ir.cron',         'search'): 'base/technical_cron.html',
    ('ir.logging',      'list'):   'base/technical_logging.html',
    ('ir.logging',      'form'):   'base/technical_log_detail.html',
    ('ir.logging',      'search'): 'base/technical_logging.html',
    ('ir.mail_server',  'list'):   'base/technical_outgoing_mail.html',
    ('ir.mail_server',  'form'):   'base/technical_outgoing_mail_detail.html',
    ('ir.mail_server',  'search'): 'base/technical_outgoing_mail.html',
    ('report.paperformat', 'list'): 'base/technical_paperformats.html',
    ('report.paperformat', 'form'): 'base/technical_paperformat_detail.html',
    ('report.paperformat', 'search'): 'base/technical_paperformats.html',
    ('ir.actions.report', 'list'): 'base/technical_reports.html',
    ('ir.actions.report', 'form'): 'base/technical_report_detail.html',
    ('ir.actions.report', 'search'): 'base/technical_reports.html',
}



class Command(BaseCommand):
    help = 'Seed ir_ui_view with list/form/search rows for every IrModel'

    def handle(self, *args, **options):
        # Detect whether external_id column exists yet
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name='ir_ui_view' AND column_name='external_id'
            """)
            has_external_id = cursor.fetchone() is not None

        if not has_external_id:
            self.stdout.write(self.style.WARNING(
                'external_id column not found in ir_ui_view -- '
                'run sql/ir_ui_view_new_columns.sql first to add it. '
                'Seeding without external_id for now (using name+model as unique key).'
            ))

        from base.models import IrModelFields

        models = IrModel.objects.filter(is_active=True)
        created_count = 0
        updated_count = 0

        for ir_model in models:
            app_label, model_slug = ir_model.model_name.split('.', 1)
            view_types = list(BASE_VIEW_TYPES)
            fields_qs = IrModelFields.objects.filter(model=ir_model, is_active=True).order_by('id')

            if ir_model.model_name in KANBAN_MODELS:
                view_types.append('kanban')

            for vtype in view_types:
                name = f'{ir_model.model_name}.{vtype}'
                template_path = TEMPLATE_MAP.get((ir_model.model_name, vtype), '')
                external_id_val = f"{ir_model.model_name.replace('.', '_')}_{vtype}_view"


                # Generate Odoo-like XML arch
                field_names = [f.field_name for f in fields_qs]
                if not field_names:
                    field_names = ['name', 'is_active', 'created_at']
                if vtype == 'list':
                    inner = "\n    ".join(f'<field name="{fn}"/>' for fn in field_names[:8])
                    arch_val = f'<tree string="{ir_model.description or model_slug}">\n    {inner}\n</tree>'
                elif vtype == 'form':
                    half = max(1, len(field_names) // 2)
                    left = "\n            ".join(f'<field name="{fn}"/>' for fn in field_names[:half])
                    right = "\n            ".join(f'<field name="{fn}"/>' for fn in field_names[half:half*2])
                    arch_val = f'<form string="{ir_model.description or model_slug}">\n    <sheet>\n        <group>\n            <group>\n            {left}\n            </group>\n            <group>\n            {right}\n            </group>\n        </group>\n    </sheet>\n</form>'
                elif vtype == 'search':
                    inner = "\n    ".join(f'<field name="{fn}"/>' for fn in field_names[:4])
                    arch_val = f'<search string="Search {ir_model.description or model_slug}">\n    {inner}\n    <filter string="Active" name="active" domain="[(\'is_active\', \'=\', True)]"/>\n</search>'
                elif vtype == 'kanban':
                    arch_val = f'<kanban>\n    <field name="name"/>\n    <templates>\n        <t t-name="kanban-box">\n            <div class="oe_kanban_card">\n                <div class="oe_kanban_global_click">\n                    <strong><field name="name"/></strong>\n                </div>\n            </div>\n        </t>\n    </templates>\n</kanban>'
                else:
                    arch_val = f'<{vtype}>\n</{vtype}>'

                defaults = {
                    'view_type': vtype,
                    'model': ir_model,
                    'template_path': template_path,
                    'priority': 16,
                    'mode': 'primary',
                    'model_data': name,
                    'external_id': external_id_val,
                    'arch': arch_val,
                    'is_active': True,
                }

                obj, created = IrUiView.objects.update_or_create(
                    name=name,
                    defaults=defaults,
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  created: {name} ({vtype})')
                else:
                    updated_count += 1
                    self.stdout.write(f'  updated: {name} ({vtype})')


        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {created_count} created, {updated_count} updated.'
        ))
