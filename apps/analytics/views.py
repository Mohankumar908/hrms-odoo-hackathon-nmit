from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from apps.employees.models import EmployeeProfile, Department
from apps.attendance.models import Attendance
from apps.leave_management.models import LeaveRequest
from apps.projects.models import Project
from apps.tasks.models import Task
import json


@login_required
def analytics_dashboard(request):
    if request.user.role not in ('admin','hr'): raise PermissionDenied
    today = timezone.localdate()
    m, y  = today.month, today.year

    total_emp     = EmployeeProfile.objects.filter(employment_status='active').count()
    by_dept       = list(Department.objects.annotate(count=Count('employees')).values('name','count').order_by('-count')[:8])
    by_status     = dict(EmployeeProfile.objects.values_list('employment_status').annotate(c=Count('id')))

    att_qs        = Attendance.objects.filter(date__month=m, date__year=y)
    att_present   = att_qs.filter(status='present').count()
    att_absent    = att_qs.filter(status='absent').count()
    att_leave     = att_qs.filter(status='leave').count()
    avg_hours     = att_qs.filter(status='present').aggregate(a=Avg('working_hours'))['a'] or 0

    leave_status  = dict(LeaveRequest.objects.values_list('status').annotate(c=Count('id')))
    proj_status   = dict(Project.objects.values_list('status').annotate(c=Count('id')))
    task_status   = dict(Task.objects.values_list('status').annotate(c=Count('id')))
    task_priority = dict(Task.objects.values_list('priority').annotate(c=Count('id')))

    return render(request, 'analytics/analytics.html', {
        'total_emp': total_emp,
        'by_dept_json': json.dumps(by_dept),
        'by_status': by_status,
        'att_present': att_present, 'att_absent': att_absent, 'att_leave': att_leave,
        'avg_hours': round(avg_hours, 1),
        'leave_status': leave_status,
        'proj_status': proj_status,
        'task_status': task_status,
        'task_priority': task_priority,
        'active_projects': proj_status.get('active',0),
        'completed_projects': proj_status.get('completed',0),
        'pending_leaves': leave_status.get('pending',0),
        'month_label': today.strftime('%B %Y'),
    })
