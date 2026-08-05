import os
import sys
from pathlib import Path
import django
import random

# Setup Django environment
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isheri_config.settings')
django.setup()

from apps.users.models import CustomUser, OTPVerification
from apps.users.emails import send_verification_otp, send_welcome_email

# Configure test account
email = os.environ.get('TEST_SIGNUP_EMAIL', 'testuser@example.com')
full_name = 'Integration Test'
password = 'TestPass123'

# Create user (or reuse)
user, created = CustomUser.objects.get_or_create(email=email, defaults={'username': email})
if created:
    user.set_password(password)
    user.is_active = False
    # set optional fields if present
    if hasattr(user, 'full_name'):
        setattr(user, 'full_name', full_name)
    user.save()
    print('Created user:', email)
else:
    print('Reusing existing user:', email)

# Generate OTP
otp_code = str(random.randint(100000, 999999))
otp = OTPVerification.objects.create(user=user, otp_code=otp_code)
print('Created OTP record:', otp.otp_code)

# Send verification email
print('\n--- Sending verification email ---')
send_verification_otp(user.email, full_name, otp_code)
print('Verification email sent (check inbox)')

# Simulate user entering OTP
print('\n--- Simulating OTP verification ---')
otp_record = OTPVerification.objects.filter(user=user, otp_code=otp_code, is_verified=False).first()
if otp_record:
    otp_record.is_verified = True
    otp_record.save()
    user.is_active = True
    user.save()
    print('OTP verified and user activated')
    # Send welcome email
    send_welcome_email(user.email, full_name)
    print('Welcome email sent')
else:
    print('OTP record not found or already verified')

print('\nDone')
