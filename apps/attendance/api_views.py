from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from core.permissions import IsAdminOrHR, IsOwnerOrAdminOrHR
from core.utils import get_client_ip
from .models import Attendance, AttendanceCorrectionRequest
from .serializers import AttendanceSerializer, CorrectionRequestSerializer
from . import services


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_in_view(request):
    attendance, created, error = services.check_in(request.user, get_client_ip(request))
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_out_view(request):
    attendance, error = services.check_out(request.user)
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    return Response(AttendanceSerializer(attendance).data)


class AttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.select_related('employee__user').all()
        if user.role not in ('admin', 'hr'):
            qs = qs.filter(employee__user=user)
        # Filters
        date = self.request.query_params.get('date')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        employee_id = self.request.query_params.get('employee_id')
        if date:
            qs = qs.filter(date=date)
        if month and year:
            qs = qs.filter(date__month=month, date__year=year)
        if employee_id and user.role in ('admin', 'hr'):
            qs = qs.filter(employee__user__employee_id=employee_id)
        return qs


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_attendance(request):
    today = timezone.localdate()
    try:
        profile = request.user.employee_profile
        attendance = Attendance.objects.get(employee=profile, date=today)
        return Response(AttendanceSerializer(attendance).data)
    except Exception:
        return Response({'status': 'absent', 'date': str(today)})


class CorrectionRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = CorrectionRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ('admin', 'hr'):
            return AttendanceCorrectionRequest.objects.filter(status='pending')
        return AttendanceCorrectionRequest.objects.filter(requested_by=user)

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAdminOrHR])
def review_correction(request, pk):
    try:
        correction = AttendanceCorrectionRequest.objects.get(pk=pk)
    except AttendanceCorrectionRequest.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    action = request.data.get('action')
    comment = request.data.get('comment', '')

    if action not in ('approve', 'reject'):
        return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    correction.reviewed_by = request.user
    correction.reviewer_comment = comment
    correction.reviewed_at = timezone.now()

    if action == 'approve':
        correction.status = 'approved'
        att = correction.attendance
        if correction.requested_check_in:
            att.check_in = correction.requested_check_in
        if correction.requested_check_out:
            att.check_out = correction.requested_check_out
        if correction.requested_status:
            att.status = correction.requested_status
        att.calculate_working_hours()
        att.save()
    else:
        correction.status = 'rejected'

    correction.save()
    return Response({'message': f'Correction {action}d.'})
