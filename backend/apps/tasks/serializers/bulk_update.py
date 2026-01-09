from rest_framework import serializers
from apps.tasks.models import Task


class BulkTaskStatusUpdateSerializer(serializers.Serializer):
    task_ids = serializers.ListField(
        child=serializers.UUIDField()
    )
    status = serializers.ChoiceField(
        choices=Task.Status.choices
    )
