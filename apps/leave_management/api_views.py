from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsAdminOrHR
from .models import LeaveType, LeaveBalance, LeaveRequest
from .serializers import LeaveTypeSerializer, LeaveBalanceSerializer, LeaveRequestSerializer, LeaveApprovalSerializer
from . import services


class LeaveTypeListCreateView(generics.ListCreateAPIView):
    queryset = LeaveType.objects.filter(is_active=True)
    serializer_class = LeaveTypeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrHR()]
        return [IsAuthenticated()]


class LeaveRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = LeaveRequest.objects.select_related('employee__user', 'leave_type').all()
        if user.role not in ('admin', 'hr'):
            qs = qs.filter(employee__user=user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        leave = serializer.save(employee=self.request.user.employee_profile)
        # Notify all HR/Admin users about new leave submission
        from apps.notifications.services import create_notification
        from apps.accounts.models import User
        for hr_user in User.objects.filter(role__in=('admin', 'hr'), is_active=True):
            create_notification(
                recipient=hr_user,
                notification_type='leave_submitted',
                title=f'New Leave Request: {leave.employee.full_name}',
                message=f'{leave.employee.full_name} has applied for {leave.leave_type.name} from {leave.start_date} to {leave.end_date} ({leave.total_days} days).',
                related_object_id=leave.id,
                action_url='/leave/',
            )


class LeaveRequestDetailView(generics.RetrieveAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]


@api_view(['PUT'])
@permission_classes([IsAdminOrHR])
def approve_leave_view(request, pk):
    try:
        leave = LeaveRequest.objects.get(pk=pk, status='pending')
    except LeaveRequest.DoesNotExist:
        return Response({'error': 'Leave request not found or already processed.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = LeaveApprovalSerializer(data=request.data)
    if serializer.is_valid():
        services.approve_leave(leave, request.user, serializer.validated_data.get('comment', ''))
        return Response({'message': 'Leave approved.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAdminOrHR])
def reject_leave_view(request, pk):
    try:
        leave = LeaveRequest.objects.get(pk=pk, status='pending')
    except LeaveRequest.DoesNotExist:
        return Response({'error': 'Leave request not found or already processed.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = LeaveApprovalSerializer(data=request.data)
    if serializer.is_valid():
        services.reject_leave(leave, request.user, serializer.validated_data.get('comment', ''))
        return Response({'message': 'Leave rejected.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveBalanceListView(generics.ListAPIView):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'hr'):
            employee_id = self.request.query_params.get('employee_id')
            if employee_id:
                return LeaveBalance.objects.filter(employee_id=employee_id)
            return LeaveBalance.objects.all()
        return LeaveBalance.objects.filter(employee__user=user)


# ── Leave Type Detail (update/deactivate) ─────────────────────────────────────
class LeaveTypeDetailView(generics.RetrieveUpdateAPIView):
    """Allow admin/HR to view and update leave types. DELETE soft-deletes (sets is_active=False)."""
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH'):
            return [IsAdminOrHR()]
        return [IsAuthenticated()]

    def delete(self, request, pk):
        try:
            lt = LeaveType.objects.get(pk=pk)
            lt.is_active = False
            lt.save(update_fields=['is_active'])
            return Response({'message': f'Leave type "{lt.name}" deactivated.'})
        except LeaveType.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)


# ── Employee cancels own pending leave ────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_leave_view(request, pk):
    try:
        leave = LeaveRequest.objects.get(pk=pk, status='pending')
    except LeaveRequest.DoesNotExist:
        return Response({'error': 'Leave request not found or cannot be cancelled.'}, status=404)

    user = request.user
    if user.role not in ('admin', 'hr') and leave.employee.user != user:
        return Response({'error': 'Permission denied.'}, status=403)

    leave.status = 'cancelled'
    leave.save(update_fields=['status'])
    return Response({'message': 'Leave request cancelled.'})


# ── Notification unread count ─────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_unread_count(request):
    from apps.notifications.models import Notification
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return Response({'unread_count': count})
