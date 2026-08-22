from rest_framework import serializers
from .models import Project, ProjectMember


class ProjectMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.full_name', read_only=True)
    employee_id = serializers.CharField(source='user.employee_id', read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'username', 'employee_id', 'role', 'joined_at']


class ProjectSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='project_manager.full_name', read_only=True)
    members = ProjectMemberSerializer(source='memberships', many=True, read_only=True)
    task_stats = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_task_stats(self, obj):
        from apps.tasks.models import Task
        tasks = Task.objects.filter(project=obj)
        return {
            'total': tasks.count(),
            'completed': tasks.filter(status='completed').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'delayed': tasks.filter(status='delayed').count(),
            'not_started': tasks.filter(status='not_started').count(),
        }


class ProjectListSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='project_manager.full_name', read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'client', 'status', 'progress', 'start_date', 'end_date',
                  'manager_name', 'member_count', 'created_at']

    def get_member_count(self, obj):
        return obj.memberships.count()
