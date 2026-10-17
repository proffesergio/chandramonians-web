import io
from contextlib import closing
import os
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.contrib.auth import authenticate
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from app.models import Alumni, CustomUser, MembershipPayment
from webapp.sheets_sync import _parse_value, sync_all, sync_sheet_tab


class CommunityAccessTests(TestCase):
    def test_directories_show_profiles_and_apply_search_with_batch(self):
        user = CustomUser.objects.create_user(username='example', email='example@example.com', first_name='Example', last_name='Alum', user_type='3')
        Alumni.objects.create(admin=user, gender='', passing_year='2000', profession='Engineer', phone='01700000000')
        other = CustomUser.objects.create_user(username='other', email='other@example.com', first_name='Another', last_name='Graduate', user_type='3')
        Alumni.objects.create(admin=other, gender='', passing_year='2005')
        response = self.client.get(reverse('public_directory'), {'q': 'Example', 'batch': '2000'})
        self.assertContains(response, 'Example Alum')
        self.assertNotContains(response, 'Another Graduate')
        self.assertNotContains(response, '01700000000')
        self.assertEqual(len(response.context['alumni_list']), 1)
        self.client.force_login(user)
        response = self.client.get(reverse('alumni_directory'), {'q': 'Engineer', 'batch': '2000'})
        self.assertContains(response, 'Example Alum')
        self.assertContains(response, 'Batch of 2000')
        self.assertNotContains(response, 'Another Graduate')
        response = self.client.get(reverse('public_directory'), {'q': 'Example', 'batch': '2005'})
        self.assertContains(response, 'No results found')

    def test_email_login_and_inactive_account(self):
        user = CustomUser.objects.create_user(username='member', email='member@example.com', password='Community!Strong2026', user_type='3')
        self.assertEqual(authenticate(username='MEMBER@example.com', password='Community!Strong2026'), user)
        user.is_active = False
        user.save()
        self.assertIsNone(authenticate(username=user.email, password='Community!Strong2026'))

    def test_public_signup_cannot_create_privileged_accounts(self):
        for role in ('1', '2'):
            with self.subTest(role=role):
                self.client.post(reverse('doRegister'), {
                    'username': 'unauthorized', 'email': 'unauthorized@example.com',
                    'user_type': role, 'password': 'Community!Strong2026', 'confirm_password': 'Community!Strong2026',
                })
                self.assertFalse(CustomUser.objects.filter(username='unauthorized').exists())

    def test_signup_form_creates_linked_alumni_profile(self):
        response = self.client.post(reverse('doRegister'), {
            'username': 'newalum', 'email': 'newalum@example.com', 'first_name': 'New', 'last_name': 'Alum',
            'user_type': '3', 'password': 'Community!Strong2026', 'confirm_password': 'Community!Strong2026',
        })
        self.assertRedirects(response, reverse('landing'))
        user = CustomUser.objects.get(username='newalum')
        self.assertTrue(Alumni.objects.filter(admin=user).exists())
        self.assertFalse(user.is_staff or user.is_superuser)

    @patch.dict(os.environ, {'DJANGO_SUPERUSER_PASSWORD': 'Community!Strong2026'})
    def test_super_admin_can_login_to_both_panels(self):
        call_command('createcommunityadmin', email='admin@example.com', username='communityadmin', noinput=True, stdout=io.StringIO())
        user = CustomUser.objects.get(email='admin@example.com')
        self.assertTrue(user.is_superuser and user.is_staff)
        self.assertEqual(user.user_type, '1')
        self.assertTrue(self.client.login(username=user.email, password='Community!Strong2026'))
        self.assertEqual(self.client.get('/admin/').status_code, 200)
        self.assertEqual(self.client.get(reverse('hod_home')).status_code, 200)

    @patch.dict(os.environ, {'DJANGO_SUPERUSER_PASSWORD': '123'})
    def test_admin_command_rejects_weak_password(self):
        with self.assertRaises(CommandError):
            call_command('createcommunityadmin', email='admin@example.com', username='communityadmin', noinput=True)
        self.assertFalse(CustomUser.objects.exists())


