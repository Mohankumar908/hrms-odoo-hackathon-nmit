from django.urls import path
from . import api_views

app_name = 'api_employees'

urlpatterns = [
    path('', api_views.EmployeeListView.as_view(), name='list'),
    path('create/', api_views.EmployeeCreateView.as_view(), name='create'),
    path('dashboard/', api_views.dashboard_stats, name='dashboard'),
    path('<int:pk>/', api_views.EmployeeDetailView.as_view(), name='detail'),
    path('<int:pk>/deactivate/', api_views.deactivate_employee, name='deactivate'),
    path('<int:employee_id>/salary/', api_views.SalaryStructureView.as_view(), name='salary'),
    path('<int:employee_id>/documents/', api_views.EmployeeDocumentListView.as_view(), name='documents'),
    path('departments/', api_views.DepartmentListCreateView.as_view(), name='departments'),
    path('departments/<int:pk>/', api_views.DepartmentDetailView.as_view(), name='department_detail'),
    path('designations/', api_views.DesignationListCreateView.as_view(), name='designations'),
    path('designations/<int:pk>/', api_views.DesignationDetailView.as_view(), name='designation_detail'),
]
