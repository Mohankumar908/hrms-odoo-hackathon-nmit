"""
DAYFLOW HRMS - Attendance models.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from apps.employees.models import EmployeeProfile


class Attendance(TimeStampedModel):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
        ('holiday', 'Holiday'),
        ('weekend', 'Weekend'),
    ]

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(db_index=True)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_late = models.BooleanField(default=False)
    is_early_checkout = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    # IP address of check-in for audit
    check_in_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'attendance_record'
        unique_together = ['employee', 'date']
        ordering = ['-date']

    def __str__(self):
        return f'{self.employee.full_name} - {self.date} - {self.status}'

    def calculate_working_hours(self):
        if self.check_in and self.check_out:
            from datetime import datetime, date
            dt_in = datetime.combine(date.today(), self.check_in)
            dt_out = datetime.combine(date.today(), self.check_out)
            delta = dt_out - dt_in
            self.working_hours = round(delta.total_seconds() / 3600, 2)
        return self.working_hours


class AttendanceCorrectionRequest(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='correction_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='correction_requests')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_corrections'
    )
    requested_check_in = models.TimeField(null=True, blank=True)
    requested_check_out = models.TimeField(null=True, blank=True)
    requested_status = models.CharField(max_length=10, choices=Attendance.STATUS_CHOICES, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewer_comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'attendance_correction_request'
        ordering = ['-created_at']

    def __str__(self):
        return f'Correction: {self.attendance} - {self.status}'
