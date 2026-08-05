from django.test import TestCase
from django.urls import reverse

from apps.users.models import CustomUser


class CheckoutPaymentFlowTests(TestCase):
    def test_initialize_payment_redirects_to_success_with_checkout_details(self):
        user = CustomUser.objects.create_user(
            username='checkout-user',
            email='checkout@example.com',
            password='testpass123',
        )
        self.client.force_login(user)

        session = self.client.session
        session['cart'] = {
            '1': {'id': 1, 'name': 'Suya', 'price': 1500.0, 'quantity': 2}
        }
        session.save()

        response = self.client.post(reverse('shop:initialize_payment'), {
            'delivery_address': '15 Admiralty Way, Lekki',
            'phone_number': '08012345678',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('shop:success'))
        self.assertEqual(
            self.client.session['checkout_details']['address'],
            '15 Admiralty Way, Lekki',
        )
