from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core.permissions import IsAdminOrHR
from . import services


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def attendance_report(request):
    filters = {
        'employee_id': request.query_params.get('employee_id'),
        'department': request.query_params.get('department'),
        'month': request.query_params.get('month'),
        'year': request.query_params.get('year'),
    }
    fmt = request.query_params.get('format', 'json')
    if fmt == 'csv':
        return services.export_attendance_csv(filters)
    qs = services.attendance_report_data(filters)
    from apps.attendance.serializers import AttendanceSerializer
    return Response(AttendanceSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def payroll_report(request):
    filters = {
        'month': request.query_params.get('month'),
        'year': request.query_params.get('year'),
        'department': request.query_params.get('department'),
    }
    fmt = request.query_params.get('format', 'json')
    if fmt == 'csv':
        return services.export_payroll_csv(filters)
    qs = services.payroll_report_data(filters)
    from apps.payroll.serializers import PayrollSerializer
    return Response(PayrollSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def leave_report(request):
    from apps.leave_management.models import LeaveRequest
    from apps.leave_management.serializers import LeaveRequestSerializer
    qs = LeaveRequest.objects.select_related('employee__user', 'leave_type').all()
    status_f = request.query_params.get('status')
    department = request.query_params.get('department')
    if status_f:
        qs = qs.filter(status=status_f)
    if department:
        qs = qs.filter(employee__department_id=department)
    return Response(LeaveRequestSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def task_report(request):
    from apps.tasks.models import Task
    from apps.tasks.serializers import TaskListSerializer
    qs = Task.objects.select_related('project').prefetch_related('assignees').all()
    status_f = request.query_params.get('status')
    project = request.query_params.get('project')
    if status_f:
        qs = qs.filter(status=status_f)
    if project:
        qs = qs.filter(project_id=project)
    return Response(TaskListSerializer(qs, many=True).data)
