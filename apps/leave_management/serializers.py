from rest_framework import serializers
from .models import LeaveType, LeaveBalance, LeaveRequest


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    remaining_days = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True)

    class Meta:
        model = LeaveBalance
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewed_by.full_name', read_only=True, default=None)

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['employee', 'status', 'reviewed_by', 'reviewer_comment', 'reviewed_at', 'total_days']

    def validate(self, attrs):
        from . import services
        errors = services.validate_leave_request(
            attrs.get('employee') or self.context['request'].user.employee_profile,
            attrs['leave_type'],
            attrs['start_date'],
            attrs['end_date'],
        )
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class LeaveApprovalSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True)
