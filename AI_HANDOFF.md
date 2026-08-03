# AI ASSISTANT HAND-OFF NOTE: ISHERI GRILLS & SUYA
**Target Workspace:** `~/Desktop/Isheri-grill-suya`
**Tech Stack:** Python 3.x / Django 5.x / PostgreSQL (Supabase) / Tailwind CSS / HTMX & Alpine.js / Gunicorn / WhiteNoise
**Deployment Target:** Render (Free Tier Web Service)

---

## 1. ARCHITECTURE & DIRECTORY LAYOUT
The project follows a clean, modular multi-app Django structure to avoid namespace collisions and circular imports:
```
isheri-grill-suya/

├── apps/

│   ├── shop/          # Menu, categories, inventory toggles, cart logic

│   ├── users/         # CustomUser, Wallet, WalletTransaction, OTP verification

│   ├── logistics/     # Delivery calculations, rider management, Google Maps Distance Matrix

│   └── support/       # Customer support routing & contact modules

├── isheri_config/     # Core settings, WSGI, URLs configuration

├── templates/         # Global & app-scoped HTML templates (Tailwind + Alpine.js)

├── static/            # CSS, JS, and product media assets

├── manage.py

├── requirements.txt

└── .env               # Local environment configuration (IGNORED BY GIT)
```
---

## 2. CORE DATABASE MODELS CONFIGURED (`apps/`)
- **`apps.users.models.CustomUser`**: Inherits from `AbstractUser`. Tracks `phone_number`, `is_verified` (Boolean), `otp_code`, `referral_code`, and `referred_by`.
- **`apps.users.models.OTPVerification`**: Manages secure 6-digit cryptographic verification codes for registration/login.
- **`apps.users.models.Wallet` & `WalletTransaction`**: Handles cashback, referral bonuses, and secure credit/debit transaction logs.
- **`apps.shop.models`**: Category, MenuItem (with real-time `is_available` toggles for kitchen stock control), Order, and OrderItem.

---

## 3. CURRENT ENVIRONMENT CONFIGURATION KEYS
The app reads parameters directly via `os.getenv()` in `isheri_config/settings.py`. 
*Note for local `.env` vs Render Cloud:* Do **not** commit `.env`. Production values are mapped securely on Render.

### **Required Environment Variables Template:**
```env
DEBUG=False
SECRET_KEY=django-insecure-9q#v$m8w2z-isheri-grills-suya-production-key-4x!p
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com

# Database (Supabase PostgreSQL Session Pooler URL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.tudftygmwfjmllqrztdr
DB_PASSWORD=Ka$kaz@zs/z@z6
DB_HOST=aws-0-eu-central-1.pooler.supabase.co
DB_PORT=6543

# Payment Gateway (Paystack)
PAYSTACK_PUBLIC_KEY=pk_test_62144fb8b8c3895bb

# Email Engine (Resend API SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSW
DEFAULT_FROM_EMAIL=Isheri Grills <onboarding@resend.dev>

# Logistics (Google Maps API)
GOOGLE_MAPS_API_KEY=AIzaSy_your_google_maps_key_here
```

## 4. RENDER DEPLOYMENT SPECIFICATIONS
If managing builds or manual configurations on Render, adhere strictly to these settings:

- **Root Directory:** Blank (`.`)
- **Runtime:** `Python 3`
- **Build Command:** ```bash

pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
- **Start Command:** ```bash

gunicorn isheri_config.wsgi:application

```

## 5. IMMEDIATE NEXT TASKS FOR VS CODE AI
When you resume work in VS Code, tackle these pending items in order:

1. **Verify Database Connection Locally:** Run `python manage.py migrate` with your Supabase credentials active to ensure all migrations run smoothly.
2. **Checkout Templates & Frontend Views:** Inspect `apps/shop/views.py` and `templates/` to make sure the mobile cart, checkout flow, and HTMX triggers connect seamlessly to backend endpoints.
3. **Seed Initial Menu Items:** Run or write a management command to populate default menu items (Suya, Shawarma, Asun, Drinks) so products render dynamically on the UI.
4. **Test Payment & Webhooks:** Verify that Paystack initialize/verify endpoints handle orders correctly.
