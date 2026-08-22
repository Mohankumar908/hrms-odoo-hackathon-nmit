from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class SavedReport(TimeStampedModel):
    REPORT_TYPE_CHOICES = [
        ('attendance','Attendance'),('payroll','Payroll'),
        ('leave','Leave'),('task','Task'),('project','Project'),
    ]
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filters = models.JSONField(default=dict)
    file = models.FileField(upload_to='reports/', null=True, blank=True)

    class Meta:
        db_table = 'saved_report'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
