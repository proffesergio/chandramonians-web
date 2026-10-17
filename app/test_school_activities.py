from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from app.models import Alumni, CustomUser, Event, MembershipPayment, VolunteerApplication


class SchoolActivityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        cls.upcoming = Event.objects.create(
            title='Science guest lesson', description='A real lesson plan for students.',
            event_date=now + timedelta(days=4), location='School classroom',
            activity_type='GUEST_CLASS', guest_faculty='A confirmed teacher',
            audience='Class 9', is_published=True,
        )
        cls.completed = Event.objects.create(
            title='Completed career seminar', description='Career discussion.',
            event_date=now - timedelta(days=5), location='School hall',
            activity_type='SEMINAR', status='COMPLETED', is_published=True,
            students_reached=32, outcome='Students practiced preparing their first CV.',
        )
        Event.objects.create(title='Private planning', description='Internal only.', event_date=now + timedelta(days=1), location='School', is_published=False)
        Event.objects.create(title='Cancelled programme', description='Will not take place.', event_date=now + timedelta(days=1), location='School', is_published=True, status='CANCELLED')
        MembershipPayment.objects.create(member_name='Actual Example Member', member_type='LIFE', sheet_row_id=2, batch_year='2001')
        user = CustomUser.objects.create_user(username='graduate', email='graduate@example.com', first_name='Example', last_name='Graduate', user_type='3')
        Alumni.objects.create(admin=user, gender='', passing_year='2001')

    def test_home_shows_real_members_and_published_activity_outcomes(self):
        response = self.client.get('/')
        self.assertContains(response, 'Actual Example Member')
        self.assertContains(response, 'Science guest lesson')
        self.assertContains(response, 'Students practiced preparing their first CV.')
        self.assertContains(response, '32 recorded student attendances')
        self.assertNotContains(response, 'Private planning')
        self.assertNotContains(response, 'Cancelled programme')
        self.assertEqual(response.context['total_members'], 1)
        self.assertEqual(response.context['upcoming_count'], 1)
        self.assertEqual(response.context['completed_activities'], 1)
        self.assertContains(response, 'homeMapTitle')
        self.assertContains(response, 'textSizeToggle')
        self.assertNotContains(response, 'bgCanvas')

    def test_activity_filters_and_completed_results(self):
        response = self.client.get(reverse('events'))
        self.assertContains(response, self.upcoming.title)
        self.assertContains(response, self.completed.title)
        self.assertNotContains(response, 'Private planning')
        self.assertNotContains(response, 'Cancelled programme')
        response = self.client.get(reverse('events'), {'type': 'GUEST_CLASS'})
        self.assertContains(response, self.upcoming.title)
        self.assertNotContains(response, self.completed.title)
        self.assertContains(response, 'A confirmed teacher')

    def test_end_time_cannot_precede_start(self):
        self.upcoming.end_date = self.upcoming.event_date - timedelta(hours=1)
        with self.assertRaises(ValidationError) as error:
            self.upcoming.full_clean()
        self.assertIn('end_date', error.exception.message_dict)

    def test_new_activities_are_drafts(self):
        self.assertFalse(Event().is_published)

    def test_member_search_selects_the_group_with_results(self):
        MembershipPayment.objects.create(member_name='General Search Example', member_type='GENERAL', sheet_row_id=3, batch_year='2005')
        response = self.client.get(reverse('public_members'), {'q': 'General Search', 'batch': '2005'})
        self.assertContains(response, 'General Search Example')
        self.assertNotContains(response, 'Actual Example Member')
        self.assertContains(response, 'id="general-tab" role="tab" aria-controls="generalMembers" aria-selected="true"')
        self.assertContains(response, 'id="life-tab" role="tab" aria-controls="lifeMembers" aria-selected="false"')
        # Both groups remain in the document for readers without JavaScript.
        self.assertContains(response, 'id="lifeMembers" role="tabpanel"')
        self.assertContains(response, 'id="generalMembers" role="tabpanel"')

    def test_member_tabs_default_to_life_and_handle_no_search_matches(self):
        for query in ({}, {'q': 'No such member'}):
            response = self.client.get(reverse('public_members'), query)
            self.assertContains(response, 'id="life-tab" role="tab" aria-controls="lifeMembers" aria-selected="true"')
        self.assertContains(response, 'No Life members match your search')


