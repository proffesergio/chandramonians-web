"""Restore missing membership records and alumni profiles from a local backup."""
from pathlib import Path
from contextlib import closing
import sqlite3

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from app.models import Alumni, CustomUser, MembershipPayment


class Command(BaseCommand):
    help = 'Restore missing community records from SQLite without overwriting live records.'

    def add_arguments(self, parser):
        parser.add_argument('--source', required=True)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        source = Path(options['source']).resolve()
        if not source.is_file():
            raise CommandError('Backup SQLite file does not exist.')
        from django.conf import settings
        target = settings.DATABASES['default']
        if target['ENGINE'].endswith('sqlite3') and Path(target['NAME']).resolve() == source:
            raise CommandError('Source and target databases must be different.')
        try:
            with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as backup:
                backup.row_factory = sqlite3.Row
                members = [dict(row) for row in backup.execute('SELECT * FROM app_membershippayment')]
                alumni = [dict(row) for row in backup.execute('SELECT * FROM app_alumni')]
                users = {row['id']: dict(row) for row in backup.execute('SELECT * FROM app_customuser')}
        except sqlite3.Error as exc:
            raise CommandError('The source must be a valid Chandramonians SQLite backup.') from exc

        member_fields = (
            'member_name', 'payment_date', 'amount', 'receipt_number',
            'batch_year', 'phone', 'status',
        )
        alumni_fields = ('address', 'gender', 'passing_year', 'phone', 'profession', 'company', 'linkedin_url', 'bio')
        counts = {'members_added': 0, 'members_kept': 0, 'alumni_added': 0, 'alumni_kept': 0}
        with transaction.atomic():
            for record in members:
                _, created = MembershipPayment.objects.get_or_create(
                    member_type=record['member_type'], sheet_row_id=record['sheet_row_id'],
                    defaults={field: record[field] for field in member_fields},
                )
                counts['members_added' if created else 'members_kept'] += 1
            for record in alumni:
                original = users.get(record['admin_id'])
                if not original or not original['email']:
                    raise CommandError('An alumni profile has no linked email; restoration rolled back.')
                user = CustomUser.objects.filter(email__iexact=original['email']).first()
                if user is None:
                    username = original['username']
                    if CustomUser.objects.filter(username=username).exists():
                        raise CommandError('An alumni username conflicts with a live account; restoration rolled back.')
                    user = CustomUser(
                        email=original['email'], username=username,
                        first_name=original['first_name'], last_name=original['last_name'],
                        user_type='3', is_staff=False, is_superuser=False,
                    )
                    # Restore directory information, never old passwords or privileges.
                    user.set_unusable_password()
                    user.save()
                _, created = Alumni.objects.get_or_create(
                    admin=user, defaults={field: record.get(field) or '' for field in alumni_fields},
                )
                counts['alumni_added' if created else 'alumni_kept'] += 1
            if options['dry_run']:
                transaction.set_rollback(True)
        prefix = 'Dry run (rolled back)' if options['dry_run'] else 'Restoration complete'
        self.stdout.write(f'{prefix}: {counts}')
        self.stdout.write(
            f'Live totals: memberships={MembershipPayment.objects.count()}, alumni={Alumni.objects.count()}'
        )
