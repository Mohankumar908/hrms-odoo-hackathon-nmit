from django.urls import path
from . import api_views
app_name = 'api_work_updates'
urlpatterns = [
    path('', api_views.DailyWorkUpdateListCreateView.as_view(), name='list'),
    path('<int:pk>/', api_views.DailyWorkUpdateDetailView.as_view(), name='detail'),
]
