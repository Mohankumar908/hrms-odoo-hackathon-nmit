"""
DAYFLOW HRMS - Leave management business logic.
"""
from django.utils import timezone
from .models import LeaveRequest, LeaveBalance, LeaveType
from apps.attendance.services import apply_leave_to_attendance


def validate_leave_request(employee, leave_type, start_date, end_date):
    """Validate business rules before creating a leave request."""
    errors = []

    if start_date > end_date:
        errors.append('Start date cannot be after end date.')

    if start_date < timezone.localdate():
        errors.append('Cannot apply leave for past dates.')

    # Check overlapping leaves
    overlapping = LeaveRequest.objects.filter(
        employee=employee,
        status__in=('pending', 'approved'),
        start_date__lte=end_date,
        end_date__gte=start_date,
    ).exists()
    if overlapping:
        errors.append('You already have a leave request for overlapping dates.')

    # Check balance for paid leaves
    if leave_type.max_days_per_year > 0:
        year = start_date.year
        balance = LeaveBalance.objects.filter(employee=employee, leave_type=leave_type, year=year).first()
        if balance:
            total_days = (end_date - start_date).days + 1
            if balance.remaining_days < total_days:
                errors.append(f'Insufficient leave balance. Available: {balance.remaining_days} days.')

    return errors


def approve_leave(leave_request, reviewer, comment=''):
    leave_request.status = 'approved'
    leave_request.reviewed_by = reviewer
    leave_request.reviewer_comment = comment
    leave_request.reviewed_at = timezone.now()
    leave_request.save()

    # Update leave balance
    year = leave_request.start_date.year
    balance = LeaveBalance.objects.filter(
        employee=leave_request.employee,
        leave_type=leave_request.leave_type,
        year=year
    ).first()
    if balance:
        balance.used_days += leave_request.total_days
        balance.save()

    # Apply attendance
    apply_leave_to_attendance(leave_request)

    # Notify employee
    from apps.notifications.services import create_notification
    create_notification(
        recipient=leave_request.employee.user,
        notification_type='leave_approved',
        title='Leave Approved',
        message=f'Your {leave_request.leave_type.name} request from {leave_request.start_date} to {leave_request.end_date} has been approved.',
        related_object_id=leave_request.id,
    )


def reject_leave(leave_request, reviewer, comment=''):
    leave_request.status = 'rejected'
    leave_request.reviewed_by = reviewer
    leave_request.reviewer_comment = comment
    leave_request.reviewed_at = timezone.now()
    leave_request.save()

    from apps.notifications.services import create_notification
    create_notification(
        recipient=leave_request.employee.user,
        notification_type='leave_rejected',
        title='Leave Rejected',
        message=f'Your {leave_request.leave_type.name} request has been rejected. Reason: {comment}',
        related_object_id=leave_request.id,
    )
