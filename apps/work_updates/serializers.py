from rest_framework import serializers
from .models import DailyWorkUpdate


class DailyWorkUpdateSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True, default=None)

    class Meta:
        model = DailyWorkUpdate
        fields = '__all__'
        read_only_fields = ['employee']

    def create(self, validated_data):
        validated_data['employee'] = self.context['request'].user.employee_profile
        return super().create(validated_data)
