from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminOrHR
from .models import DailyWorkUpdate
from .serializers import DailyWorkUpdateSerializer


class DailyWorkUpdateListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyWorkUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = DailyWorkUpdate.objects.select_related('employee__user', 'project', 'task').all()
        if user.role not in ('admin', 'hr'):
            qs = qs.filter(employee__user=user)
        # Filters
        employee_id = self.request.query_params.get('employee_id')
        project_id = self.request.query_params.get('project')
        date = self.request.query_params.get('date')
        if employee_id and user.role in ('admin', 'hr'):
            qs = qs.filter(employee__user__employee_id=employee_id)
        if project_id:
            qs = qs.filter(project_id=project_id)
        if date:
            qs = qs.filter(date=date)
        return qs


class DailyWorkUpdateDetailView(generics.RetrieveUpdateAPIView):
    queryset = DailyWorkUpdate.objects.all()
    serializer_class = DailyWorkUpdateSerializer
    permission_classes = [IsAuthenticated]
