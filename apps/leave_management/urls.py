from django.urls import path
from . import views

app_name = 'leave_management'

urlpatterns = [
    path('',              views.leave_list_view,        name='leave_list'),
    path('apply/',        views.apply_leave_view,        name='apply_leave'),
    path('types/',        views.leave_type_list_view,    name='leave_types'),
    path('<int:pk>/approve/', views.approve_leave_view,  name='approve_leave'),
    path('<int:pk>/reject/',  views.reject_leave_view,   name='reject_leave'),
]
