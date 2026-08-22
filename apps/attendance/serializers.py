from rest_framework import serializers
from .models import Attendance, AttendanceCorrectionRequest


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.user.employee_id', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['employee', 'working_hours', 'is_late', 'is_early_checkout']


class CorrectionRequestSerializer(serializers.ModelSerializer):
    attendance_date = serializers.DateField(source='attendance.date', read_only=True)
    employee_name = serializers.CharField(source='requested_by.full_name', read_only=True)

    class Meta:
        model = AttendanceCorrectionRequest
        fields = '__all__'
        read_only_fields = ['requested_by', 'reviewed_by', 'status', 'reviewer_comment', 'reviewed_at']
