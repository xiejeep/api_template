from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    """任务序列化器"""
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
