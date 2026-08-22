from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Project, ProjectMember
from apps.accounts.models import User


@login_required
def project_list_view(request):
    user = request.user
    projects = Project.objects.all() if user.role in ('admin','hr') else Project.objects.filter(team_members=user)
    status = request.GET.get('status')
    if status: projects = projects.filter(status=status)
    return render(request, 'projects/project_list.html', {
        'projects': projects, 'filter_status': status, 'status_choices': Project.STATUS_CHOICES,
    })


@login_required
def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    if user.role not in ('admin','hr') and not project.team_members.filter(pk=user.pk).exists():
        raise PermissionDenied
    from apps.tasks.models import Task
    from apps.work_updates.models import DailyWorkUpdate
    tasks   = Task.objects.filter(project=project).prefetch_related('assignees')
    updates = DailyWorkUpdate.objects.filter(project=project).select_related('employee__user').order_by('-date')[:20]
    members = project.memberships.select_related('user__employee_profile')
    return render(request, 'projects/project_detail.html', {
        'project': project, 'tasks': tasks, 'updates': updates, 'members': members,
    })


@login_required
def project_create_view(request):
    if request.user.role not in ('admin','hr'): raise PermissionDenied
    users = User.objects.filter(is_active=True).select_related('employee_profile')
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        sd   = request.POST.get('start_date')
        if not name or not sd:
            messages.error(request, 'Name and start date are required.')
        else:
            proj = Project.objects.create(
                name=name, description=request.POST.get('description','').strip(),
                client=request.POST.get('client','').strip(),
                start_date=sd, end_date=request.POST.get('end_date') or None,
                project_manager_id=request.POST.get('project_manager') or None,
                status=request.POST.get('status','planning'),
            )
            for uid in request.POST.getlist('members'):
                ProjectMember.objects.get_or_create(project=proj, user_id=uid)
            messages.success(request, f'Project "{name}" created.')
            return redirect('projects:project_detail', pk=proj.pk)
    return render(request, 'projects/project_form.html', {
        'users': users, 'action': 'Create', 'status_choices': Project.STATUS_CHOICES,
        'form_data': request.POST if request.method == 'POST' else {},
    })


@login_required
def project_edit_view(request, pk):
    if request.user.role not in ('admin','hr'): raise PermissionDenied
    project = get_object_or_404(Project, pk=pk)
    users   = User.objects.filter(is_active=True).select_related('employee_profile')
    current_ids = list(project.team_members.values_list('id', flat=True))
    if request.method == 'POST':
        project.name        = request.POST.get('name', project.name).strip()
        project.description = request.POST.get('description','').strip()
        project.client      = request.POST.get('client','').strip()
        project.start_date  = request.POST.get('start_date', project.start_date)
        project.end_date    = request.POST.get('end_date') or None
        project.project_manager_id = request.POST.get('project_manager') or None
        project.status      = request.POST.get('status', project.status)
        project.save()
        new_ids = request.POST.getlist('members')
        project.memberships.exclude(user_id__in=new_ids).delete()
        for uid in new_ids:
            ProjectMember.objects.get_or_create(project=project, user_id=uid)
        messages.success(request, 'Project updated.')
        return redirect('projects:project_detail', pk=project.pk)
    return render(request, 'projects/project_form.html', {
        'project': project, 'users': users, 'action': 'Edit',
        'status_choices': Project.STATUS_CHOICES,
        'current_member_ids': [str(i) for i in current_ids], 'form_data': {},
    })


@login_required
def project_delete_view(request, pk):
    if request.user.role != 'admin': raise PermissionDenied
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted.')
        return redirect('projects:project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})
