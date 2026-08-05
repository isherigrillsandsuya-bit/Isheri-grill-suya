# AI Assistant Hand-Off Note: Isheri Grills & Suya

**Target workspace:** Isheri Grills & Suya Django project
**Tech stack:** Python / Django / PostgreSQL / Tailwind CSS / HTMX / Alpine.js / Gunicorn
**Deployment target:** Render

---

## 1. Project structure

The project is organized as a modular Django monolith with app-specific responsibilities:

```text
isheri-grill-suya/
├── apps/
│   ├── shop/         # Menu, categories, cart, checkout, kitchen views
│   ├── users/        # Authentication, wallet, OTP, user profile data
│   ├── logistics/    # Delivery calculations, rider dashboard, mapping helpers
│   └── support/      # Support and contact-related flows
├── isheri_config/    # Settings, URL routing, WSGI/ASGI entry points
├── templates/        # Base and app templates
├── static/           # CSS, JS, and static assets
├── manage.py
├── requirements.txt
└── .env              # Local environment file; do not commit
```

---

## 2. Core models and modules

- `apps.users.models.CustomUser`: extends `AbstractUser` and tracks phone verification, OTPs, referrals, and wallet state.
- `apps.users.models.OTPVerification`: stores short-lived verification codes.
- `apps.users.models.Wallet` and `WalletTransaction`: manage balance changes and audit-friendly logs.
- `apps.shop.models`: covers categories, menu items, orders, and line items.

---

## 3. Environment configuration template

The app reads settings from environment variables in `isheri_config/settings.py`. Keep local secrets out of version control and use Render environment variables in production.

```env
DEBUG=False
SECRET_KEY=replace-with-strong-secret
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=replace-with-db-password
DB_HOST=your_db_host
DB_PORT=5432

# Payment gateway
PAYSTACK_PUBLIC_KEY=replace-with-paystack-public-key
PAYSTACK_SECRET_KEY=replace-with-paystack-secret-key

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=replace-with-email-user
EMAIL_HOST_PASSWORD=replace-with-email-password
DEFAULT_FROM_EMAIL=Isheri Grills <hello@example.com>

# Maps
GOOGLE_MAPS_API_KEY=replace-with-google-maps-keyyment notes

Use these deployment settings when configuring the Render service:

- Root directory: `.`
- Runtime: `Python 3`
- Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

- Start command:

```bash
gunicorn isheri_config.wsgi:application
```

---

## 5. Current audit snapshot

### Status

- ✅ Core Django app structure is present.
- ✅ Base templates and storefront pages are in place.
- ⚠️ Several template and styling issues were found and cleaned up.
- ⚠️ Remaining work is mostly around runtime validation and checkout/payment integration.

### Remaining fixes (todo list)

- [x] Restore the checkout/payment handoff route and connect it to the storefront.
- [x] Capture delivery details from the checkout form and carry them into the success/receipt flow.
- [ ] Verify the local database connection with the real environment values.
- [ ] Validate the checkout and cart flow end to end.
- [ ] Seed initial menu items for the storefront.
- [ ] Test payment initialization and verification flows once Paystack credentials are configured.
- [ ] Review the production settings and confirm the secret handling strategy.
