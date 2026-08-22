from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from core.permissions import IsAdminOrHR, IsOwnerOrAdminOrHR
from .models import Department, Designation, EmployeeProfile, SalaryStructure, EmployeeDocument
from .serializers import (
    DepartmentSerializer, DesignationSerializer, EmployeeProfileSerializer,
    EmployeeProfileUpdateSerializer, EmployeeListSerializer,
    SalaryStructureSerializer, EmployeeDocumentSerializer
)


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    def get_permissions(self):
        return [IsAdminOrHR()] if self.request.method == 'POST' else [IsAuthenticated()]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrHR]


class DesignationListCreateView(generics.ListCreateAPIView):
    queryset = Designation.objects.select_related('department').all()
    serializer_class = DesignationSerializer
    def get_permissions(self):
        return [IsAdminOrHR()] if self.request.method == 'POST' else [IsAuthenticated()]


class DesignationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAdminOrHR]


class EmployeeListView(generics.ListAPIView):
    serializer_class = EmployeeListSerializer
    permission_classes = [IsAdminOrHR]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'employment_status', 'designation']
    search_fields = ['full_name', 'user__email', 'user__employee_id']
    ordering_fields = ['full_name', 'joining_date', 'created_at']
    def get_queryset(self):
        return EmployeeProfile.objects.select_related('user', 'department', 'designation').all()


class EmployeeCreateView(generics.CreateAPIView):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAdminOrHR]


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    queryset = EmployeeProfile.objects.select_related('user', 'department', 'designation').all()
    permission_classes = [IsOwnerOrAdminOrHR]
    def get_serializer_class(self):
        return EmployeeProfileSerializer if self.request.user.role in ('admin', 'hr') else EmployeeProfileUpdateSerializer


class SalaryStructureView(generics.RetrieveUpdateAPIView):
    serializer_class = SalaryStructureSerializer
    def get_permissions(self):
        return [IsAdminOrHR()] if self.request.method in ('PUT', 'PATCH') else [IsAuthenticated()]
    def get_object(self):
        employee_id = self.kwargs.get('employee_id')
        user = self.request.user
        profile = EmployeeProfile.objects.get(pk=employee_id) if user.role in ('admin', 'hr') else user.employee_profile
        return SalaryStructure.objects.get(employee=profile)


class EmployeeDocumentListView(generics.ListCreateAPIView):
    serializer_class = EmployeeDocumentSerializer
    def get_permissions(self):
        return [IsAdminOrHR()] if self.request.method == 'POST' else [IsAuthenticated()]
    def get_queryset(self):
        user = self.request.user
        if user.role not in ('admin', 'hr'):
            return EmployeeDocument.objects.filter(employee__user=user)
        return EmployeeDocument.objects.filter(employee_id=self.kwargs['employee_id'])
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


@api_view(['POST'])
@permission_classes([IsAdminOrHR])
def deactivate_employee(request, pk):
    try:
        profile = EmployeeProfile.objects.get(pk=pk)
        profile.employment_status = 'inactive'
        profile.user.is_active = False
        profile.save()
        profile.user.save()
        return Response({'message': 'Employee deactivated.'})
    except EmployeeProfile.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    from apps.attendance.models import Attendance
    from apps.leave_management.models import LeaveRequest
    from apps.tasks.models import Task
    from apps.projects.models import Project
    from django.utils import timezone
    today = timezone.localdate()
    user = request.user
    if user.role in ('admin', 'hr'):
        return Response({
            'total_employees': EmployeeProfile.objects.filter(employment_status='active').count(),
            'today_present': Attendance.objects.filter(date=today, status='present').count(),
            'today_absent': Attendance.objects.filter(date=today, status='absent').count(),
            'on_leave': Attendance.objects.filter(date=today, status='leave').count(),
            'pending_leaves': LeaveRequest.objects.filter(status='pending').count(),
            'active_projects': Project.objects.filter(status='active').count(),
            'active_tasks': Task.objects.filter(status='in_progress').count(),
            'delayed_tasks': Task.objects.filter(status='delayed').count(),
        })
    # Employee view
    try:
        profile = user.employee_profile
        today_att = Attendance.objects.filter(employee=profile, date=today).first()
        return Response({
            'today_attendance': {'status': today_att.status if today_att else 'absent',
                                 'check_in': str(today_att.check_in) if today_att and today_att.check_in else None,
                                 'check_out': str(today_att.check_out) if today_att and today_att.check_out else None},
            'pending_leaves': LeaveRequest.objects.filter(employee=profile, status='pending').count(),
            'active_tasks': Task.objects.filter(assignees=user, status__in=['not_started', 'in_progress']).count(),
        })
    except Exception:
        return Response({'error': 'Profile not found'}, status=404)
