import re
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import CustomUser, OTPVerification


class UserRegistrationTests(TestCase):

    def test_register_creates_inactive_user_and_sends_otp(self):
        url = reverse('users:register')
        with patch('apps.users.views.send_verification_otp') as mock_send:
            response = self.client.post(url, {
                'name': 'Moyo Oshodi',
                'email': 'moyo@example.com',
                'phone': '08012345678',
                'password': 'SuperSecret123',
                'confirm_password': 'SuperSecret123',
            })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(email='moyo@example.com').exists())
        user = CustomUser.objects.get(email='moyo@example.com')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)
        self.assertEqual(mock_send.call_count, 1)
        otp = OTPVerification.objects.filter(user=user).first()
        self.assertIsNotNone(otp)
        self.assertRegex(otp.otp_code, r'^\d{6}$')

    def test_verify_otp_activates_user(self):
        user = CustomUser.objects.create_user(
            username='verify@example.com',
            email='verify@example.com',
            password='Password123',
            is_active=False,
        )
        otp = OTPVerification.objects.create(user=user, otp_code='123456')

        session = self.client.session
        session['verify_email'] = user.email
        session.save()

        response = self.client.post(reverse('users:verify_otp'), {'code': '123456'})

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_verified)
        otp.refresh_from_db()
        self.assertTrue(otp.is_verified)

    def test_resend_otp_blocks_when_limit_exceeded(self):
        user = CustomUser.objects.create_user(
            username='limit@example.com',
            email='limit@example.com',
            password='Password123',
            is_active=False,
        )
        session = self.client.session
        session['verify_email'] = user.email
        session['last_otp_sent'] = timezone.now().timestamp() - 120
        session['otp_resend_count'] = 3
        session.save()

        response = self.client.get(reverse('users:resend_otp'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['otp_resend_count'], 3)

    def test_resend_otp_obeys_cooldown(self):
        user = CustomUser.objects.create_user(
            username='cooldown@example.com',
            email='cooldown@example.com',
            password='Password123',
            is_active=False,
        )
        session = self.client.session
        session['verify_email'] = user.email
        session['last_otp_sent'] = timezone.now().timestamp()
        session['otp_resend_count'] = 1
        session.save()

        response = self.client.get(reverse('users:resend_otp'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please wait')
        self.assertEqual(self.client.session['otp_resend_count'], 1)

# Create your tests here.
