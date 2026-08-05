import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isheri_config.settings')
import django
django.setup()
from django.test import Client
from django.urls import reverse
from apps.users.models import CustomUser, OTPVerification

client = Client()
user = CustomUser.objects.create_user(username='verify@example.com', email='verify@example.com', password='Password123', is_active=False)
OTPVerification.objects.create(user=user, otp_code='123456')
session = client.session
session['verify_email'] = user.email
session.save()
try:
    response = client.post(reverse('users:verify_otp'), {'code': '123456'})
    print('STATUS', response.status_code)
    print('URL', getattr(response, 'url', None))
    print('CONTENT', response.content[:500])
except Exception:
    import traceback
    traceback.print_exc()
