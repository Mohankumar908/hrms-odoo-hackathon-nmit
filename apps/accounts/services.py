"""
DAYFLOW HRMS - Accounts business logic layer.
"""
import uuid
from django.utils import timezone
from django.conf import settings
from core.utils import send_notification_email
from .models import User


def send_verification_email(user):
    verify_url = f"{settings.FRONTEND_URL}/accounts/verify-email/{user.email_verification_token}/"
    send_notification_email(
        subject='Verify your DAYFLOW account',
        template_name='accounts/emails/verify_email.html',
        context={'user': user, 'verify_url': verify_url},
        recipient_list=[user.email],
    )


def verify_email_token(token):
    try:
        user = User.objects.get(email_verification_token=token, is_email_verified=False)
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        return user
    except User.DoesNotExist:
        return None


def send_password_reset_email(email):
    try:
        user = User.objects.get(email=email, is_active=True)
        user.password_reset_token = uuid.uuid4()
        user.password_reset_token_created = timezone.now()
        user.save(update_fields=['password_reset_token', 'password_reset_token_created'])
        reset_url = f"{settings.FRONTEND_URL}/accounts/reset-password/{user.password_reset_token}/"
        send_notification_email(
            subject='Reset your DAYFLOW password',
            template_name='accounts/emails/reset_password.html',
            context={'user': user, 'reset_url': reset_url},
            recipient_list=[user.email],
        )
        return True
    except User.DoesNotExist:
        return False


def reset_password(token, new_password):
    from datetime import timedelta
    try:
        user = User.objects.get(password_reset_token=token)
        # Token valid for 1 hour
        if timezone.now() > user.password_reset_token_created + timedelta(hours=1):
            return None, 'Token expired.'
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_token_created = None
        user.save(update_fields=['password', 'password_reset_token', 'password_reset_token_created'])
        return user, None
    except User.DoesNotExist:
        return None, 'Invalid token.'
