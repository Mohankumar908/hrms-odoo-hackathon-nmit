from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Task, TaskComment
from apps.projects.models import Project
from apps.accounts.models import User


@login_required
def task_list_view(request):
    user = request.user
    tasks = Task.objects.select_related('project').prefetch_related('assignees').all() \
        if user.role in ('admin','hr') else \
        Task.objects.filter(assignees=user).select_related('project')
    if request.GET.get('status'):   tasks = tasks.filter(status=request.GET['status'])
    if request.GET.get('priority'): tasks = tasks.filter(priority=request.GET['priority'])
    if request.GET.get('project'):  tasks = tasks.filter(project_id=request.GET['project'])
    projects = Project.objects.all() if user.role in ('admin','hr') else Project.objects.filter(team_members=user)
    return render(request, 'tasks/task_list.html', {
        'tasks': tasks, 'projects': projects,
        'status_choices': Task.STATUS_CHOICES, 'priority_choices': Task.PRIORITY_CHOICES,
        'filter_status': request.GET.get('status'), 'filter_priority': request.GET.get('priority'),
        'filter_project': request.GET.get('project'),
    })


@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(Task.objects.select_related('project','created_by').prefetch_related('assignees','comments__author'), pk=pk)
    user = request.user
    if user.role not in ('admin','hr') and not task.assignees.filter(pk=user.pk).exists():
        raise PermissionDenied
    if request.method == 'POST':
        content = request.POST.get('content','').strip()
        if content:
            TaskComment.objects.create(task=task, author=user, content=content,
                                       is_blocker=request.POST.get('is_blocker')=='on')
            messages.success(request, 'Comment added.')
        return redirect('tasks:task_detail', pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def task_create_view(request):
    if request.user.role not in ('admin','hr'): raise PermissionDenied
    projects = Project.objects.filter(status__in=['planning','active'])
    users    = User.objects.filter(is_active=True).select_related('employee_profile')
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        pid   = request.POST.get('project')
        if not title or not pid:
            messages.error(request, 'Title and project required.')
        else:
            t = Task.objects.create(
                title=title, project_id=pid,
                description=request.POST.get('description','').strip(),
                priority=request.POST.get('priority','medium'),
                status=request.POST.get('status','not_started'),
                deadline=request.POST.get('deadline') or None,
                estimated_hours=request.POST.get('estimated_hours') or None,
                created_by=request.user,
            )
            ids = request.POST.getlist('assignees')
            if ids: t.assignees.set(ids)
            messages.success(request, f'Task "{title}" created.')
            return redirect('tasks:task_detail', pk=t.pk)
    return render(request, 'tasks/task_form.html', {
        'projects': projects, 'users': users, 'action': 'Create',
        'status_choices': Task.STATUS_CHOICES, 'priority_choices': Task.PRIORITY_CHOICES,
        'form_data': request.POST if request.method == 'POST' else {},
    })


@login_required
def task_edit_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    user = request.user
    if user.role not in ('admin','hr') and not task.assignees.filter(pk=user.pk).exists():
        raise PermissionDenied
    projects = Project.objects.filter(status__in=['planning','active'])
    users    = User.objects.filter(is_active=True).select_related('employee_profile')
    current_ids = list(task.assignees.values_list('id', flat=True))
    if request.method == 'POST':
        if user.role in ('admin','hr'):
            task.title       = request.POST.get('title', task.title).strip()
            task.project_id  = request.POST.get('project', task.project_id)
            task.description = request.POST.get('description','').strip()
            task.priority    = request.POST.get('priority', task.priority)
            task.deadline    = request.POST.get('deadline') or None
            task.estimated_hours = request.POST.get('estimated_hours') or None
            ids = request.POST.getlist('assignees')
            if ids: task.assignees.set(ids)
        task.status   = request.POST.get('status', task.status)
        task.progress = int(request.POST.get('progress', task.progress) or 0)
        task.actual_hours = request.POST.get('actual_hours') or task.actual_hours
        task.save()
        messages.success(request, 'Task updated.')
        return redirect('tasks:task_detail', pk=pk)
    return render(request, 'tasks/task_form.html', {
        'task': task, 'projects': projects, 'users': users, 'action': 'Edit',
        'status_choices': Task.STATUS_CHOICES, 'priority_choices': Task.PRIORITY_CHOICES,
        'current_assignee_ids': [str(i) for i in current_ids], 'form_data': {},
    })


@login_required
def task_delete_view(request, pk):
    if request.user.role not in ('admin','hr'): raise PermissionDenied
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        pid = task.project_id
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('projects:project_detail', pk=pid)
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})
