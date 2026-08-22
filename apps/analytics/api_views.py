from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core.permissions import IsAdminOrHR
from django.utils import timezone
from django.db.models import Count, Avg, Sum


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def dashboard_analytics(request):
    from apps.employees.models import EmployeeProfile, Department
    from apps.attendance.models import Attendance
    from apps.leave_management.models import LeaveRequest
    from apps.tasks.models import Task
    from apps.projects.models import Project
    from apps.payroll.models import Payroll

    today = timezone.localdate()
    month = today.month
    year = today.year

    # Employee stats
    total_emp = EmployeeProfile.objects.filter(employment_status='active').count()
    dept_dist = list(Department.objects.annotate(count=Count('employees')).values('name', 'count'))

    # Attendance stats (this month)
    att_month = Attendance.objects.filter(date__month=month, date__year=year)
    present_pct = round((att_month.filter(status='present').count() / max(att_month.count(), 1)) * 100, 1)
    late_count = att_month.filter(is_late=True).count()

    # Today
    today_att = Attendance.objects.filter(date=today)
    today_present = today_att.filter(status='present').count()
    today_absent = today_att.filter(status='absent').count()
    today_leave = today_att.filter(status='leave').count()

    # Leave stats
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    approved_this_month = LeaveRequest.objects.filter(status='approved', start_date__month=month).count()

    # Task stats
    task_stats = {
        'total': Task.objects.count(),
        'completed': Task.objects.filter(status='completed').count(),
        'in_progress': Task.objects.filter(status='in_progress').count(),
        'delayed': Task.objects.filter(status='delayed').count(),
        'not_started': Task.objects.filter(status='not_started').count(),
    }

    # Project stats
    project_stats = {
        'total': Project.objects.count(),
        'active': Project.objects.filter(status='active').count(),
        'completed': Project.objects.filter(status='completed').count(),
        'delayed': Project.objects.filter(status='delayed').count(),
        'on_hold': Project.objects.filter(status='on_hold').count(),
    }

    # Payroll summary this month
    payroll_qs = Payroll.objects.filter(month=month, year=year)
    from django.db.models import ExpressionWrapper, FloatField, F
    payroll_summary = payroll_qs.aggregate(
        total_gross=Sum('basic_salary'),
        avg_basic=Avg('basic_salary'),
        count=Count('id'),
    )

    return Response({
        'employees': {'total': total_emp, 'department_distribution': dept_dist},
        'attendance': {
            'today_present': today_present,
            'today_absent': today_absent,
            'today_leave': today_leave,
            'monthly_present_percent': present_pct,
            'late_count_this_month': late_count,
        },
        'leave': {'pending': pending_leaves, 'approved_this_month': approved_this_month},
        'tasks': task_stats,
        'projects': project_stats,
        'payroll': payroll_summary,
    })


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def attendance_trend(request):
    """Last 30 days attendance trend for Chart.js."""
    from apps.attendance.models import Attendance
    from datetime import timedelta
    today = timezone.localdate()
    dates = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    data = []
    for d in dates:
        att = Attendance.objects.filter(date=d)
        data.append({
            'date': str(d),
            'present': att.filter(status='present').count(),
            'absent': att.filter(status='absent').count(),
            'leave': att.filter(status='leave').count(),
        })
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def workload_analysis(request):
    """AI feature: detect employees with high workload."""
    from apps.tasks.models import Task
    from apps.accounts.models import User
    from django.db.models import Count

    workload = (
        User.objects.filter(assigned_tasks__status__in=['in_progress', 'not_started'])
        .annotate(active_tasks=Count('assigned_tasks'))
        .values('employee_id', 'email', 'active_tasks')
        .order_by('-active_tasks')
    )

    avg = sum(w['active_tasks'] for w in workload) / max(len(workload), 1)
    result = []
    for w in workload:
        risk = 'high' if w['active_tasks'] > avg * 1.5 else ('medium' if w['active_tasks'] > avg else 'normal')
        result.append({**w, 'risk': risk, 'avg_tasks': round(avg, 1)})

    return Response({'workload': result, 'average_tasks_per_employee': round(avg, 1)})


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def project_risk_analysis(request):
    """AI feature: identify projects at risk of delay."""
    from apps.projects.models import Project
    from apps.tasks.models import Task
    from django.utils import timezone

    today = timezone.localdate()
    projects = Project.objects.filter(status__in=['active', 'planning'])
    result = []

    for p in projects:
        tasks = Task.objects.filter(project=p)
        total = tasks.count()
        completed = tasks.filter(status='completed').count()
        delayed = tasks.filter(status='delayed').count()
        overdue = tasks.filter(deadline__lt=today).exclude(status='completed').count()

        completion_rate = round((completed / max(total, 1)) * 100, 1)
        risk_score = delayed + overdue * 2
        risk_level = 'high' if risk_score >= 5 else ('medium' if risk_score >= 2 else 'low')

        days_left = (p.end_date - today).days if p.end_date else None

        result.append({
            'id': p.id, 'name': p.name, 'status': p.status,
            'completion_rate': completion_rate,
            'delayed_tasks': delayed, 'overdue_tasks': overdue,
            'days_left': days_left, 'risk_level': risk_level,
        })

    result.sort(key=lambda x: ['high', 'medium', 'low'].index(x['risk_level']))
    return Response(result)
