from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsAdminOrHR
from .models import Notification
from .serializers import NotificationSerializer
from . import services


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user)
        unread_only = self.request.query_params.get('unread')
        if unread_only == '1':
            qs = qs.filter(is_read=False)
        return qs


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_read(request, pk):
    Notification.objects.filter(pk=pk, recipient=request.user).update(is_read=True)
    return Response({'message': 'Marked as read.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    services.mark_all_read(request.user)
    return Response({'message': 'All marked as read.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, pk):
    deleted, _ = Notification.objects.filter(pk=pk, recipient=request.user).delete()
    if deleted:
        return Response({'message': 'Notification deleted.'})
    return Response({'error': 'Not found.'}, status=404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_all_notifications(request):
    count, _ = Notification.objects.filter(recipient=request.user).delete()
    return Response({'message': f'{count} notifications cleared.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'unread_count': count})


@api_view(['POST'])
@permission_classes([IsAdminOrHR])
def broadcast_announcement(request):
    """
    Send an announcement to all users or a specific department.
    Body: { "title": "...", "message": "...", "target": "all" | "department:<dept_id>" }
    """
    title   = request.data.get('title', '').strip()
    message = request.data.get('message', '').strip()
    target  = request.data.get('target', 'all')

    if not title or not message:
        return Response({'error': 'title and message are required.'}, status=400)

    from apps.accounts.models import User
    from apps.employees.models import Department

    if target == 'all':
        users = User.objects.filter(is_active=True)
    elif target.startswith('department:'):
        dept_id = target.split(':')[1]
        users = User.objects.filter(
            is_active=True,
            employee_profile__department_id=dept_id
        )
    else:
        return Response({'error': 'Invalid target. Use "all" or "department:<id>".'}, status=400)

    services.broadcast_announcement(users, title, message)
    return Response({'message': f'Announcement sent to {users.count()} users.'})
