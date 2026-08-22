from django.urls import path
from . import api_views
app_name = 'api_analytics'
urlpatterns = [
    path('dashboard/', api_views.dashboard_analytics, name='dashboard'),
    path('attendance-trend/', api_views.attendance_trend, name='attendance_trend'),
    path('workload/', api_views.workload_analysis, name='workload'),
    path('project-risk/', api_views.project_risk_analysis, name='project_risk'),
]
