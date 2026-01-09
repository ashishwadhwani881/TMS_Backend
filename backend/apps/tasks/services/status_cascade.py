from rest_framework.exceptions import ValidationError
from apps.tasks.models import Task
from apps.tasks.services.history_logger import log_task_change


def handle_status_change(new_task, old_task=None, user=None):

   
    if old_task and old_task.status == new_task.status:
        return

    
    if new_task.status == Task.Status.COMPLETED:
        children = new_task.subtasks.all()

        for child in children:
            if child.status in [
                Task.Status.IN_PROGRESS,
                Task.Status.BLOCKED
            ]:
                raise ValidationError(
                    "Cannot complete parent task while a child is in progress or blocked."
                )

        
        for child in children.filter(status=Task.Status.PENDING):
            old_status = child.status
            child.status = Task.Status.COMPLETED
            child.save()

            log_task_change(
                task=child,
                field="status",
                old_value=old_status,
                new_value=Task.Status.COMPLETED,
                changed_by=user,
                reason="Auto-completed due to parent completion",
            )

    
    if new_task.parent_task and new_task.status == Task.Status.BLOCKED:
        parent = new_task.parent_task

        if parent.status != Task.Status.BLOCKED:
            old_status = parent.status
            parent.status = Task.Status.BLOCKED
            parent.save()

            log_task_change(
                task=parent,
                field="status",
                old_value=old_status,
                new_value=Task.Status.BLOCKED,
                changed_by=user,
                reason="Blocked due to child task",
            )
