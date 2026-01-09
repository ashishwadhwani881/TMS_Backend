from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from apps.tasks.models import Task
from apps.tasks.serializers.task import TaskSerializer
from apps.tasks.permissions import TaskPermission,TimeBasedTaskPermission
from apps.tasks.services.status_cascade import handle_status_change
from apps.tasks.services.history_logger import log_task_change
from apps.tasks.views.bulk import BulkUpdateMixin

class TaskViewSet(BulkUpdateMixin,ModelViewSet):
    queryset = Task.objects.select_related(
        "assigned_to", "created_by", "parent_task"
    ).prefetch_related("subtasks")

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskPermission ,  TimeBasedTaskPermission,]

    def perform_create(self, serializer):
        task = serializer.save()
        handle_status_change(task)

    def perform_update(self, serializer):
        old_task = self.get_object()
        new_task = serializer.save()
        handle_status_change(new_task, old_task)

    def perform_update(self, serializer):
        old_task = self.get_object()
        new_task = serializer.save()

        handle_status_change(
            new_task,
            old_task=old_task,
            user=self.request.user
        )

        if old_task.status != new_task.status:
            log_task_change(
                task=new_task,
                field="status",
                old_value=old_task.status,
                new_value=new_task.status,
                changed_by=self.request.user,
                reason="Manual update",
            )