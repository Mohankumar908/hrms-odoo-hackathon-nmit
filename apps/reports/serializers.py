from rest_framework import serializers
from .models import SavedReport

class SavedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedReport
        fields = '__all__'
        read_only_fields = ['created_by']