class VolunteerFlowTests(TestCase):
    def offer(self, **overrides):
        fields = {
            'name': 'Example Volunteer', 'email': 'volunteer@example.com', 'phone': '',
            'interest': 'GUEST_CLASS', 'expertise': 'Physics', 'availability': 'Friday mornings',
            'message': 'I would like to offer a lesson.', 'consent_to_contact': 'on',
            'status': 'APPROVED', 'admin_notes': 'Untrusted browser input',
        }
        fields.update(overrides)
        return fields

    def test_offer_is_saved_as_private_unreviewed_application(self):
        response = self.client.post(reverse('volunteer'), self.offer())
        self.assertRedirects(response, reverse('volunteer_received'))
        application = VolunteerApplication.objects.get()
        self.assertEqual(application.status, 'NEW')
        self.assertEqual(application.admin_notes, '')
        self.assertIsNone(application.assigned_to)
        self.assertTrue(application.consent_to_contact)
        self.assertNotContains(self.client.get('/'), 'volunteer@example.com')
        self.assertEqual(self.client.get(reverse('admin:app_volunteerapplication_changelist')).status_code, 302)

    def test_invalid_offer_is_not_saved_and_shows_helpful_errors(self):
        response = self.client.post(reverse('volunteer'), self.offer(email='', phone='', consent_to_contact=''))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please provide an email address or phone number')
        self.assertFalse(VolunteerApplication.objects.exists())

    def test_csrf_protection_remains_enabled(self):
        response = Client(enforce_csrf_checks=True).post(reverse('volunteer'), self.offer())
        self.assertEqual(response.status_code, 403)
        self.assertFalse(VolunteerApplication.objects.exists())

    def test_repeat_offer_is_not_duplicated(self):
        self.client.post(reverse('volunteer'), self.offer())
        response = self.client.post(reverse('volunteer'), self.offer())
        self.assertContains(response, 'received recently')
        self.assertEqual(VolunteerApplication.objects.count(), 1)

    def test_honeypot_rejects_bot_offer(self):
        self.client.post(reverse('volunteer'), self.offer(website='https://spam.example.com'))
        self.assertFalse(VolunteerApplication.objects.exists())

    def test_admin_can_assign_application_to_an_activity(self):
        owner = CustomUser.objects.create_superuser(username='owner', email='owner@example.com', password='SecureCommunity2026!', user_type='1')
        self.client.force_login(owner)
        offer = VolunteerApplication.objects.create(**{
            key: value for key, value in self.offer().items() if key not in ('consent_to_contact', 'admin_notes', 'status')
        }, consent_to_contact=True)
        event = Event.objects.create(title='Teacher session', description='Class plan', event_date=timezone.now()+timedelta(days=3), location='School')
        url = reverse('admin:app_volunteerapplication_change', args=[offer.pk])
        response = self.client.post(url, {'status':'CONTACTED', 'assigned_to':owner.pk, 'activity':event.pk, 'admin_notes':'Arrange a school visit.', '_save':'Save'})
        self.assertEqual(response.status_code, 302)
        offer.refresh_from_db()
        self.assertEqual(offer.status, 'CONTACTED')
        self.assertEqual(offer.activity, event)
        self.assertEqual(offer.assigned_to, owner)

    def test_staff_without_permission_cannot_read_applications(self):
        staff = CustomUser.objects.create_user(username='staff', email='staff@example.com', is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse('admin:app_volunteerapplication_changelist')).status_code, 403)
