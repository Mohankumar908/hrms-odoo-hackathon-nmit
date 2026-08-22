"""
DAYFLOW HRMS - Leave management models.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from apps.employees.models import EmployeeProfile


class LeaveType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    max_days_per_year = models.PositiveIntegerField(default=0)  # 0 = unlimited
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'leave_type'

    def __str__(self):
        return self.name


class LeaveBalance(TimeStampedModel):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='balances')
    year = models.PositiveIntegerField()
    allocated_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        db_table = 'leave_balance'
        unique_together = ['employee', 'leave_type', 'year']

    @property
    def remaining_days(self):
        return self.allocated_days - self.used_days

    def __str__(self):
        return f'{self.employee.full_name} - {self.leave_type.name} ({self.year})'


class LeaveRequest(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='requests')
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='reviewed_leaves'
    )
    reviewer_comment = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'leave_request'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee.full_name} - {self.leave_type.name} ({self.start_date} to {self.end_date})'

    def calculate_total_days(self):
        delta = (self.end_date - self.start_date).days + 1
        self.total_days = delta
        return delta

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.calculate_total_days()
        super().save(*args, **kwargs)
