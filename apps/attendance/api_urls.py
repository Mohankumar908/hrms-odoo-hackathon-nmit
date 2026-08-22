from django.urls import path
from . import api_views

app_name = 'api_attendance'

urlpatterns = [
    path('check-in/', api_views.check_in_view, name='check_in'),
    path('check-out/', api_views.check_out_view, name='check_out'),
    path('', api_views.AttendanceListView.as_view(), name='list'),
    path('today/', api_views.today_attendance, name='today'),
    path('corrections/', api_views.CorrectionRequestListCreateView.as_view(), name='corrections'),
    path('corrections/<int:pk>/review/', api_views.review_correction, name='review_correction'),
]
