"""
DAYFLOW HRMS - Report generation services.
"""
import csv
import io
from django.http import HttpResponse
from django.utils import timezone


def attendance_report_data(filters):
    from apps.attendance.models import Attendance
    qs = Attendance.objects.select_related('employee__user', 'employee__department')
    if filters.get('employee_id'):
        qs = qs.filter(employee__user__employee_id=filters['employee_id'])
    if filters.get('department'):
        qs = qs.filter(employee__department_id=filters['department'])
    if filters.get('month') and filters.get('year'):
        qs = qs.filter(date__month=filters['month'], date__year=filters['year'])
    return qs


def payroll_report_data(filters):
    from apps.payroll.models import Payroll
    qs = Payroll.objects.select_related('employee__user', 'employee__department')
    if filters.get('month'):
        qs = qs.filter(month=filters['month'])
    if filters.get('year'):
        qs = qs.filter(year=filters['year'])
    if filters.get('department'):
        qs = qs.filter(employee__department_id=filters['department'])
    return qs


def export_attendance_csv(filters):
    qs = attendance_report_data(filters)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Employee ID', 'Name', 'Department', 'Date', 'Check In', 'Check Out', 'Status', 'Working Hours', 'Late'])
    for r in qs:
        writer.writerow([
            r.employee.user.employee_id, r.employee.full_name,
            r.employee.department.name if r.employee.department else '',
            r.date, r.check_in, r.check_out, r.status, r.working_hours, r.is_late
        ])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{timezone.now().date()}.csv"'
    return response


def export_payroll_csv(filters):
    qs = payroll_report_data(filters)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Employee ID', 'Name', 'Month', 'Year', 'Basic', 'Gross', 'Deductions', 'Net', 'Status'])
    for r in qs:
        writer.writerow([
            r.employee.user.employee_id, r.employee.full_name,
            r.month, r.year, r.basic_salary, r.gross_salary, r.total_deductions, r.net_salary, r.status
        ])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payroll_report_{timezone.now().date()}.csv"'
    return response
