from rest_framework import serializers
from .models import Department, Designation, EmployeeProfile, SalaryStructure, EmployeeDocument
from apps.accounts.serializers import UserSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'head', 'employee_count', 'created_at']

    def get_employee_count(self, obj):
        return obj.employees.filter(employment_status='active').count()


class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Designation
        fields = ['id', 'title', 'department', 'department_name', 'description']


class SalaryStructureSerializer(serializers.ModelSerializer):
    net_salary = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_allowances = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SalaryStructure
        fields = '__all__'


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = '__all__'
        read_only_fields = ['uploaded_by']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = '__all__'

    def get_profile_picture_url(self, obj):
        return obj.profile_picture_url


class EmployeeProfileUpdateSerializer(serializers.ModelSerializer):
    """Restricted serializer for employees updating their own profile."""
    class Meta:
        model = EmployeeProfile
        fields = ['phone', 'address', 'profile_picture']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    employee_id = serializers.CharField(source='user.employee_id')
    email = serializers.EmailField(source='user.email')
    role = serializers.CharField(source='user.role')
    is_active = serializers.BooleanField(source='user.is_active')
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = ['id', 'employee_id', 'email', 'full_name', 'role', 'is_active',
                  'department_name', 'designation_title', 'employment_status',
                  'joining_date', 'profile_picture_url']

    def get_profile_picture_url(self, obj):
        return obj.profile_picture_url
