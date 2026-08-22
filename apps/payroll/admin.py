from django.contrib import admin
from .models import Payroll


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'basic_salary', 'net_salary', 'status']
    list_filter = ['status', 'month', 'year']
    search_fields = ['employee__full_name']
    readonly_fields = ['processed_by', 'processed_at', 'gross_salary', 'net_salary', 'total_deductions']
