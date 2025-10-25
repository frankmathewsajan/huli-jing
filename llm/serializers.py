from rest_framework import serializers
from .models import Task, DailySchedule


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "task_name",
            "description",
            "estimated_duration_minutes",
            "priority",
            "related_goal",
            "suggested_time",
            "is_flexible",
            "completed",
            "feedback",
            "rating",
        ]
        read_only_fields = ["id"]


class DailyScheduleSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)

    class Meta:
        model = DailySchedule
        fields = [
            "id",
            "user",
            "date",
            "day_of_week",
            "tasks",
            "total_committed_hours",
            "total_available_hours",
            "notes",
            "updated_commitments",
            "updated_goals",
            "user_behaviour_patterns",
        ]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        tasks_data = validated_data.pop("tasks", [])
        schedule = DailySchedule.objects.create(**validated_data)
        for task_data in tasks_data:
            task = Task.objects.create(**task_data)
            schedule.tasks.add(task)
        return schedule
