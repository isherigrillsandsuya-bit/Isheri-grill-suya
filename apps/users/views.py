from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import CustomUser, OTPVerification
import random

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('users:register')
            
        # Create inactive user
        user = CustomUser.objects.create_user(email=email, phone_number=phone, password=password, full_name=full_name)
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(user=user, code=otp_code)
        
        # 🚨 TEMPORARY: Print to terminal until Resend is integrated!
        print(f"\n" + "="*40)
        print(f"📧 EMAIL SIMULATION for {email}")
        print(f"🔑 YOUR OTP CODE IS: {otp_code}")
        print("="*40 + "\n")
        
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
                user.is_active = True
                user.save()
                
                # Log them in automatically
                login(request, user)
                del request.session['verify_email']
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
