from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_verification_otp(email, name, otp):
    """Sends the initial OTP verification code to the new user using an HTML template."""
    subject = 'Verify Your Isheri Grills & Suya Account'
    context = {'name': name, 'otp': otp}
    html_content = render_to_string('users/emails/verification_email.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send(fail_silently=False)


def send_welcome_email(email, name):
    """Sends the official welcome and bonus notification after successful verification."""
    subject = 'Welcome to Isheri Grills & Suya! 🔥'
    context = {'name': name}
    html_content = render_to_string('users/emails/welcome_email.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send(fail_silently=False)


def send_order_receipt(email, name, order_context):
    """Sends an order receipt email to the user after order completion."""
    subject = f"Your Isheri Grills Receipt — Order {order_context.get('order_id')}"
    context = {'name': name}
    context.update(order_context)
    html_content = render_to_string('users/emails/order_receipt.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send(fail_silently=False)
