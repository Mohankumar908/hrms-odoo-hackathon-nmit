from django.contrib import admin
from .models import Attendance, AttendanceCorrectionRequest


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status', 'working_hours', 'is_late']
    list_filter = ['status', 'date', 'is_late']
    search_fields = ['employee__full_name', 'employee__user__employee_id']
    date_hierarchy = 'date'


@admin.register(AttendanceCorrectionRequest)
class CorrectionRequestAdmin(admin.ModelAdmin):
    list_display = ['attendance', 'requested_by', 'status', 'created_at']
    list_filter = ['status']
