import os
import sys
sys.path.insert(0, r'c:\Users\HP-PC\Desktop\Isheri-grill-suya')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isheri_config.settings')
import django
django.setup()
from django.test import RequestFactory
from django.urls import reverse
from apps.users.views import verify_otp_view
from apps.users.models import CustomUser, OTPVerification
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.messages.middleware import MessageMiddleware

rf = RequestFactory()
user = CustomUser.objects.create_user(username='verify@example.com', email='verify@example.com', password='Password123', is_active=False)
otp = OTPVerification.objects.create(user=user, otp_code='123456')
request = rf.post(reverse('users:verify_otp'), {'code': '123456'})
# add session
middleware = SessionMiddleware(lambda req: None)
middleware.process_request(request)
request.session.save()
request.session['verify_email'] = user.email
request.session.save()
# add messages
messages = FallbackStorage(request)
request._messages = messages

try:
    response = verify_otp_view(request)
    print('RESPONSE', response.status_code)
    print(type(response))
    print(getattr(response, 'url', None))
    if hasattr(response, 'content'):
        print(response.content[:500])
except Exception as e:
    import traceback
    traceback.print_exc()
