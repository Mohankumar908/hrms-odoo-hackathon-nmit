from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsAdminOrHR
from .models import Task, TaskComment
from .serializers import TaskSerializer, TaskListSerializer, TaskUpdateSerializer, TaskCommentSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TaskListSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'hr'):
            qs = Task.objects.all()
        else:
            qs = Task.objects.filter(assignees=user)
        project_id = self.request.query_params.get('project')
        status_filter = self.request.query_params.get('status')
        if project_id:
            qs = qs.filter(project_id=project_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.prefetch_related('assignees').select_related('project')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrHR()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.prefetch_related('assignees', 'comments__author').select_related('project')

    def get_serializer_class(self):
        user = self.request.user
        if user.role in ('admin', 'hr'):
            return TaskSerializer
        return TaskUpdateSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        instance = serializer.save()
        # Notify about completion
        if instance.status == 'completed':
            from apps.notifications.services import create_notification
            if instance.project.project_manager:
                create_notification(
                    recipient=instance.project.project_manager,
                    notification_type='task_completed',
                    title='Task Completed',
                    message=f'Task "{instance.title}" has been marked as completed.',
                    related_object_id=instance.id,
                )


class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskComment.objects.filter(task_id=self.kwargs['task_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, task_id=self.kwargs['task_id'])


@api_view(['POST'])
@permission_classes([IsAdminOrHR])
def assign_task(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

    user_ids = request.data.get('user_ids', [])
    task.assignees.set(user_ids)
    task.save()

    # Notify each assigned user
    from apps.notifications.services import create_notification
    from apps.accounts.models import User
    for uid in user_ids:
        try:
            u = User.objects.get(pk=uid)
            create_notification(
                recipient=u,
                notification_type='task_assigned',
                title='New Task Assigned',
                message=f'You have been assigned to task: "{task.title}" in project "{task.project.name}".',
                related_object_id=task.id,
            )
        except User.DoesNotExist:
            pass

    return Response({'message': 'Assignees updated.', 'task': TaskSerializer(task).data})
