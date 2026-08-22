from django.contrib import admin
from .models import Task, TaskComment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'priority', 'status', 'progress', 'deadline']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['title', 'project__name']
    filter_horizontal = ['assignees']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'is_blocker', 'created_at']
    list_filter = ['is_blocker']
