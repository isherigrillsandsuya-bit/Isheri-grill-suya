import random

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser, OTPVerification
from .emails import send_verification_otp, send_welcome_email

OTP_TTL_MINUTES = 10
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_RESEND_LIMIT = 3


def register_view(request):
    if request.method == 'POST':
        full_name = (request.POST.get('full_name') or request.POST.get('name') or '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Please provide both email and password to continue.")
            return redirect('users:register')

        if CustomUser.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('users:register')

        name_parts = full_name.split(None, 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            phone_number=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False,
        )

        otp_code = f"{random.randint(100000, 999999)}"
        OTPVerification.objects.create(user=user, otp_code=otp_code)
        try:
            send_verification_otp(email, user.full_name, otp_code)
        except Exception as e:
            print(f"Verification email failed: {e}")

        request.session['verify_email'] = email
        request.session['last_otp_sent'] = timezone.now().timestamp()
        request.session['otp_resend_count'] = 0
        return redirect('users:verify_otp')

    return render(request, 'users/register.html')


def verify_otp_view(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('users:register')

    try:
        user = CustomUser.objects.get(email__iexact=email)
    except CustomUser.DoesNotExist:
        return redirect('users:register')

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        otp_record = OTPVerification.objects.filter(user=user, otp_code=code, is_verified=False).first()

        if otp_record:
            if otp_record.is_expired:
                messages.error(request, "This verification code has expired. Please request a new one.")
            else:
                otp_record.is_verified = True
                otp_record.save()
                user.is_active = True
                user.is_verified = True
                user.save(update_fields=['is_active', 'is_verified'])

                try:
                    send_welcome_email(user.email, user.full_name)
                except Exception as e:
                    print(f"Welcome email skipped/failed: {e}")

                login(request, user, backend='apps.users.backends.EmailBackend')
                request.session.pop('verify_email', None)
                request.session.pop('last_otp_sent', None)
                request.session.pop('otp_resend_count', None)
                return redirect('shop:checkout')
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, 'users/verify_otp.html', {'email': email})


def resend_otp_view(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('users:register')

    try:
        user = CustomUser.objects.get(email__iexact=email)
    except CustomUser.DoesNotExist:
        return redirect('users:register')

    now_ts = timezone.now().timestamp()
    last_sent_ts = request.session.get('last_otp_sent', 0)
    resend_count = request.session.get('otp_resend_count', 0)

    if resend_count >= OTP_RESEND_LIMIT:
        messages.error(request, 'You have reached the maximum number of OTP resend attempts. Please try again later.')
        return redirect('users:verify_otp')

    if now_ts - last_sent_ts < OTP_RESEND_COOLDOWN_SECONDS:
        wait_seconds = int(OTP_RESEND_COOLDOWN_SECONDS - (now_ts - last_sent_ts))
        messages.warning(request, f'Please wait {wait_seconds} seconds before requesting a new verification code.')
        return redirect('users:verify_otp')

    otp_code = f"{random.randint(100000, 999999)}"
    OTPVerification.objects.create(user=user, otp_code=otp_code)
    request.session['last_otp_sent'] = now_ts
    request.session['otp_resend_count'] = resend_count + 1

    try:
        send_verification_otp(user.email, user.full_name, otp_code)
        messages.success(request, 'A new verification code was sent to your email.')
    except Exception as e:
        print(f"Resend verification email failed: {e}")
        messages.warning(request, 'We could not resend the code right now. Please try again shortly.')

    return redirect('users:verify_otp')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('shop:checkout')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('shop:home')
