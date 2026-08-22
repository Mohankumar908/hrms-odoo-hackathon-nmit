from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('',                          views.employee_dashboard,      name='employee_dashboard'),
    path('admin-dashboard/',          views.admin_dashboard,         name='admin_dashboard'),
    path('hr-dashboard/',             views.hr_dashboard,            name='hr_dashboard'),
    path('profile/',                  views.employee_profile_view,   name='profile'),
    path('profile/<int:pk>/',         views.employee_profile_view,   name='profile_detail'),
    path('list/',                     views.employee_list_view,      name='employee_list'),
    path('create/',                   views.employee_create_view,    name='employee_create'),
    path('create/hr/',                lambda req: views.employee_create_view(req, role='hr'), name='hr_create'),
    path('<int:pk>/edit/',            views.employee_edit_view,      name='employee_edit'),
    path('<int:pk>/delete/',          views.employee_delete_view,    name='employee_delete'),
    path('<int:pk>/toggle-active/',   views.toggle_active_view,      name='toggle_active'),
    path('<int:pk>/salary/',          views.salary_structure_view,   name='salary_structure'),
    path('hr/list/',                  views.hr_list_view,            name='hr_list'),
]
