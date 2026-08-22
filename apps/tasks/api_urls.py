from django.urls import path
from . import api_views

app_name = 'api_tasks'

urlpatterns = [
    path('', api_views.TaskListCreateView.as_view(), name='list'),
    path('<int:pk>/', api_views.TaskDetailView.as_view(), name='detail'),
    path('<int:pk>/assign/', api_views.assign_task, name='assign'),
    path('<int:task_id>/comments/', api_views.TaskCommentListCreateView.as_view(), name='comments'),
]
