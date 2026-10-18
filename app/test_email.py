from unittest.mock import patch

from django.conf import settings
from django.contrib.messages import get_messages
from django.core import mail
from django.core.mail import mail_admins, mail_managers
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AssociationEmailTests(TestCase):
    def message_data(self, **changes):
        data = {'name': 'Alumni Visitor', 'email': 'visitor@example.com',
                'subject': 'Membership question', 'message': 'How can I join?'}
        data.update(changes)
        return data

    @override_settings(DEFAULT_FROM_EMAIL='mailer@example.com', ADMIN_EMAIL='thechandramonians@gmail.com')
    def test_contact_delivers_to_association_inbox_with_visitor_reply_to(self):
        response = self.client.post(reverse('contact'), self.message_data())
        self.assertRedirects(response, reverse('contact'))
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['thechandramonians@gmail.com'])
        self.assertEqual(message.from_email, 'mailer@example.com')
        self.assertEqual(message.reply_to, ['visitor@example.com'])
        self.assertIn('How can I join?', message.body)

    def test_admin_and_manager_notifications_use_association_inbox(self):
        self.assertEqual(settings.ADMIN_EMAIL, 'thechandramonians@gmail.com')
        mail_admins('Server notification', 'Details')
        mail_managers('Manager notification', 'Details')
        self.assertEqual(len(mail.outbox), 2)
        for message in mail.outbox:
            self.assertEqual(message.to, ['thechandramonians@gmail.com'])

    @override_settings(ADMIN_EMAIL='thechandramonians@gmail.com')
    def test_contact_page_uses_configured_mailto_link(self):
        response = self.client.get(reverse('contact'))
        self.assertContains(response, 'href="mailto:thechandramonians@gmail.com"')

    def test_invalid_contact_email_or_excessive_content_does_not_send(self):
        for data in (self.message_data(email='invalid-email'), self.message_data(name=''),
                     self.message_data(message='x' * 10001)):
            with self.subTest(email=data['email'], length=len(data['message'])):
                self.client.post(reverse('contact'), data)
        self.assertEqual(len(mail.outbox), 0)

    @patch('webapp.Public_Views.EmailMessage.send', side_effect=OSError('SMTP unavailable'))
    def test_delivery_failure_does_not_report_success(self, send):
        response = self.client.post(reverse('contact'), self.message_data())
        notices = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertIn('Message could not be sent. Please try again or contact us directly.', notices)
        self.assertNotIn('Your message has been sent! We will get back to you soon.', notices)
