"""
DAYFLOW HRMS - Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Template-based views
    path('', include('apps.accounts.urls', namespace='accounts')),
    path('employees/', include('apps.employees.urls', namespace='employees')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('leave/', include('apps.leave_management.urls', namespace='leave_management')),
    path('payroll/', include('apps.payroll.urls', namespace='payroll')),
    path('projects/', include('apps.projects.urls', namespace='projects')),
    path('tasks/', include('apps.tasks.urls', namespace='tasks')),
    path('work-updates/', include('apps.work_updates.urls', namespace='work_updates')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),

    # REST API
    path('api/auth/', include('apps.accounts.api_urls', namespace='api_accounts')),
    path('api/employees/', include('apps.employees.api_urls', namespace='api_employees')),
    path('api/attendance/', include('apps.attendance.api_urls', namespace='api_attendance')),
    path('api/leaves/', include('apps.leave_management.api_urls', namespace='api_leave')),
    path('api/payroll/', include('apps.payroll.api_urls', namespace='api_payroll')),
    path('api/projects/', include('apps.projects.api_urls', namespace='api_projects')),
    path('api/tasks/', include('apps.tasks.api_urls', namespace='api_tasks')),
    path('api/work-updates/', include('apps.work_updates.api_urls', namespace='api_work_updates')),
    path('api/notifications/', include('apps.notifications.api_urls', namespace='api_notifications')),
    path('api/reports/', include('apps.reports.api_urls', namespace='api_reports')),
    path('api/analytics/', include('apps.analytics.api_urls', namespace='api_analytics')),

    # API docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
