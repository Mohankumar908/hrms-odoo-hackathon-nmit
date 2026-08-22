"""
DAYFLOW HRMS - Attendance business logic.
"""
from django.utils import timezone
from django.conf import settings
from .models import Attendance, AttendanceCorrectionRequest
from apps.employees.models import EmployeeProfile


# Standard work hours
WORK_START_HOUR = 9   # 9:00 AM
LATE_THRESHOLD_MINUTES = 15  # grace period


def check_in(user, ip_address=None):
    """Record employee check-in. Returns (attendance, created, error)."""
    try:
        profile = user.employee_profile
    except EmployeeProfile.DoesNotExist:
        return None, False, 'Employee profile not found.'

    today = timezone.localdate()
    now_time = timezone.localtime().time()

    # Check if already checked in
    attendance, created = Attendance.objects.get_or_create(
        employee=profile,
        date=today,
        defaults={
            'check_in': now_time,
            'status': 'present',
            'check_in_ip': ip_address,
        }
    )
    if not created:
        if attendance.check_in:
            return attendance, False, 'Already checked in today.'
        attendance.check_in = now_time
        attendance.status = 'present'
        attendance.check_in_ip = ip_address

    # Check if late
    from datetime import time
    if now_time > time(WORK_START_HOUR, LATE_THRESHOLD_MINUTES):
        attendance.is_late = True

    attendance.save()

    # Notify employee and HR about late check-in
    if attendance.is_late:
        from apps.notifications.services import create_notification
        from apps.accounts.models import User
        create_notification(
            recipient=user,
            notification_type='late_attendance',
            title='Late Check-in Recorded',
            message=f'Your check-in at {now_time.strftime("%H:%M")} was recorded as late (after {WORK_START_HOUR:02d}:{LATE_THRESHOLD_MINUTES:02d}).',
            action_url='/attendance/',
        )
        # Also notify HR
        for hr_user in User.objects.filter(role__in=('admin', 'hr'), is_active=True):
            create_notification(
                recipient=hr_user,
                notification_type='late_attendance',
                title=f'Late Arrival: {user.full_name}',
                message=f'{user.full_name} ({user.employee_id}) checked in late at {now_time.strftime("%H:%M")} today.',
                action_url='/attendance/admin/',
            )

    return attendance, created, None


def check_out(user):
    """Record employee check-out. Returns (attendance, error)."""
    try:
        profile = user.employee_profile
    except EmployeeProfile.DoesNotExist:
        return None, 'Employee profile not found.'

    today = timezone.localdate()
    now_time = timezone.localtime().time()

    try:
        attendance = Attendance.objects.get(employee=profile, date=today)
    except Attendance.DoesNotExist:
        return None, 'No check-in record found for today.'

    if not attendance.check_in:
        return None, 'You have not checked in yet.'

    if attendance.check_out:
        return attendance, 'Already checked out today.'

    attendance.check_out = now_time
    attendance.calculate_working_hours()

    # Check early checkout (less than 8 hours worked)
    if float(attendance.working_hours) < 8.0:
        attendance.is_early_checkout = True

    # Half day if worked less than 4 hours
    if float(attendance.working_hours) < 4.0:
        attendance.status = 'half_day'

    attendance.save()
    return attendance, None


def apply_leave_to_attendance(leave_request):
    """When a leave is approved, create/update attendance records for those dates."""
    from datetime import timedelta
    current = leave_request.start_date
    while current <= leave_request.end_date:
        profile = leave_request.employee
        Attendance.objects.update_or_create(
            employee=profile,
            date=current,
            defaults={
                'status': 'leave',
                'notes': f'Leave: {leave_request.leave_type.name}',
            }
        )
        current += timedelta(days=1)
