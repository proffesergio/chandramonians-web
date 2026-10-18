from io import BytesIO
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from app.models import Alumni, CustomUser, MembershipPayment, ProfilePicture
from app.profile_storage import ProfilePictureStorage


class ProfileAndMapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(username='mapalum', email='private@example.com',
                                                 first_name='Registered', last_name='Alumnus', user_type='3',
                                                 password='Initial!Community2026')
        cls.alumni = Alumni.objects.create(admin=cls.user, passing_year='2001', gender='',
                                          address='Private street', phone='01712345678')

    def image(self, name='avatar.png', size=(800, 600)):
        data = BytesIO()
        Image.new('RGB', size, 'green').save(data, 'PNG')
        return SimpleUploadedFile(name, data.getvalue(), content_type='image/png')

    def update(self, **changes):
        self.client.force_login(self.user)
        data = {'first_name': 'Registered', 'last_name': 'Alumnus', 'password': '', 'map_country': ''}
        data.update(changes)
        return self.client.post(reverse('profile_update'), data)

    def test_upload_is_durable_resized_and_served_without_local_media(self):
        response = self.update(profile_pic=self.image())
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile_pic.name.startswith('avatars/'))
        self.assertEqual(ProfilePicture.objects.count(), 1)
        # A fresh storage instance reads the image from the database, not disk.
        with ProfilePictureStorage().open(self.user.profile_pic.name) as saved:
            image = Image.open(saved)
            self.assertEqual(image.format, 'WEBP')
            self.assertLessEqual(max(image.size), 512)
        response = self.client.get(self.user.profile_pic.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/webp')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(self.client.get(self.user.profile_pic.url, HTTP_IF_NONE_MATCH=response['ETag']).status_code, 304)

    def test_invalid_upload_does_not_change_profile(self):
        file = SimpleUploadedFile('fake.jpg', b'<script>invalid</script>', content_type='image/jpeg')
        response = self.update(profile_pic=file, first_name='Should not save')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Registered')
        self.assertFalse(ProfilePicture.objects.exists())

    def test_oversized_file_does_not_save(self):
        photo = self.image()
        content = photo.read() + b'\0' * (3 * 1024 * 1024)
        response = self.update(profile_pic=SimpleUploadedFile('large.png', content, content_type='image/png'))
        self.assertContains(response, 'smaller than 3 MB')
        self.assertFalse(ProfilePicture.objects.exists())

    def test_weak_password_is_rejected_and_successful_change_keeps_login(self):
        response = self.update(password='123')
        self.assertTrue(response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Initial!Community2026'))
        response = self.update(password='New!RandomCommunity2027')
        self.assertRedirects(response, reverse('profile'))
        self.assertEqual(self.client.get(reverse('profile')).status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('New!RandomCommunity2027'))

    def test_all_registered_profiles_appear_but_private_details_do_not(self):
        self.alumni.map_country = 'CAN'
        self.alumni.save()
        MembershipPayment.objects.create(member_name='Sheet only member', member_type='LIFE', sheet_row_id=2)
        response = self.client.get(reverse('alumni_map'))
        self.assertContains(response, 'Registered Alumnus')
        self.assertContains(response, 'Location not shared')
        self.assertNotContains(response, 'private@example.com')
        self.assertNotContains(response, 'Private street')
        self.assertNotContains(response, '01712345678')
        self.assertNotContains(response, 'Sheet only member')
        self.assertEqual(response.context['markers'], [])
        self.assertEqual(response.context['registered_count'], 1)

    def test_profile_location_consent_controls_marker_and_country_filter(self):
        self.assertRedirects(self.update(map_country='BGD', map_visible='on'), reverse('profile'))
        response = self.client.get(reverse('alumni_map'), {'country': 'BGD', 'batch': '2001', 'q': 'Registered'})
        self.assertContains(response, 'Registered Alumnus')
        self.assertEqual(response.context['markers'][0]['name'], 'Bangladesh')
        self.assertEqual(response.context['markers'][0]['count'], 1)
        self.assertEqual(response.context['map_profiles']['BGD'][0]['name'], 'Registered Alumnus')
        self.assertNotIn('phone', response.context['map_profiles']['BGD'][0])
        self.assertContains(response, 'atlasProfiles')
        self.assertContains(response, 'Create a group chat')
        self.assertEqual(self.client.get(reverse('alumni_map'), {'country': 'CAN'}).context['alumni_list'].count(), 0)
        self.assertRedirects(self.update(map_country='BGD'), reverse('profile'))
        self.assertEqual(self.client.get(reverse('alumni_map')).context['markers'], [])
        self.assertEqual(self.client.get(reverse('alumni_map')).context['map_profiles'], {})
        self.assertEqual(self.client.get(reverse('alumni_map'), {'country': 'BGD'}).context['alumni_list'].count(), 0)

    def test_missing_or_invalid_country_does_not_publish_location(self):
        response = self.update(map_visible='on')
        self.assertContains(response, 'Choose a country before sharing')
        response = self.update(map_country='XXX', map_visible='on')
        self.assertTrue(response.context['form'].errors)
        self.alumni.refresh_from_db()
        self.assertFalse(self.alumni.map_visible)

    def test_new_alumni_signup_appears_on_map_list_without_fake_location(self):
        response = self.client.post(reverse('doRegister'), {'username': 'newmap', 'email': 'newmap@example.com',
            'first_name': 'Newly', 'last_name': 'Registered', 'user_type': '3',
            'password': 'New!CommunityPassword2026', 'confirm_password': 'New!CommunityPassword2026'})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('alumni_map'))
        self.assertContains(response, 'Newly Registered')
        self.assertEqual(response.context['registered_count'], 2)
        self.assertEqual(response.context['markers'], [])

    def test_inactive_accounts_are_excluded_and_empty_search_renders(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.get(reverse('alumni_map'))
        self.assertNotContains(response, 'Registered Alumnus')
        self.assertEqual(response.context['registered_count'], 0)
        self.assertContains(response, 'No alumni found')
        self.assertEqual(self.client.get(reverse('profile_picture', args=[uuid.uuid4()])).status_code, 404)
