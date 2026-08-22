"""
DAYFLOW HRMS - Daily Work Update models.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from apps.employees.models import EmployeeProfile
from apps.projects.models import Project
from apps.tasks.models import Task


class DailyWorkUpdate(TimeStampedModel):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE, related_name='work_updates')
    date = models.DateField(db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='work_updates')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='work_updates')

    work_completed = models.TextField(help_text='What work was completed today?')
    work_in_progress = models.TextField(blank=True, help_text='What is currently in progress?')
    pending_work = models.TextField(blank=True, help_text='What work is pending?')
    blockers = models.TextField(blank=True, help_text='Any blockers or issues?')
    hours_worked = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    progress_percentage = models.PositiveIntegerField(default=0)  # Task-level progress update
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'daily_work_update'
        unique_together = ['employee', 'date', 'task']
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.employee.full_name} - {self.date} - {self.project.name}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync task progress
        if self.task and self.progress_percentage:
            self.task.progress = self.progress_percentage
            self.task.save(update_fields=['progress'])
