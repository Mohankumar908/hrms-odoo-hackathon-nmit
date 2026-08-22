from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Notification(TimeStampedModel):
    TYPE_CHOICES = [
        ('leave_submitted','Leave Submitted'),('leave_approved','Leave Approved'),
        ('leave_rejected','Leave Rejected'),('task_assigned','Task Assigned'),
        ('task_reassigned','Task Reassigned'),('task_completed','Task Completed'),
        ('task_deadline','Task Deadline Approaching'),('attendance_reminder','Attendance Reminder'),
        ('late_attendance','Late Attendance'),('work_update_reminder','Work Update Reminder'),
        ('project_delay','Project Delay'),('announcement','Announcement'),('general','General'),
    ]
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_url = models.CharField(max_length=300, blank=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient} - {self.title}'
