from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from .models import EmployeeProfile, Department, Designation


# ── Helpers ───────────────────────────────────────────────────────────────────

def _shared_form_context(profile=None, post_data=None):
    """Common context for create/edit forms."""
    post_data = post_data or {}
    return {
        'departments':  Department.objects.all(),
        'designations': Designation.objects.select_related('department').all(),
        'employment_status_choices': EmployeeProfile.EMPLOYMENT_STATUS_CHOICES,
        'employment_type_choices':   EmployeeProfile.EMPLOYMENT_TYPE_CHOICES,
        'gender_choices':            EmployeeProfile.GENDER_CHOICES,
        'profile':    profile,
        'form_data':  post_data,
    }


# ── Dashboards ────────────────────────────────────────────────────────────────

@login_required
def employee_dashboard(request):
    user = request.user
    try:
        profile = user.employee_profile
    except EmployeeProfile.DoesNotExist:
        profile = None
    from apps.attendance.models import Attendance
    from apps.leave_management.models import LeaveRequest
    from apps.tasks.models import Task
    from apps.notifications.models import Notification
    today = timezone.now().date()
    today_att  = Attendance.objects.filter(employee__user=user, date=today).first() if profile else None
    pending_lv = LeaveRequest.objects.filter(employee__user=user, status='pending').count() if profile else 0
    my_tasks   = Task.objects.filter(assignees=user, status__in=['not_started','in_progress']).count() if profile else 0
    notifs     = Notification.objects.filter(recipient=user, is_read=False).order_by('-created_at')[:5]
    return render(request, 'dashboard/employee_dashboard.html', {
        'profile': profile, 'today_attendance': today_att,
        'pending_leaves': pending_lv, 'my_tasks': my_tasks,
        'notifications': notifs, 'today': today,
    })


@login_required
def admin_dashboard(request):
    if request.user.role not in ('admin', 'hr'):
        return redirect('employees:employee_dashboard')
    from apps.attendance.models import Attendance
    from apps.leave_management.models import LeaveRequest
    from apps.projects.models import Project
    from apps.tasks.models import Task
    today = timezone.now().date()
    total_employees  = EmployeeProfile.objects.filter(employment_status='active').count()
    today_present    = Attendance.objects.filter(date=today, status='present').count()
    today_absent     = Attendance.objects.filter(date=today, status='absent').count()
    on_leave_today   = Attendance.objects.filter(date=today, status='leave').count()
    pending_leaves   = LeaveRequest.objects.filter(status='pending').count()
    active_projects  = Project.objects.filter(status='active').count()
    active_tasks     = Task.objects.filter(status='in_progress').count()
    completed_tasks  = Task.objects.filter(status='completed').count()
    delayed_tasks    = Task.objects.filter(status='delayed').count()
    recent_leaves    = LeaveRequest.objects.select_related('employee__user','leave_type').filter(status='pending').order_by('-created_at')[:5]
    recent_employees = EmployeeProfile.objects.select_related('user','department').order_by('-created_at')[:5]
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_employees': total_employees, 'today_present': today_present,
        'today_absent': today_absent, 'on_leave_today': on_leave_today,
        'pending_leaves': pending_leaves, 'active_projects': active_projects,
        'active_tasks': active_tasks, 'completed_tasks': completed_tasks,
        'delayed_tasks': delayed_tasks, 'recent_leaves': recent_leaves,
        'recent_employees': recent_employees, 'today': today,
    })


def hr_dashboard(request):
    return admin_dashboard(request)


# ── Profile ───────────────────────────────────────────────────────────────────

@login_required
def employee_profile_view(request, pk=None):
    user = request.user
    if pk and user.role in ('admin', 'hr'):
        profile = get_object_or_404(EmployeeProfile, pk=pk)
    else:
        # Try to get the profile; if it doesn't exist, create a minimal one
        try:
            profile = user.employee_profile
        except EmployeeProfile.DoesNotExist:
            # Auto-create a basic profile for users who don't have one yet
            profile = EmployeeProfile.objects.create(
                user=user,
                full_name=user.email.split('@')[0],
                first_name='',
                last_name='',
                employment_status='active',
            )
            messages.info(request, 'Your profile has been created. Please fill in your details.')

    if request.method == 'POST':
        for f in ['phone', 'address']:
            if f in request.POST:
                setattr(profile, f, request.POST[f])
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, 'Profile updated.')
        return redirect('employees:profile')
    return render(request, 'employees/profile.html', {'profile': profile})


