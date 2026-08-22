from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsAdminOrHR
from .models import Project, ProjectMember
from .serializers import ProjectSerializer, ProjectListSerializer, ProjectMemberSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'hr'):
            return Project.objects.all()
        return Project.objects.filter(team_members=user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrHR()]
        return [IsAuthenticated()]


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.prefetch_related('memberships__user').all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdminOrHR()]
        return [IsAuthenticated()]


@api_view(['POST'])
@permission_classes([IsAdminOrHR])
def add_project_member(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProjectMemberSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(project=project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_progress_report(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    from apps.tasks.models import Task
    from apps.work_updates.models import DailyWorkUpdate

    tasks = Task.objects.filter(project=project)
    recent_updates = DailyWorkUpdate.objects.filter(project=project).order_by('-date')[:10]

    delayed_tasks = tasks.filter(status='delayed')
    blockers = []
    for update in recent_updates:
        if update.blockers:
            blockers.append({'date': update.date, 'blocker': update.blockers, 'employee': update.employee.full_name})

    return Response({
        'project': ProjectSerializer(project).data,
        'task_summary': {
            'total': tasks.count(),
            'completed': tasks.filter(status='completed').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'delayed': delayed_tasks.count(),
            'not_started': tasks.filter(status='not_started').count(),
        },
        'delayed_tasks': [{'title': t.title, 'deadline': t.deadline, 'assignees': [a.full_name for a in t.assignees.all()]} for t in delayed_tasks],
        'blockers': blockers,
        'recent_updates_count': recent_updates.count(),
    })
