"""
DAYFLOW HRMS - View mixins for role-based access control on template views.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class HRRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ('admin', 'hr'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class EmployeeRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