class SheetSyncTests(TestCase):
    def test_payment_status_does_not_mark_unpaid_as_paid(self):
        for raw, expected in [('Unpaid', 'PENDING'), ('Not paid', 'PENDING'), ('Partially paid', 'PARTIAL'), ('Paid', 'PAID'), ('Unknown', 'PENDING')]:
            with self.subTest(raw=raw):
                self.assertEqual(_parse_value('status', raw), expected)

    def test_named_tab_and_title_row_are_supported(self):
        sheet = Mock()
        sheet.worksheet.return_value.get_all_values.return_value = [
            ['Association Life Members'], ["Member's Name", 'Batch', 'Total Paid Amount', 'Payment Status'],
            ['Example Member', '2001', '1,500', 'Unpaid'],
        ]
        first = sync_sheet_tab(sheet, 'LIFE', 0, 'Life Members')
        second = sync_sheet_tab(sheet, 'LIFE', 0, 'Life Members')
        self.assertEqual(first['added'], 1)
        self.assertEqual(second['updated'], 1)
        sheet.worksheet.assert_called_with('Life Members')
        member = MembershipPayment.objects.get()
        self.assertEqual(member.sheet_row_id, 3)
        self.assertEqual(member.status, 'PENDING')

    def test_unrecognised_sheet_headers_report_failure(self):
        sheet = Mock()
        sheet.get_worksheet.return_value.get_all_values.return_value = [['Wrong header'], ['A member']]
        self.assertEqual(sync_sheet_tab(sheet, 'LIFE', 0)['errors'], 1)

    @override_settings(GOOGLE_CREDS_JSON='')
    def test_missing_credentials_are_reported(self):
        self.assertFalse(sync_all()['success'])

    @patch('webapp.sheets_sync._get_credentials', return_value={})
    @patch('gspread.service_account_from_dict')
    @patch('webapp.sheets_sync.sync_sheet_tab')
    def test_partial_failure_does_not_report_success(self, tab, client, credentials):
        tab.side_effect = [dict(added=1, updated=0, skipped=0, errors=0), dict(added=0, updated=0, skipped=0, errors=1)]
        self.assertFalse(sync_all()['success'])

    @override_settings(CRON_SECRET='test-scheduler-token')
    @patch('webapp.Member_Views.sync_all', return_value={'success': True, 'total_added': 1})
    def test_scheduled_sync_requires_token(self, sync):
        url = reverse('scheduled_member_sync')
        self.assertEqual(self.client.post(url).status_code, 403)
        sync.assert_not_called()
        self.assertEqual(self.client.post(url, HTTP_AUTHORIZATION='Bearer test-scheduler-token').status_code, 200)


class RestorationTests(TestCase):
    def make_backup(self, path):
        with closing(sqlite3.connect(path)) as db:
            db.executescript('''
                CREATE TABLE app_membershippayment (
                    member_name TEXT, member_type TEXT, sheet_row_id INTEGER, payment_date TEXT,
                    amount TEXT, receipt_number TEXT, batch_year TEXT, phone TEXT, status TEXT);
                INSERT INTO app_membershippayment VALUES ('Original member','LIFE',2,NULL,'500','R1','2000','','PAID');
                CREATE TABLE app_customuser (id INTEGER, email TEXT, username TEXT, first_name TEXT, last_name TEXT);
                INSERT INTO app_customuser VALUES (1,'alum@example.com','restoredalum','Example','Alum');
                CREATE TABLE app_alumni (admin_id INTEGER, gender TEXT, passing_year TEXT);
                INSERT INTO app_alumni VALUES (1,'','2000');
            ''')

    def test_restore_is_idempotent_and_preserves_live_edits(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / 'backup.sqlite3'
            self.make_backup(source)
            call_command('restore_community', source=str(source), stdout=io.StringIO())
            MembershipPayment.objects.update(member_name='Newer live name')
            call_command('restore_community', source=str(source), stdout=io.StringIO())
        self.assertEqual(MembershipPayment.objects.get().member_name, 'Newer live name')
        self.assertEqual(Alumni.objects.count(), 1)
        user = CustomUser.objects.get()
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_superuser or user.is_staff)

    def test_dry_run_leaves_database_unchanged(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / 'backup.sqlite3'
            self.make_backup(source)
            call_command('restore_community', source=str(source), dry_run=True, stdout=io.StringIO())
        self.assertFalse(MembershipPayment.objects.exists())
        self.assertFalse(CustomUser.objects.exists())

    def test_conflict_rolls_back_all_imports(self):
        CustomUser.objects.create_user(username='restoredalum', email='different@example.com')
        with TemporaryDirectory() as directory:
            source = Path(directory) / 'backup.sqlite3'
            self.make_backup(source)
            with self.assertRaises(CommandError):
                call_command('restore_community', source=str(source), stdout=io.StringIO())
        self.assertFalse(MembershipPayment.objects.exists())
        self.assertFalse(Alumni.objects.exists())
