from django.contrib import admin
from .models import SavedReport

@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'created_by', 'created_at']
