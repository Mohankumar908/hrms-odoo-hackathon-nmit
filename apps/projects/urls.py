from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('',                 views.project_list_view,   name='project_list'),
    path('create/',          views.project_create_view, name='project_create'),
    path('<int:pk>/',        views.project_detail_view, name='project_detail'),
    path('<int:pk>/edit/',   views.project_edit_view,   name='project_edit'),
    path('<int:pk>/delete/', views.project_delete_view, name='project_delete'),
]
