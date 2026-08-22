from django.urls import path
from . import api_views

app_name = 'api_payroll'

urlpatterns = [
    path('',                    api_views.PayrollListView.as_view(),        name='list'),
    path('<int:pk>/',           api_views.PayrollDetailView.as_view(),      name='detail'),
    path('<int:pk>/mark-paid/', api_views.mark_payroll_paid_view,           name='mark_paid'),
    path('generate/',           api_views.generate_payroll_view,            name='generate'),
    path('generate-bulk/',      api_views.generate_payroll_bulk_view,       name='generate_bulk'),
    path('mine/',               api_views.my_payroll_view,                  name='mine'),
]
