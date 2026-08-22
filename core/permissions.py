"""
DAYFLOW HRMS - Reusable DRF permission classes.
"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access only to Admin role users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsHR(BasePermission):
    """Allow access only to HR role users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'hr'


class IsAdminOrHR(BasePermission):
    """Allow access to Admin or HR role users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('admin', 'hr')


class IsEmployee(BasePermission):
    """Allow access to Employee role users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employee'


class IsOwnerOrAdminOrHR(BasePermission):
    """Object-level: owner can access own data; admin/hr can access any."""
    def has_object_permission(self, request, view, obj):
        if request.user.role in ('admin', 'hr'):
            return True
        # obj may have a 'user' or 'employee' FK
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'employee'):
            return obj.employee.user == request.user
        return False
