from django.urls import path
from . import api_views

app_name = 'api_projects'

urlpatterns = [
    path('', api_views.ProjectListCreateView.as_view(), name='list'),
    path('<int:pk>/', api_views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/members/', api_views.add_project_member, name='add_member'),
    path('<int:pk>/progress-report/', api_views.project_progress_report, name='progress_report'),
]
