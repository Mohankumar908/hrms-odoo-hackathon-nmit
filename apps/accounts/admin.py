from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['employee_id', 'email', 'role', 'is_active', 'is_email_verified', 'created_at']
    list_filter = ['role', 'is_active', 'is_email_verified']
    search_fields = ['employee_id', 'email']
    ordering = ['employee_id']
    fieldsets = (
        (None, {'fields': ('employee_id', 'email', 'password')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_email_verified')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('employee_id', 'email', 'role', 'password1', 'password2'),
        }),
    )
