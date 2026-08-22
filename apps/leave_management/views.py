from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import LeaveRequest, LeaveType, LeaveBalance
from . import services


@login_required
def leave_list_view(request):
    user = request.user
    if user.role in ('admin', 'hr'):
        leaves  = LeaveRequest.objects.select_related('employee__user','leave_type').all()
        pending = leaves.filter(status='pending')
    else:
        leaves  = LeaveRequest.objects.filter(employee__user=user).select_related('leave_type')
        pending = None

    leave_types = LeaveType.objects.filter(is_active=True)
    balances    = LeaveBalance.objects.filter(employee__user=user) if hasattr(user, 'employee_profile') else []

    return render(request, 'leave_management/leave_list.html', {
        'leaves': leaves, 'pending': pending,
        'leave_types': leave_types, 'balances': balances,
    })


@login_required
def apply_leave_view(request):
    leave_types = LeaveType.objects.filter(is_active=True)

    if request.method == 'POST':
        leave_type_id = request.POST.get('leave_type', '').strip()
        start_str     = request.POST.get('start_date', '').strip()
        end_str       = request.POST.get('end_date', '').strip()
        reason        = request.POST.get('reason', '').strip()

        errors = []
        if not leave_type_id:
            errors.append('Leave type is required.')
        if not start_str:
            errors.append('Start date is required.')
        if not end_str:
            errors.append('End date is required.')
        if not reason:
            errors.append('Reason is required.')

        sd = ed = leave_type = None
        if leave_type_id and not errors:
            try:
                leave_type = LeaveType.objects.get(pk=leave_type_id, is_active=True)
            except LeaveType.DoesNotExist:
                errors.append('Invalid leave type selected.')

        if start_str and end_str and not errors:
            try:
                sd = datetime.strptime(start_str, '%Y-%m-%d').date()
                ed = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid date format.')

            if sd and ed:
                if ed < sd:
                    errors.append('End date cannot be before start date.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'leave_management/apply_leave.html', {
                'leave_types': leave_types,
                'form_data': request.POST,
            })

        # Business-rule validation (from services)
        try:
            profile = request.user.employee_profile
        except Exception:
            messages.error(request, 'No employee profile found for your account.')
            return redirect('leave_management:leave_list')

        biz_errors = services.validate_leave_request(profile, leave_type, sd, ed)
        if biz_errors:
            for e in biz_errors:
                messages.error(request, e)
            return render(request, 'leave_management/apply_leave.html', {
                'leave_types': leave_types,
                'form_data': request.POST,
            })

        LeaveRequest.objects.create(
            employee=profile,
            leave_type=leave_type,
            start_date=sd,
            end_date=ed,
            reason=reason,
        )
        messages.success(request, 'Leave request submitted successfully.')
        return redirect('leave_management:leave_list')

    return render(request, 'leave_management/apply_leave.html', {
        'leave_types': leave_types,
        'form_data': {},
    })


@login_required
def approve_leave_view(request, pk):
    if request.user.role not in ('admin', 'hr'):
        messages.error(request, 'Permission denied.')
        return redirect('leave_management:leave_list')
    if request.method != 'POST':
        return redirect('leave_management:leave_list')
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if leave.status != 'pending':
        messages.warning(request, f'This leave request is already {leave.status}.')
        return redirect('leave_management:leave_list')
    comment = request.POST.get('comment', 'Approved')
    services.approve_leave(leave, request.user, comment)
    messages.success(request, f'Leave approved for {leave.employee.full_name}.')
    return redirect('leave_management:leave_list')


@login_required
def reject_leave_view(request, pk):
    if request.user.role not in ('admin', 'hr'):
        messages.error(request, 'Permission denied.')
        return redirect('leave_management:leave_list')
    if request.method != 'POST':
        return redirect('leave_management:leave_list')
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if leave.status != 'pending':
        messages.warning(request, f'This leave request is already {leave.status}.')
        return redirect('leave_management:leave_list')
    comment = request.POST.get('comment', '').strip()
    if not comment:
        messages.error(request, 'Please provide a reason for rejection.')
        return redirect('leave_management:leave_list')
    services.reject_leave(leave, request.user, comment)
    messages.success(request, f'Leave rejected for {leave.employee.full_name}.')
    return redirect('leave_management:leave_list')


# ── Leave Types Management (Admin/HR) ─────────────────────────────────────────

@login_required
def leave_type_list_view(request):
    if request.user.role not in ('admin', 'hr'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            name = request.POST.get('name', '').strip()
            if name:
                LeaveType.objects.get_or_create(
                    name=name,
                    defaults={
                        'description':       request.POST.get('description', ''),
                        'max_days_per_year': int(request.POST.get('max_days_per_year') or 0),
                        'is_paid':           request.POST.get('is_paid') == 'on',
                        'requires_approval': request.POST.get('requires_approval') == 'on',
                        'is_active':         True,
                    }
                )
                messages.success(request, f'Leave type "{name}" created.')
            else:
                messages.error(request, 'Name is required.')
        elif action == 'toggle':
            lt_id = request.POST.get('id')
            lt = get_object_or_404(LeaveType, pk=lt_id)
            lt.is_active = not lt.is_active
            lt.save(update_fields=['is_active'])
            messages.success(request, f'"{lt.name}" {"activated" if lt.is_active else "deactivated"}.')
        return redirect('leave_management:leave_types')

    leave_types = LeaveType.objects.all().order_by('name')
    return render(request, 'leave_management/leave_types.html', {'leave_types': leave_types})
