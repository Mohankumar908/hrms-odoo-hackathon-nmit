from django.contrib import admin
from .models import DailyWorkUpdate

@admin.register(DailyWorkUpdate)
class DailyWorkUpdateAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'project', 'task', 'hours_worked', 'progress_percentage']
    list_filter = ['date', 'project']
    search_fields = ['employee__full_name']
