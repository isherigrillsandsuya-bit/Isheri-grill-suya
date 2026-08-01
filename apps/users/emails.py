from django.core.mail import send_mail
from django.conf import settings

def send_verification_otp(email, name, otp):
    """Sends the initial OTP verification code to the new user."""
    subject = 'Verify Your Isheri Grills & Suya Account'
    message = f"Hello {name},\n\nThank you for signing up! Your verification code is: {otp}\n\nEnter this code on the website to activate your account."
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def send_welcome_email(email, name):
    """Sends the official welcome and bonus notification after successful verification."""
    subject = 'Welcome to Isheri Grills & Suya! 🔥'
    message = f"Hello {name},\n\nYour account has been successfully verified!\n\nAs promised, your ₦150 Welcome Bonus is ready for your first order. Enjoy 2% cashback on all your future Suya and Grill orders.\n\nStay spicy,\nThe Isheri Grills Team"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
