from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('',                 views.task_list_view,   name='task_list'),
    path('create/',          views.task_create_view, name='task_create'),
    path('<int:pk>/',        views.task_detail_view, name='task_detail'),
    path('<int:pk>/edit/',   views.task_edit_view,   name='task_edit'),
    path('<int:pk>/delete/', views.task_delete_view, name='task_delete'),
]
