from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.tasks.models import Task


def bulk_update_task_status(task_ids, new_status):
    """
    Validates and updates tasks atomically.
    """

    tasks = Task.objects.select_related(
        "parent_task"
    ).prefetch_related(
        "subtasks"
    ).filter(id__in=task_ids)

    if tasks.count() != len(task_ids):
        raise ValidationError("One or more tasks not found")

  

    for task in tasks:
       
        if new_status == Task.Status.COMPLETED:
            for child in task.subtasks.all():
                if child.status in [
                    Task.Status.IN_PROGRESS,
                    Task.Status.BLOCKED
                ] and child.id not in task_ids:
                    raise ValidationError(
                        f"Task {task.id} cannot be completed due to active child {child.id}"
                    )

        
        if (
            task.parent_task
            and new_status == Task.Status.BLOCKED
            and task.parent_task.id not in task_ids
        ):
            raise ValidationError(
                f"Blocking child {task.id} requires parent {task.parent_task.id} to be included"
            )

    

    with transaction.atomic():
        tasks.update(status=new_status)

    return tasks
