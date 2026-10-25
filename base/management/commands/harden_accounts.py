"""
One-time (and safe to re-run) account hardening after upgrading to the secured authentication code.

    python manage.py harden_accounts              # apply
    python manage.py harden_accounts --dry-run    # only report

What it does
1. Hashes any password that is still stored as PLAINTEXT (the old code accepted these).
2. Keeps legitimate administrators working: the old code treated usernames admin / administrator /
   root and e-mails starting with "admin@" as super-admins automatically.  That shortcut is gone, so
   those existing accounts are added to the 'Administrator' group first -- review the printed list
   and remove anyone who should not be an admin.
3. Re-saves outgoing mail server (SMTP) passwords so they are stored encrypted.
4. Reports every account that still uses a known default password such as "123".  Those users are
   forced to change it at next login.
"""
from django.contrib.auth.hashers import identify_hasher, make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from authentication.auth_helpers import uses_known_weak_password
from base.models import IrMailServer, ResGroups, ResUsers, ResUsersGroups


def _is_hashed(value):
    try:
        identify_hasher(value)
        return True
    except ValueError:
        return False


class Command(BaseCommand):
    help = 'Hash plaintext passwords, grandfather legacy admin accounts into the Administrator group, report weak passwords.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Report only; change nothing.')

    @transaction.atomic
    def handle(self, *args, **options):
        dry = options['dry_run']
        prefix = '[dry-run] ' if dry else ''

        # 1. plaintext -> hashed
        hashed = 0
        for user in ResUsers.objects.all():
            if user.password_hash and not _is_hashed(user.password_hash):
                self.stdout.write(self.style.WARNING(f'{prefix}plaintext password found for "{user.username}" -> hashing'))
                if not dry:
                    user.password_hash = make_password(user.password_hash)
                    user.save(update_fields=['password_hash', 'updated_at'])
                hashed += 1

        # 2. legacy implicit admins -> explicit group membership
        admin_group = ResGroups.objects.filter(name__iexact='Administrator', privilege__iexact='General').first() or ResGroups.objects.filter(name__iexact='Administrator').first()
        if admin_group is None and not dry:
            admin_group = ResGroups.objects.create(name='Administrator', privilege='General', is_active=True)
        legacy = [
            u for u in ResUsers.objects.filter(is_active=True)
            if u.username.lower() in ('admin', 'administrator', 'root') or (u.email or '').lower().startswith('admin@')
        ]
        for user in legacy:
            exists = admin_group is not None and ResUsersGroups.objects.filter(user=user, group=admin_group).exists()
            if not exists:
                self.stdout.write(self.style.WARNING(
                    f'{prefix}"{user.username}" <{user.email}> was an implicit admin -> adding to Administrator group (REVIEW THIS)'))
                if not dry:
                    ResUsersGroups.objects.update_or_create(user=user, group=admin_group, defaults={'is_active': True})

        # 3. weak password report
        weak = [u for u in ResUsers.objects.filter(is_active=True) if uses_known_weak_password(u)]
        for user in weak:
            self.stdout.write(self.style.ERROR(f'{prefix}"{user.username}" still uses a known default password -> will be forced to change at next login'))

        # 4. SMTP passwords: re-save so legacy plaintext values get encrypted at rest
        encrypted = 0
        for server in IrMailServer.objects.exclude(smtp_pass__isnull=True).exclude(smtp_pass=''):
            if not dry:
                server.save(update_fields=['smtp_pass'])
            encrypted += 1
        if encrypted:
            self.stdout.write(f'{prefix}{encrypted} outgoing mail server password(s) stored encrypted')

        self.stdout.write(self.style.SUCCESS(
            f'{prefix}done: {hashed} plaintext password(s) hashed, {len(legacy)} legacy admin(s) checked, {len(weak)} weak-password account(s) found.'))
