from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

app_name = 'api_accounts'

urlpatterns = [
    path('register/', api_views.register_view, name='register'),
    path('login/', api_views.login_view, name='login'),
    path('logout/', api_views.logout_view, name='logout'),
    path('me/', api_views.me_view, name='me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', api_views.change_password_view, name='change_password'),
    path('verify-email/<uuid:token>/', api_views.verify_email_view, name='verify_email'),
    path('forgot-password/', api_views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uuid:token>/', api_views.reset_password_view, name='reset_password'),
]
