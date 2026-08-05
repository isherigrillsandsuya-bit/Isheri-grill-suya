import os
import sys
from pathlib import Path
import django

# Ensure project root is on sys.path so Django settings package can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isheri_config.settings')
django.setup()

from apps.users.emails import send_verification_otp

email = 'testuser@example.com'
full_name = 'Test User'
otp_code = '654321'

print('\n--- Sending verification email (no DB writes) ---')
send_verification_otp(email, full_name, otp_code)
print('--- Done ---')
