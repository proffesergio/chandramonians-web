from django.test import TestCase
from django.urls import reverse

from app.models import Alumni, AlumniFeedback, ApplyForMembership, CustomUser, Staff, StaffNotification


class LegacyPanelSecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.hod = CustomUser.objects.create_user(username='hod', email='hod@example.com', user_type='1')
        cls.alum_user = CustomUser.objects.create_user(username='alum', email='alum@example.com', user_type='3')
        cls.alum = Alumni.objects.create(admin=cls.alum_user, gender='')
        cls.staff_user = CustomUser.objects.create_user(username='staff', email='staff@example.com', user_type='2')
        cls.staff = Staff.objects.create(admin=cls.staff_user, gender='')
        cls.other_staff_user = CustomUser.objects.create_user(username='otherstaff', email='otherstaff@example.com', user_type='2')
        cls.other_staff = Staff.objects.create(admin=cls.other_staff_user, gender='')
        cls.application = ApplyForMembership.objects.create(alum_id=cls.alum, date='2026-10-18')
        cls.feedback = AlumniFeedback.objects.create(alum_id=cls.alum, feedback='Please reply')
        cls.notification = StaffNotification.objects.create(staff_id=cls.other_staff, message='Private')

    def hod_routes(self):
        return [
            ('hod_home', []), ('add_alumni', []), ('view_alumni', []), ('edit_alumni', [self.alum.pk]),
            ('update_alumni', []), ('delete_alumni', [self.alum_user.pk]), ('add_staff', []),
            ('view_staff', []), ('edit_staff', [self.staff.pk]), ('update_staff', []),
            ('delete_staff', [self.staff_user.pk]), ('notify_staff', []), ('save_notification', []),
            ('membership_applications', []), ('membership_approved', [self.application.pk]),
            ('membership_denied', [self.application.pk]), ('alum_feedback', []), ('reply_feedback', []),
        ]

    def test_anonymous_and_every_other_role_cannot_access_any_hod_route(self):
        student = CustomUser.objects.create_user(username='student', email='student@example.com', user_type='4')
        for user in (None, self.alum_user, self.staff_user, student):
            self.client.logout()
            if user:
                self.client.force_login(user)
            for name, args in self.hod_routes():
                for method in ('get', 'post'):
                    with self.subTest(role=user.user_type if user else 'anonymous', route=name, method=method):
                        response = getattr(self.client, method)(reverse(name, args=args))
                        self.assertEqual(response.status_code, 403 if user else 302)
        self.assertTrue(CustomUser.objects.filter(pk=self.alum_user.pk).exists())
        self.assertTrue(CustomUser.objects.filter(pk=self.staff_user.pk).exists())
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 0)

    def test_hod_mutations_require_post_and_valid_csrf(self):
        self.client.force_login(self.hod)
        for name, args in self.hod_routes():
            if name in {'update_alumni', 'delete_alumni', 'update_staff', 'delete_staff', 'save_notification',
                        'membership_approved', 'membership_denied', 'reply_feedback'}:
                with self.subTest(route=name):
                    self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 405)
        from django.test import Client
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.hod)
        self.assertEqual(strict.post(reverse('delete_alumni', args=[self.alum_user.pk])).status_code, 403)

    def test_hod_can_approve_reply_and_delete_intended_role(self):
        self.client.force_login(self.hod)
        self.assertEqual(self.client.post(reverse('membership_approved', args=[self.application.pk])).status_code, 302)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 1)
        response = self.client.post(reverse('reply_feedback'), {'feedback_id': self.feedback.pk, 'feedback_reply': 'Received'})
        self.assertRedirects(response, reverse('alum_feedback'))
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.feedback_reply, 'Received')
        self.assertContains(self.client.get(reverse('alum_feedback')), f'name="feedback_id" value="{self.feedback.pk}"')
        self.assertEqual(self.client.post(reverse('delete_alumni', args=[self.hod.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('delete_staff', args=[self.alum_user.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('delete_staff', args=[self.staff_user.pk])).status_code, 302)
        self.assertFalse(CustomUser.objects.filter(pk=self.staff_user.pk).exists())

    def test_staff_can_only_read_and_update_their_own_notifications(self):
        self.client.force_login(self.staff_user)
        self.assertNotContains(self.client.get(reverse('notifications')), 'Private')
        url = reverse('mark_as_done', args=[self.notification.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url).status_code, 404)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 0)
        self.client.force_login(self.other_staff_user)
        self.assertContains(self.client.get(reverse('notifications')), 'Private')
        self.assertEqual(self.client.post(url).status_code, 302)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 1)

    def test_wrong_roles_cannot_enter_alumni_or_staff_panels(self):
        self.client.force_login(self.hod)
        for name in ('staff_home', 'notifications', 'alumni_home', 'membership_apply', 'save_membership', 'save_feedback', 'alumni_feedback'):
            with self.subTest(route=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 403)

    def test_membership_history_shows_approved_and_denied_correctly(self):
        self.client.force_login(self.alum_user)
        for status, expected, wrong in ((1, 'Approved', 'Denied'), (2, 'Denied', 'Approved')):
            with self.subTest(status=status):
                self.application.status = status
                self.application.save()
                response = self.client.get(reverse('membership_apply'))
                self.assertContains(response, f'>{expected}</span>')
                self.assertNotContains(response, f'>{wrong}</span>')

    def test_feedback_reply_controls_use_current_bootstrap_attributes(self):
        self.client.force_login(self.hod)
        response = self.client.get(reverse('alum_feedback'))
        self.assertContains(response, 'data-bs-toggle="modal"')
        self.assertNotContains(response, 'data-toggle="modal"')
