"""
DAYFLOW HRMS - Task management models.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from apps.projects.models import Project


class Task(TimeStampedModel):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
        ('on_hold', 'On Hold'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')
    progress = models.PositiveIntegerField(default=0)  # 0-100%

    assignees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_tasks', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_tasks'
    )

    deadline = models.DateField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)

    class Meta:
        db_table = 'task'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.project.name}]'

    def check_if_delayed(self):
        from django.utils import timezone
        if self.deadline and timezone.localdate() > self.deadline and self.status not in ('completed',):
            self.status = 'delayed'
            self.save(update_fields=['status'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update project progress after saving task
        if self.project_id:
            self.project.update_progress()


class TaskComment(TimeStampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_comments')
    content = models.TextField()
    is_blocker = models.BooleanField(default=False)

    class Meta:
        db_table = 'task_comment'
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.task.title}'
