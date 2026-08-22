"""
DAYFLOW HRMS - Work updates helper functions.
"""
from django.utils import timezone
from .models import DailyWorkUpdate


def get_team_updates_for_project(project_id, limit=20):
    return DailyWorkUpdate.objects.filter(project_id=project_id).order_by('-date')[:limit]


def get_blockers_for_project(project_id):
    return DailyWorkUpdate.objects.filter(
        project_id=project_id
    ).exclude(blockers='').order_by('-date').values('date', 'blockers', 'employee__full_name')
