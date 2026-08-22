from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from .models import DailyWorkUpdate
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.employees.models import EmployeeProfile


@login_required
def work_update_list(request):
    user = request.user
    if user.role in ('admin', 'hr'):
        updates = DailyWorkUpdate.objects.select_related(
            'employee__user', 'project', 'task'
        ).all()
    else:
        updates = DailyWorkUpdate.objects.select_related(
            'employee__user', 'project', 'task'
        ).filter(employee__user=user)

    # Filters
    project_id = request.GET.get('project')
    date_filter = request.GET.get('date')
    employee_id = request.GET.get('employee_id')

    if project_id:
        updates = updates.filter(project_id=project_id)
    if date_filter:
        updates = updates.filter(date=date_filter)
    if employee_id and user.role in ('admin', 'hr'):
        updates = updates.filter(employee_id=employee_id)

    projects = Project.objects.all() if user.role in ('admin', 'hr') else Project.objects.filter(team_members=user)
    employees = EmployeeProfile.objects.select_related('user').all() if user.role in ('admin', 'hr') else None

    return render(request, 'work_updates/work_update_list.html', {
        'updates': updates,
        'projects': projects,
        'employees': employees,
        'filter_project': project_id,
        'filter_date': date_filter,
        'filter_employee': employee_id,
        'today': timezone.localdate(),
    })


@login_required
def work_update_create(request):
    user = request.user
    try:
        employee = user.employee_profile
    except EmployeeProfile.DoesNotExist:
        messages.error(request, 'No employee profile found for your account.')
        return redirect('work_updates:list')

    # Projects available to this user
    if user.role in ('admin', 'hr'):
        projects = Project.objects.filter(status__in=['planning', 'active'])
    else:
        projects = Project.objects.filter(team_members=user, status__in=['planning', 'active'])

    selected_project = None
    tasks = Task.objects.none()

    if request.method == 'POST':
        project_id = request.POST.get('project')
        task_id = request.POST.get('task') or None
        date = request.POST.get('date')
        work_completed = request.POST.get('work_completed', '').strip()
        work_in_progress = request.POST.get('work_in_progress', '').strip()
        pending_work = request.POST.get('pending_work', '').strip()
        blockers = request.POST.get('blockers', '').strip()
        hours_worked = request.POST.get('hours_worked', 0) or 0
        progress_percentage = request.POST.get('progress_percentage', 0) or 0
        remarks = request.POST.get('remarks', '').strip()

        errors = []
        if not project_id:
            errors.append('Project is required.')
        if not date:
            errors.append('Date is required.')
        if not work_completed:
            errors.append('Work completed is required.')

        # Check unique_together constraint
        if project_id and date and task_id:
            exists = DailyWorkUpdate.objects.filter(
                employee=employee, date=date, task_id=task_id
            ).exists()
            if exists:
                errors.append('A work update for this employee, date, and task already exists.')
        elif project_id and date and not task_id:
            exists = DailyWorkUpdate.objects.filter(
                employee=employee, date=date, task__isnull=True, project_id=project_id
            ).exists()
            if exists:
                errors.append('A work update for this project and date already exists (no task).')

        if errors:
            for e in errors:
                messages.error(request, e)
            selected_project = projects.filter(pk=project_id).first() if project_id else None
            if selected_project:
                tasks = Task.objects.filter(project=selected_project)
            return render(request, 'work_updates/work_update_form.html', {
                'projects': projects,
                'tasks': tasks,
                'selected_project_id': project_id,
                'form_data': request.POST,
                'today': timezone.localdate(),
            })

        update = DailyWorkUpdate.objects.create(
            employee=employee,
            project_id=project_id,
            task_id=task_id if task_id else None,
            date=date,
            work_completed=work_completed,
            work_in_progress=work_in_progress,
            pending_work=pending_work,
            blockers=blockers,
            hours_worked=hours_worked,
            progress_percentage=progress_percentage,
            remarks=remarks,
        )
        messages.success(request, 'Work update submitted successfully.')
        return redirect('work_updates:detail', pk=update.pk)

    return render(request, 'work_updates/work_update_form.html', {
        'projects': projects,
        'tasks': tasks,
        'form_data': {},
        'today': timezone.localdate(),
    })


@login_required
def work_update_detail(request, pk):
    update = get_object_or_404(
        DailyWorkUpdate.objects.select_related('employee__user', 'project', 'task'), pk=pk
    )
    user = request.user
    if user.role not in ('admin', 'hr') and update.employee.user != user:
        raise PermissionDenied
    return render(request, 'work_updates/work_update_detail.html', {'update': update})


@login_required
def work_update_edit(request, pk):
    update = get_object_or_404(DailyWorkUpdate, pk=pk)
    user = request.user

    if user.role not in ('admin', 'hr') and update.employee.user != user:
        raise PermissionDenied

    if user.role in ('admin', 'hr'):
        projects = Project.objects.filter(status__in=['planning', 'active'])
    else:
        projects = Project.objects.filter(team_members=user, status__in=['planning', 'active'])

    tasks = Task.objects.filter(project=update.project)

    if request.method == 'POST':
        project_id = request.POST.get('project')
        task_id = request.POST.get('task') or None

        update.project_id = project_id
        update.task_id = task_id if task_id else None
        update.date = request.POST.get('date')
        update.work_completed = request.POST.get('work_completed', '').strip()
        update.work_in_progress = request.POST.get('work_in_progress', '').strip()
        update.pending_work = request.POST.get('pending_work', '').strip()
        update.blockers = request.POST.get('blockers', '').strip()
        update.hours_worked = request.POST.get('hours_worked', 0) or 0
        update.progress_percentage = request.POST.get('progress_percentage', 0) or 0
        update.remarks = request.POST.get('remarks', '').strip()

        if not update.work_completed:
            messages.error(request, 'Work completed is required.')
            return render(request, 'work_updates/work_update_form.html', {
                'projects': projects,
                'tasks': tasks,
                'update': update,
                'form_data': request.POST,
                'today': timezone.localdate(),
            })

        update.save()
        messages.success(request, 'Work update saved.')
        return redirect('work_updates:detail', pk=update.pk)

    return render(request, 'work_updates/work_update_form.html', {
        'projects': projects,
        'tasks': tasks,
        'update': update,
        'form_data': {},
        'today': timezone.localdate(),
    })


@login_required
def work_update_delete(request, pk):
    update = get_object_or_404(DailyWorkUpdate, pk=pk)
    user = request.user

    if user.role not in ('admin', 'hr') and update.employee.user != user:
        raise PermissionDenied

    if request.method == 'POST':
        update.delete()
        messages.success(request, 'Work update deleted.')
        return redirect('work_updates:list')

    return render(request, 'work_updates/work_update_confirm_delete.html', {'update': update})


@login_required
def get_tasks_for_project(request):
    """AJAX: return tasks for a given project as JSON."""
    from django.http import JsonResponse
    project_id = request.GET.get('project_id')
    if not project_id:
        return JsonResponse({'tasks': []})
    tasks = Task.objects.filter(project_id=project_id).values('id', 'title')
    return JsonResponse({'tasks': list(tasks)})
