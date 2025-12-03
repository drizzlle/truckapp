from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_password_reset_email(user, token):
    subject = "Reset Your Password - TruckApp"
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}" if hasattr(settings, 'FRONTEND_URL') else f"http://localhost:3000/reset-password?token={token}"
    
    html_message = render_to_string('emails/password_reset.html', {
        'first_name': user.first_name or user.username,
        'reset_url': reset_url,
        'email': user.email,
    })
    
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)


def send_email_verification_email(user, code):
    subject = "Verify Your Email - TruckApp"
    
    html_message = render_to_string('emails/email_verification.html', {
        'first_name': user.first_name or user.username,
        'verification_code': code,
        'email': user.email,
    })
    
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)


def send_welcome_email(user, user_type='customer'):
    subject = "Welcome to TruckApp"
    template = 'emails/welcome_customer.html' if user_type == 'customer' else 'emails/welcome_driver.html'
    
    html_message = render_to_string(template, {
        'first_name': user.first_name or user.username,
        'email': user.email,
    })
    
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)


