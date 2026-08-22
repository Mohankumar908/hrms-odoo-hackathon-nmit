"""
DAYFLOW HRMS - Shared utility functions.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_notification_email(subject, template_name, context, recipient_list):
    """Send an HTML email using a Django template."""
    html_message = render_to_string(template_name, context)
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=True,
    )


def get_client_ip(request):
    """Extract the client IP address from a request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
