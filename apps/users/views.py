from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import CustomUser, OTPVerification
from .emails import send_verification_otp, send_welcome_email
import random

def register_view(request):
    if request.method == 'POST':
        # Safely handle 'name' (from our HTML) or 'full_name' 
        full_name = request.POST.get('full_name') or request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('users:register')
            
        # Create inactive user
        user = CustomUser.objects.create_user(email=email, phone_number=phone, password=password, full_name=full_name)
        user.is_active = False # Explicitly lock account until OTP
        user.save()
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(user=user, code=otp_code)
        
        # 🚨 TEMPORARY: Print to terminal until Resend is integrated!
        print(f"\n" + "="*40)
        print(f"📧 EMAIL SIMULATION for {email}")
        print(f"🔑 YOUR OTP CODE IS: {otp_code}")
        print("="*40 + "\n")
        
        # Trigger the actual email (fails gracefully if .env is missing)
        try:
            send_verification_otp(email, full_name, otp_code)
        except Exception as e:
            print(f"Mail sending skipped/failed: {e}")

        request.session['verify_email'] = email
        return redirect('users:verify_otp')
        
    return render(request, 'users/register.html')

def verify_otp_view(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('users:register')
        
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            user = CustomUser.objects.get(email=email)
            otp_record = OTPVerification.objects.filter(user=user, code=code, is_verified=False).first()
            
            if otp_record:
                otp_record.is_verified = True
                otp_record.save()
                
                # Activate User
                user.is_active = True
                user.save()
                
                # Trigger Welcome Email with Bonus notice
                try:
                    send_welcome_email(user.email, getattr(user, 'full_name', 'Foodie'))
                except Exception as e:
                    print(f"Welcome Mail skipped/failed: {e}")
                
                # Log them in automatically
                login(request, user)
                del request.session['verify_email']
                
                # Send to checkout or home based on flow
                return redirect('shop:checkout') 
            else:
                messages.error(request, "Invalid or expired OTP.")
        except CustomUser.DoesNotExist:
            return redirect('users:register')
            
    return render(request, 'users/verify_otp.html', {'email': email})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
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
