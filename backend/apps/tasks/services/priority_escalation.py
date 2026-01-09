from django.utils import timezone
from datetime import timedelta

from apps.tasks.models import Task
from apps.tasks.constants import PRIORITY_ORDER
from apps.notifications.models import Notification


def escalate_priorities():
    now = timezone.now()
    threshold = now + timedelta(hours=24)

    tasks = Task.objects.filter(
        deadline__lte=threshold,
        status__in=[
            Task.Status.PENDING,
            Task.Status.IN_PROGRESS,
            Task.Status.BLOCKED,
        ],
        priority_escalated=False,
    )

    for task in tasks:
        current_priority = task.priority

        if current_priority not in PRIORITY_ORDER:
            continue

        idx = PRIORITY_ORDER.index(current_priority)

        if idx < len(PRIORITY_ORDER) - 1:
            new_priority = PRIORITY_ORDER[idx + 1]

            task.priority = new_priority
            task.priority_escalated = True
            task.save(update_fields=["priority", "priority_escalated"])

            Notification.objects.create(
                user=task.assigned_to,
                task=task,
                message=f"Priority escalated to {new_priority} due to approaching deadline",
            )
