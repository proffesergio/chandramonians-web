from django.test import TestCase, Client
from django.urls import reverse

from app.models import Alumni, CustomUser


class AlumniPrivacyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = CustomUser.objects.create_user(username='privacy-owner', email='owner@example.com', user_type='3', first_name='Private', last_name='Graduate')
        cls.profile = Alumni.objects.create(admin=cls.owner, gender='', father_name='PrivateFather',
            mother_name='PrivateMother', current_address='PrivateCurrentStreet', permanent_address='PrivatePermanentStreet',
            phone='01755556666', blood_group='AB-', education='PrivateQualification',
            profession='PrivateProfession', company='PrivateWorkplace', passing_year='1998',
            show_profession=False, show_company=False, show_passing_year=False, map_country='BGD', map_visible=True)
        cls.other = CustomUser.objects.create_user(username='other-profile', email='other-profile@example.com', user_type='3')
        Alumni.objects.create(admin=cls.other, gender='')

    def data(self, **changes):
        data = {'father_name': 'New father', 'mother_name': 'New mother',
                'current_address': 'New current address', 'permanent_address': 'New permanent address',
                'phone': '+8801755556666', 'blood_group': 'O+', 'education': 'Graduate',
                'profession': 'Teacher', 'company': 'School', 'passing_year': '2001'}
        data.update(changes)
        return data

    def test_default_private_values_are_absent_from_public_profile_map_and_directory(self):
        for name, args in [('alumni_public_profile', [self.profile.pk]), ('alumni_map', []), ('public_directory', [])]:
            response = self.client.get(reverse(name, args=args))
            self.assertEqual(response.status_code, 200)
            for secret in ['PrivateFather', 'PrivateMother', 'PrivateCurrentStreet', 'PrivatePermanentStreet',
                           '01755556666', 'AB-', 'PrivateQualification', 'PrivateProfession', 'PrivateWorkplace', '1998']:
                self.assertNotContains(response, secret)
        self.client.force_login(self.other)
        response = self.client.get(reverse('alumni_directory'))
        self.assertNotContains(response, 'PrivateProfession')
        self.assertNotContains(response, 'PrivateWorkplace')
        self.assertNotContains(response, 'AB-')

    def test_visibility_is_opt_in_and_can_be_revoked(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('alumni_profile_update'), self.data(show_blood_group='on', show_phone='on', donor_opt_in='on'))
        self.assertRedirects(response, reverse('profile'))
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.donor_opt_in)
        public = self.client.get(reverse('alumni_public_profile', args=[self.profile.pk]))
        self.assertContains(public, 'O+')
        self.assertContains(public, '+8801755556666')
        self.assertNotContains(public, 'New father')
        self.client.post(reverse('alumni_profile_update'), self.data())
        public = self.client.get(reverse('alumni_public_profile', args=[self.profile.pk]))
        self.assertNotContains(public, 'O+')
        self.assertNotContains(public, '+8801755556666')
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.donor_opt_in)

    def test_owner_scope_ignores_forged_target_and_role_fields(self):
        self.client.force_login(self.other)
        self.client.post(reverse('alumni_profile_update'), self.data(admin=self.owner.pk, user_type='1', is_superuser='on'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.father_name, 'PrivateFather')
        self.other.refresh_from_db()
        self.assertFalse(self.other.is_superuser)
        self.assertEqual(self.other.user_type, '3')

    def test_invalid_blood_group_phone_batch_and_missing_donor_group_do_not_save(self):
        self.client.force_login(self.owner)
        for changes in [{'blood_group': 'UNKNOWN'}, {'phone': '<script>'}, {'passing_year': '2999'}, {'blood_group': '', 'donor_opt_in': 'on'}]:
            response = self.client.post(reverse('alumni_profile_update'), self.data(**changes))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['alumni_form'].errors)
            self.profile.refresh_from_db()
            self.assertEqual(self.profile.father_name, 'PrivateFather')

    def test_private_batch_and_profession_cannot_be_used_as_search_or_filter(self):
        self.assertEqual(self.client.get(reverse('alumni_map'), {'q': 'PrivateProfession'}).context['alumni_list'].count(), 0)
        self.assertEqual(self.client.get(reverse('public_directory'), {'batch': '1998'}).context['alumni_list'].count(), 0)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse('alumni_directory'), {'q': 'PrivateWorkplace'}).context['alumni_list'].count(), 0)

    def test_role_csrf_and_method_protection(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('alumni_profile_update')).status_code, 405)
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.owner)
        self.assertEqual(strict.post(reverse('alumni_profile_update'), self.data()).status_code, 403)
        student = CustomUser.objects.create_user(username='privacy-student', email='privacy-student@example.com', user_type='4')
        self.client.force_login(student)
        self.assertEqual(self.client.post(reverse('alumni_profile_update'), self.data()).status_code, 403)
