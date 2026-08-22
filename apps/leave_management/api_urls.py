from django.urls import path
from . import api_views

app_name = 'api_leave'

urlpatterns = [
    path('',                              api_views.LeaveRequestListCreateView.as_view(),  name='list'),
    path('<int:pk>/',                     api_views.LeaveRequestDetailView.as_view(),       name='detail'),
    path('<int:pk>/approve/',             api_views.approve_leave_view,                     name='approve'),
    path('<int:pk>/reject/',              api_views.reject_leave_view,                      name='reject'),
    path('<int:pk>/cancel/',              api_views.cancel_leave_view,                      name='cancel'),
    path('types/',                        api_views.LeaveTypeListCreateView.as_view(),      name='types'),
    path('types/<int:pk>/',              api_views.LeaveTypeDetailView.as_view(),           name='type_detail'),
    path('balances/',                     api_views.LeaveBalanceListView.as_view(),         name='balances'),
]
