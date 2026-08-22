from django.urls import path
from . import views

app_name = 'work_updates'

urlpatterns = [
    path('', views.work_update_list, name='list'),
    path('create/', views.work_update_create, name='create'),
    path('<int:pk>/', views.work_update_detail, name='detail'),
    path('<int:pk>/edit/', views.work_update_edit, name='edit'),
    path('<int:pk>/delete/', views.work_update_delete, name='delete'),
    path('ajax/tasks/', views.get_tasks_for_project, name='ajax_tasks'),
]
