"""
DAYFLOW HRMS - Project management models.
"""
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class Project(TimeStampedModel):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    client = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='managed_projects'
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='ProjectMember', related_name='projects'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planning')
    progress = models.PositiveIntegerField(default=0)  # 0-100 %
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'project'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def update_progress(self):
        """Recalculate project progress based on completed tasks."""
        from apps.tasks.models import Task
        tasks = Task.objects.filter(project=self)
        total = tasks.count()
        if total == 0:
            self.progress = 0
        else:
            completed = tasks.filter(status='completed').count()
            self.progress = round((completed / total) * 100)
        self.save(update_fields=['progress'])
        return self.progress


class ProjectMember(TimeStampedModel):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('designer', 'Designer'),
        ('tester', 'Tester'),
        ('analyst', 'Analyst'),
        ('member', 'Member'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'project_member'
        unique_together = ['project', 'user']

    def __str__(self):
        return f'{self.user} in {self.project.name}'
