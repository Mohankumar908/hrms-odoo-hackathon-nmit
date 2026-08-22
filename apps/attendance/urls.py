from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('',          views.attendance_view,      name='attendance'),
    path('checkin/',  views.checkin_view,          name='checkin'),
    path('checkout/', views.checkout_view,         name='checkout'),
    path('admin/',    views.admin_attendance_view, name='admin_attendance'),
]
