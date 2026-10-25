"""
Management command: seed_technical_defaults

Seeds standard ERP technical records:
1. IrActions (ir.actions.act_window) for all ERP models
2. IrSequence (ir.sequence) for document numbering (employees, leaves, attendances, etc.)
3. IrCron (ir.cron) scheduled actions for background jobs (mail queue, checkout, log pruning)

Safe to re-run: uses update_or_create to avoid duplicate records.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from base.models import IrModel, IrActions, IrSequence, IrCron, ResCompany, ResUsers, ResGroups


class Command(BaseCommand):
    help = 'Seed standard technical defaults: Window Actions, Sequences, and Scheduled Actions (Cron)'

    def handle(self, *args, **options):
        self.stdout.write("Seeding IrActions (Window Actions)...")
        actions_data = [
            # Human Resources & Employees
            {'name': 'Employees', 'action_type': 'ir.actions.act_window', 'res_model': 'hr.employee', 'view_mode': 'kanban,list,form'},
            {'name': 'Departments', 'action_type': 'ir.actions.act_window', 'res_model': 'hr.department', 'view_mode': 'kanban,list,form'},
            {'name': 'Onboarding Plans', 'action_type': 'ir.actions.act_window', 'res_model': 'hr.employee.onboarding', 'view_mode': 'list,form'},
            # Time Off
            {'name': 'Time Off Requests', 'action_type': 'ir.actions.act_window', 'res_model': 'hr.leave', 'view_mode': 'calendar,list,form,kanban'},
            {'name': 'Allocations', 'action_type': 'ir.actions.act_window', 'res_model': 'hr.leave.allocation', 'view_mode': 'list,form'},
            {'name': 'Time Off Types', 'action_type': 'ir.actions.act_window', 'res_model': 'hr.leave.type', 'view_mode': 'list,form'},
            {'name': 'Public Holidays', 'action_type': 'ir.actions.act_window', 'res_model': 'hr.leave.mandatory.day', 'view_mode': 'list,form'},
            # Attendance
            {'name': 'Attendances', 'action_type': 'ir.actions.act_window', 'res_model': 'attendance.attendance', 'view_mode': 'list,form'},
            # Users & Access Control
            {'name': 'Users', 'action_type': 'ir.actions.act_window', 'res_model': 'res.users', 'view_mode': 'list,form'},
            {'name': 'User Groups', 'action_type': 'ir.actions.act_window', 'res_model': 'res.groups', 'view_mode': 'list,form'},
            {'name': 'Privileges', 'action_type': 'ir.actions.act_window', 'res_model': 'res.privilege', 'view_mode': 'list,form'},
            {'name': 'Companies', 'action_type': 'ir.actions.act_window', 'res_model': 'res.company', 'view_mode': 'list,form'},
            {'name': 'Contacts / Partners', 'action_type': 'ir.actions.act_window', 'res_model': 'res.partner', 'view_mode': 'kanban,list,form'},
            # Technical Structure
            {'name': 'Database Models', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.model', 'view_mode': 'list,form'},
            {'name': 'Model Fields', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.model.fields', 'view_mode': 'list,form'},
            {'name': 'User Interface Views', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.ui.view', 'view_mode': 'list,form'},
            {'name': 'Menu Items', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.ui.menu', 'view_mode': 'list,form'},
            {'name': 'Sequences', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.sequence', 'view_mode': 'list,form'},
            {'name': 'Scheduled Actions (Cron)', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.cron', 'view_mode': 'list,form'},
            {'name': 'Access Rights', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.model.access', 'view_mode': 'list,form'},
            {'name': 'Record Rules', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.rule', 'view_mode': 'list,form'},
            {'name': 'Reports', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.actions.report', 'view_mode': 'list,form'},
            {'name': 'Paper Formats', 'action_type': 'ir.actions.act_window', 'res_model': 'report.paperformat', 'view_mode': 'list,form'},
            {'name': 'Outgoing Mail Servers', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.mail_server', 'view_mode': 'list,form'},
            {'name': 'System Logging', 'action_type': 'ir.actions.act_window', 'res_model': 'ir.logging', 'view_mode': 'list,form'},
            # Mail & Discuss
            {'name': 'Mail Messages', 'action_type': 'ir.actions.act_window', 'res_model': 'mail.message', 'view_mode': 'list,form'},
            {'name': 'Mail Channels', 'action_type': 'ir.actions.act_window', 'res_model': 'mail.channel', 'view_mode': 'kanban,list,form'},
            {'name': 'Activities', 'action_type': 'ir.actions.act_window', 'res_model': 'mail.activity', 'view_mode': 'list,form'},
        ]

        action_count = 0
        for ad in actions_data:
            _, created = IrActions.objects.update_or_create(
                name=ad['name'],
                defaults={
                    'action_type': ad['action_type'],
                    'res_model': ad['res_model'],
                    'view_mode': ad['view_mode'],
                    'target': 'current',
                    'is_active': True,
                }
            )
            action_count += 1
        self.stdout.write(f"  Processed {action_count} IrActions.")

        self.stdout.write("Seeding IrSequence (Sequences)...")
        company = ResCompany.objects.first()
        sequences_data = [
            {'code': 'hr.employee', 'name': 'Employee Badge ID', 'prefix': 'EMP/', 'padding': 5, 'next_number': 1001, 'step': 1, 'implementation': 'standard'},
            {'code': 'hr.leave', 'name': 'Time Off Request Reference', 'prefix': 'LEAVE/%(range_year)s/', 'padding': 5, 'next_number': 1, 'step': 1, 'use_date_range': True, 'implementation': 'standard'},
            {'code': 'hr.leave.allocation', 'name': 'Time Off Allocation Reference', 'prefix': 'ALLOC/%(range_year)s/', 'padding': 5, 'next_number': 1, 'step': 1, 'use_date_range': True, 'implementation': 'standard'},
            {'code': 'attendance.attendance', 'name': 'Attendance Check-in Badge', 'prefix': 'ATT/', 'padding': 6, 'next_number': 1, 'step': 1, 'implementation': 'standard'},
            {'code': 'mail.message', 'name': 'Chatter Message Serial', 'prefix': 'MSG/', 'padding': 6, 'next_number': 1, 'step': 1, 'implementation': 'standard'},
            {'code': 'res.partner', 'name': 'Contact / Partner Code', 'prefix': 'PART/', 'padding': 5, 'next_number': 1, 'step': 1, 'implementation': 'standard'},
            {'code': 'ir.logging', 'name': 'Diagnostics Log Sequence', 'prefix': 'LOG/', 'padding': 6, 'next_number': 1, 'step': 1, 'implementation': 'standard'},
            {'code': 'ir.attachment', 'name': 'Document Attachment Identifier', 'prefix': 'DOC/', 'padding': 5, 'next_number': 1, 'step': 1, 'implementation': 'standard'},
            {'code': 'project.task', 'name': 'Project Task Reference', 'prefix': 'TASK/', 'padding': 5, 'next_number': 1, 'step': 1, 'implementation': 'standard'},
        ]

        seq_count = 0
        for sd in sequences_data:
            _, created = IrSequence.objects.update_or_create(
                code=sd['code'],
                defaults={
                    'name': sd['name'],
                    'prefix': sd['prefix'],
                    'padding': sd['padding'],
                    'next_number': sd['next_number'],
                    'step': sd['step'],
                    'use_date_range': sd.get('use_date_range', False),
                    'implementation': sd['implementation'],
                    'company': company,
                    'is_active': True,
                }
            )
            seq_count += 1
        self.stdout.write(f"  Processed {seq_count} IrSequences.")

        self.stdout.write("Seeding IrCron (Scheduled Actions)...")
        admin_user = (
            ResUsers.objects.filter(username__in=['admin', 'administrator', 'tech_admin'], is_active=True).first()
            or ResUsers.objects.filter(is_active=True).first()
        )
        now = timezone.now()

        cron_configs = [
            {
                'name': 'Mail: Email Queue Manager',
                'model_name': 'mail.message',
                'interval_number': 5,
                'interval_type': 'minutes',
                'priority': 5,
                'code': 'model.process_email_queue()',
            },
            {
                'name': 'Attendance: Auto Checkout Incomplete Shifts',
                'model_name': 'attendance.attendance',
                'interval_number': 1,
                'interval_type': 'days',
                'priority': 10,
                'code': 'model.auto_checkout_incomplete()',
            },
            {
                'name': 'Time Off: Accrual Allocation Plan',
                'model_name': 'hr.leave.allocation',
                'interval_number': 1,
                'interval_type': 'days',
                'priority': 12,
                'code': 'model.run_accrual_allocations()',
            },
            {
                'name': 'Diagnostics: Prune Old System Logs',
                'model_name': 'ir.logging',
                'interval_number': 7,
                'interval_type': 'days',
                'priority': 20,
                'code': 'model.prune_old_logs(days=30)',
            },
            {
                'name': 'Security: Clean Expired User Sessions',
                'model_name': 'res.users',
                'interval_number': 1,
                'interval_type': 'days',
                'priority': 25,
                'code': 'model.clean_expired_sessions()',
            },
            {
                'name': 'HR: Work Anniversary & Birthday Reminders',
                'model_name': 'hr.employee',
                'interval_number': 1,
                'interval_type': 'days',
                'priority': 15,
                'code': 'model.send_anniversary_notifications()',
            },
        ]

        cron_count = 0
        for cc in cron_configs:
            model_obj = IrModel.objects.filter(model_name=cc['model_name']).first()
            _, created = IrCron.objects.update_or_create(
                name=cc['name'],
                defaults={
                    'model': model_obj,
                    'user': admin_user,
                    'interval_number': cc['interval_number'],
                    'interval_type': cc['interval_type'],
                    'priority': cc['priority'],
                    'code': cc['code'],
                    'next_execution_date': now + timezone.timedelta(minutes=cc['interval_number'] if cc['interval_type'] == 'minutes' else 60),
                    'numbercall': -1,
                    'doall': False,
                    'is_active': True,
                }
            )
            cron_count += 1
        self.stdout.write(f"  Processed {cron_count} IrCron scheduled actions.")

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded Technical Defaults: {action_count} actions, {seq_count} sequences, {cron_count} cron jobs."
        ))
