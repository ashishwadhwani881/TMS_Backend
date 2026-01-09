from rest_framework import serializers
from apps.tasks.models import Task


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "status", "priority"]


class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "created_by",
            "parent_task",
            "priority_escalated",
            "estimated_hours",
            "actual_hours",
            "deadline",
            "subtasks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]

    def validate_parent_task(self, parent):
        if parent is None:
            return parent

        instance = self.instance

        if instance and parent.id == instance.id:
            raise serializers.ValidationError(
                "Task cannot be parent of itself."
            )

        current = parent
        while current.parent_task:
            if instance and current.parent_task.id == instance.id:
                raise serializers.ValidationError(
                    "Circular parent-child relationship detected."
                )
            current = current.parent_task

        return parent

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["created_by"] = request.user
        return super().create(validated_data)
    
    def validate_assigned_to(self, user):
        print("VALIDATE ASSIGNED TO CALLED")
        print("REQUEST IN CONTEXT:", self.context.get("request"))
        request = self.context["request"]

        if request.user.role == "DEVELOPER" and user != request.user:
            raise serializers.ValidationError(
                "Developers can only assign tasks to themselves."
            )

        return user
    