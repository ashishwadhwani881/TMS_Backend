from apps.tasks.models import TaskHistory


def log_task_change(
    *,
    task,
    field,
    old_value,
    new_value,
    changed_by=None,
    reason=""
):
    TaskHistory.objects.create(
        task=task,
        field=field,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        changed_by=changed_by,
        reason=reason,
    )
