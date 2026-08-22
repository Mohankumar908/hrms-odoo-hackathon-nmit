from rest_framework import serializers
from .models import Task, TaskComment


class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ['author']


class TaskSerializer(serializers.ModelSerializer):
    assignee_names = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by']

    def get_assignee_names(self, obj):
        return [{'id': str(u.id), 'name': u.full_name} for u in obj.assignees.all()]


class TaskListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    assignee_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'project', 'project_name', 'priority', 'status',
                  'progress', 'deadline', 'assignee_count', 'created_at']

    def get_assignee_count(self, obj):
        return obj.assignees.count()


class TaskUpdateSerializer(serializers.ModelSerializer):
    """For employees updating their own task status and progress."""
    class Meta:
        model = Task
        fields = ['status', 'progress', 'actual_hours']
