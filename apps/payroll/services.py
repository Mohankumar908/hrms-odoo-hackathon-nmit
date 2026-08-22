"""
DAYFLOW HRMS - Payroll processing logic.
"""
from django.utils import timezone
from .models import Payroll
from apps.employees.models import EmployeeProfile, SalaryStructure
from apps.attendance.models import Attendance
import calendar


def generate_payroll(employee_id, month, year, processed_by):
    """Auto-generate a payroll record from salary structure and attendance."""
    try:
        profile = EmployeeProfile.objects.get(pk=employee_id)
        salary = profile.salary_structure
    except (EmployeeProfile.DoesNotExist, SalaryStructure.DoesNotExist):
        return None, 'Employee or salary structure not found.'

    # Check if already processed
    if Payroll.objects.filter(employee=profile, month=month, year=year).exists():
        return None, 'Payroll already exists for this period.'

    # Calculate working days in month
    _, total_days_in_month = calendar.monthrange(year, month)
    attendance_qs = Attendance.objects.filter(employee=profile, date__month=month, date__year=year)
    present_days = attendance_qs.filter(status='present').count()
    absent_days = attendance_qs.filter(status='absent').count()
    leave_days = attendance_qs.filter(status='leave').count()

    # Unpaid leave deduction (per day rate * absent days)
    daily_rate = float(salary.basic_salary) / total_days_in_month
    from decimal import Decimal
    unpaid_deduction = Decimal(str(round(daily_rate * absent_days, 2)))

    payroll = Payroll.objects.create(
        employee=profile,
        month=month,
        year=year,
        basic_salary=salary.basic_salary,
        house_allowance=salary.house_allowance,
        transport_allowance=salary.transport_allowance,
        medical_allowance=salary.medical_allowance,
        other_allowances=salary.other_allowances,
        tax_deduction=salary.tax_deduction,
        provident_fund=salary.provident_fund,
        unpaid_leave_deduction=unpaid_deduction,
        other_deductions=salary.other_deductions,
        working_days=total_days_in_month,
        present_days=present_days,
        absent_days=absent_days,
        leave_days=leave_days,
        status='processed',
        processed_by=processed_by,
        processed_at=timezone.now(),
    )
    return payroll, None
