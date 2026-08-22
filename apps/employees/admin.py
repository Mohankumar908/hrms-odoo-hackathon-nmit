from django.contrib import admin
from .models import Department, Designation, EmployeeProfile, SalaryStructure, EmployeeDocument


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head', 'created_at']
    search_fields = ['name']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['title', 'department']
    list_filter = ['department']


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'department', 'designation', 'employment_status', 'joining_date']
    list_filter = ['department', 'employment_status', 'gender']
    search_fields = ['full_name', 'user__email', 'user__employee_id']
    raw_id_fields = ['user', 'manager']


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['employee', 'basic_salary', 'net_salary', 'effective_from']
    search_fields = ['employee__full_name']


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'document_type', 'title', 'created_at']
    list_filter = ['document_type']
