from .models import Notification

def create_notification(recipient, notification_type, title, message, related_object_id=None, action_url=''):
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        related_object_id=related_object_id,
        action_url=action_url,
    )

def mark_all_read(user):
    Notification.objects.filter(recipient=user, is_read=False).update(is_read=True)

def broadcast_announcement(users, title, message):
    notifications = [
        Notification(recipient=u, notification_type='announcement', title=title, message=message)
        for u in users
    ]
    Notification.objects.bulk_create(notifications)