# ── List ──────────────────────────────────────────────────────────────────────

@login_required
def employee_list_view(request):
    if request.user.role not in ('admin', 'hr'):
        return redirect('employees:employee_dashboard')
    employees   = EmployeeProfile.objects.select_related('user','department','designation').filter(user__role='employee')
    departments = Department.objects.all()
    dept   = request.GET.get('department')
    status = request.GET.get('status')
    q      = request.GET.get('q', '').strip()
    if dept:   employees = employees.filter(department_id=dept)
    if status: employees = employees.filter(employment_status=status)
    if q:      employees = employees.filter(full_name__icontains=q)
    return render(request, 'employees/employee_list.html', {
        'employees': employees, 'departments': departments,
        'filter_dept': dept, 'filter_status': status, 'filter_q': q,
        'list_type': 'employee',
    })


@login_required
def hr_list_view(request):
    if request.user.role != 'admin':
        raise PermissionDenied
    hrs = EmployeeProfile.objects.select_related('user','department','designation').filter(user__role='hr')
    return render(request, 'employees/employee_list.html', {
        'employees': hrs, 'departments': Department.objects.all(),
        'list_type': 'hr',
    })


# ── Create ────────────────────────────────────────────────────────────────────

@login_required
def employee_create_view(request, role='employee'):
    """
    Create accounts.
    - role='employee' → Admin OR HR can create
    - role='hr'       → Admin ONLY
    """
    if request.user.role == 'employee':
        raise PermissionDenied
    if role == 'hr' and request.user.role != 'admin':
        messages.error(request, 'Only Admin can create HR accounts.')
        raise PermissionDenied

    ctx = _shared_form_context(post_data=request.POST if request.method == 'POST' else {})
    ctx['action'] = 'Create'
    ctx['target_role'] = role
    ctx['role_label'] = 'HR' if role == 'hr' else 'Employee'
    ctx['can_change_role'] = (request.user.role == 'admin')

    if request.method == 'POST':
        from apps.accounts.models import User
        email       = request.POST.get('email', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        password    = request.POST.get('password', '')
        password2   = request.POST.get('password2', '')

        errors = []
        if not email:         errors.append('Email is required.')
        if not employee_id:   errors.append('Employee ID is required.')
        if not first_name:    errors.append('First name is required.')
        if not password:      errors.append('Password is required.')
        if password != password2: errors.append('Passwords do not match.')
        if len(password) < 8: errors.append('Password must be at least 8 characters.')
        if not errors:
            if User.objects.filter(email=email).exists():
                errors.append('Email already in use.')
            if User.objects.filter(employee_id=employee_id).exists():
                errors.append('Employee ID already in use.')

        if errors:
            for e in errors: messages.error(request, e)
            return render(request, 'employees/employee_form.html', ctx)

        u = User.objects.create_user(
            email=email, employee_id=employee_id,
            password=password, role=role, is_email_verified=True,
        )
        EmployeeProfile.objects.create(
            user=u,
            first_name=first_name,
            last_name=last_name,
            full_name=f'{first_name} {last_name}'.strip(),
            phone=request.POST.get('phone', ''),
            gender=request.POST.get('gender', ''),
            department_id=request.POST.get('department') or None,
            designation_id=request.POST.get('designation') or None,
            joining_date=request.POST.get('joining_date') or None,
            employment_status=request.POST.get('employment_status', 'active'),
            employment_type=request.POST.get('employment_type', 'full_time'),
        )
        messages.success(request, f'{ctx["role_label"]} account for {first_name} {last_name} created successfully.')
        return redirect('employees:hr_list' if role == 'hr' else 'employees:employee_list')

    return render(request, 'employees/employee_form.html', ctx)


# ── Edit ──────────────────────────────────────────────────────────────────────

@login_required
def employee_edit_view(request, pk):
    if request.user.role not in ('admin', 'hr'):
        raise PermissionDenied

    profile = get_object_or_404(EmployeeProfile.objects.select_related('user'), pk=pk)

    # Permission rules:
    # - HR can only edit employees (role='employee')
    # - Admin can edit anyone
    if request.user.role == 'hr' and profile.user.role != 'employee':
        messages.error(request, 'HR can only edit Employee accounts.')
        raise PermissionDenied

    ctx = _shared_form_context(profile=profile)
    ctx['action'] = 'Edit'
    ctx['target_role'] = profile.user.role
    ctx['role_label'] = profile.user.get_role_display()
    ctx['can_change_role'] = (request.user.role == 'admin')

    if request.method == 'POST':
        profile.first_name        = request.POST.get('first_name', profile.first_name).strip()
        profile.last_name         = request.POST.get('last_name', profile.last_name).strip()
        profile.phone             = request.POST.get('phone', profile.phone)
        profile.gender            = request.POST.get('gender', profile.gender)
        profile.address           = request.POST.get('address', profile.address)
        profile.department_id     = request.POST.get('department') or None
        profile.designation_id    = request.POST.get('designation') or None
        profile.joining_date      = request.POST.get('joining_date') or None
        profile.employment_status = request.POST.get('employment_status', profile.employment_status)
        profile.employment_type   = request.POST.get('employment_type', profile.employment_type)
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()

        # Only Admin can change role or activate/deactivate
        if request.user.role == 'admin':
            new_role = request.POST.get('role')
            if new_role and new_role in ('admin', 'hr', 'employee'):
                profile.user.role = new_role
                profile.user.save(update_fields=['role'])

            is_active = request.POST.get('is_active') == '1'
            if profile.user.is_active != is_active:
                profile.user.is_active = is_active
                profile.user.save(update_fields=['is_active'])

        # Password reset (both Admin and HR can reset employee passwords; Admin can reset anyone's)
        new_pwd = request.POST.get('new_password', '').strip()
        if new_pwd:
            if len(new_pwd) < 8:
                messages.error(request, 'New password must be at least 8 characters.')
                return render(request, 'employees/employee_form.html', ctx)
            profile.user.set_password(new_pwd)
            profile.user.save(update_fields=['password'])
            messages.info(request, 'Password updated.')

        messages.success(request, f'{profile.full_name} updated successfully.')
        return redirect('employees:hr_list' if profile.user.role == 'hr' else 'employees:employee_list')

    return render(request, 'employees/employee_form.html', ctx)


# ── Delete ────────────────────────────────────────────────────────────────────

@login_required
def employee_delete_view(request, pk):
    """Only Admin can delete accounts."""
    if request.user.role != 'admin':
        messages.error(request, 'Only Admin can delete accounts.')
        raise PermissionDenied
    profile = get_object_or_404(EmployeeProfile, pk=pk)
    if request.method == 'POST':
        profile.user.delete()
        messages.success(request, 'Account deleted.')
        return redirect('employees:employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'profile': profile})


# ── Toggle active ─────────────────────────────────────────────────────────────

@login_required
def toggle_active_view(request, pk):
    """Only Admin can activate/deactivate accounts."""
    if request.user.role != 'admin':
        messages.error(request, 'Only Admin can activate or deactivate accounts.')
        raise PermissionDenied
    profile = get_object_or_404(EmployeeProfile, pk=pk)
    if request.method == 'POST':
        profile.user.is_active = not profile.user.is_active
        profile.user.save(update_fields=['is_active'])
        state = 'activated' if profile.user.is_active else 'deactivated'
        messages.success(request, f'{profile.full_name} {state}.')
    return redirect(request.POST.get('next', 'employees:employee_list'))


# ── Salary Structure UI ───────────────────────────────────────────────────────

@login_required
def salary_structure_view(request, pk):
    """View/edit salary structure for an employee. Admin only."""
    if request.user.role != 'admin':
        raise PermissionDenied
    profile = get_object_or_404(EmployeeProfile.objects.select_related('user'), pk=pk)
    from .models import SalaryStructure
    salary, _ = SalaryStructure.objects.get_or_create(
        employee=profile,
        defaults={'effective_from': profile.joining_date or timezone.now().date()}
    )

    if request.method == 'POST':
        fields = [
            'basic_salary', 'house_allowance', 'transport_allowance',
            'medical_allowance', 'other_allowances', 'tax_deduction',
            'provident_fund', 'other_deductions',
        ]
        for f in fields:
            val = request.POST.get(f, '0').strip() or '0'
            try:
                setattr(salary, f, float(val))
            except ValueError:
                pass
        salary.effective_from = request.POST.get('effective_from') or salary.effective_from
        salary.notes = request.POST.get('notes', '')
        salary.save()
        messages.success(request, f'Salary structure updated for {profile.full_name}.')
        return redirect('employees:salary_structure', pk=pk)

    return render(request, 'employees/salary_structure.html', {
        'profile': profile, 'salary': salary,
    })
