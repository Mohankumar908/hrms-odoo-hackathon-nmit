from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/verify-email/<uuid:token>/', views.verify_email_view, name='verify_email'),
    path('accounts/forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('accounts/reset-password/<uuid:token>/', views.reset_password_view, name='reset_password'),
]
