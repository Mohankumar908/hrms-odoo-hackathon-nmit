"""
DAYFLOW HRMS - Accounts template views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import services
from .models import User


def _role_redirect(user):
    if user.role == 'admin':
        return '/employees/admin-dashboard/'
    elif user.role == 'hr':
        return '/employees/admin-dashboard/'
    return '/employees/'


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_role_redirect(request.user))
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, email=email, password=password)
        if user:
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated. Please contact the Admin.')
                return render(request, 'accounts/login.html')
            # Also block if employee profile is inactive/terminated
            try:
                if user.employee_profile.employment_status in ('inactive', 'terminated'):
                    messages.error(request, 'Your account is inactive. Please contact the Admin.')
                    return render(request, 'accounts/login.html')
            except Exception:
                pass
            login(request, user)
            next_url = request.GET.get('next', '')
            return redirect(next_url if next_url else _role_redirect(user))
        messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register_view(request):
    """Public registration is disabled. Only admins can create accounts."""
    from django.http import Http404
    raise Http404


def verify_email_view(request, token):
    user = services.verify_email_token(token)
    if user:
        messages.success(request, 'Email verified! You can now log in.')
    else:
        messages.error(request, 'Invalid or expired verification link.')
    return redirect('accounts:login')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        services.send_password_reset_email(email)
        messages.success(request, 'If that email exists, a reset link has been sent.')
        return redirect('accounts:login')
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, token):
    if request.method == 'POST':
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        new_password = request.POST.get('new_password', '')
        confirm = request.POST.get('confirm_password', '')
        if new_password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/reset_password.html', {'token': token})
        try:
            validate_password(new_password)
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return render(request, 'accounts/reset_password.html', {'token': token})
        user, error = services.reset_password(token, new_password)
        if error:
            messages.error(request, error)
            return render(request, 'accounts/reset_password.html', {'token': token})
        messages.success(request, 'Password reset successful. You can now log in.')
        return redirect('accounts:login')
    return render(request, 'accounts/reset_password.html', {'token': token})


@login_required
def dashboard_view(request):
    """Route users to the correct dashboard based on role."""
    return redirect(_role_redirect(request.user))
