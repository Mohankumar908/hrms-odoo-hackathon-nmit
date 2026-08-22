from django.urls import path
from . import api_views
app_name = 'api_reports'
urlpatterns = [
    path('attendance/', api_views.attendance_report, name='attendance'),
    path('payroll/', api_views.payroll_report, name='payroll'),
    path('leave/', api_views.leave_report, name='leave'),
    path('tasks/', api_views.task_report, name='tasks'),
]
