import os, sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isheri_config.settings')
import django
django.setup()
from django.db import connection

def columns(table):
    with connection.cursor() as c:
        c.execute(f"PRAGMA table_info('{table}')")
        rows = c.fetchall()
        return rows

for t in ['users_customuser','users_otpverification']:
    print('Table:', t)
    try:
        for r in columns(t):
            print(r)
    except Exception as e:
        print('Error reading table:', e)
    print('')
