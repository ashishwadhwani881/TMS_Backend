from django.utils import timezone
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from apps.tasks.models import Task

def get_my_tasks_analytics(user):
    qs = Task.objects.filter(assigned_to=user)

    total = qs.count()

    by_status = (
        qs.values("status")
        .annotate(count=Count("id"))
    )

    by_status_dict = {
        item["status"]: item["count"] for item in by_status
    }

    overdue_count = qs.filter(
        deadline__lt=timezone.now(),
        status__in=["pending", "in_progress", "blocked"],
    ).count()

    
    completed = qs.filter(status="completed")

    avg_completion_time = completed.aggregate(
        avg_time=Avg(
            ExpressionWrapper(
                F("updated_at") - F("created_at"),
                output_field=DurationField(),
            )
        )
    )["avg_time"]

    avg_hours = (
        round(avg_completion_time.total_seconds() / 3600, 2)
        if avg_completion_time else 0
    )

    return {
        "total": total,
        "by_status": by_status_dict,
        "overdue_count": overdue_count,
        "avg_completion_time": f"{avg_hours} hours",
    }

def get_team_tasks_analytics(user):

    if user.role == "AUDITOR":
        qs = Task.objects.all()

    elif user.role == "MANAGER":
        qs = Task.objects.filter(created_by=user)

    else:  # DEVELOPER
        qs = Task.objects.filter(created_by__role="MANAGER")

    total = qs.count()

    blocked_tasks = qs.filter(status="blocked").values(
        "id", "title", "assigned_to__username"
    )

    priority_distribution = (
        qs.values("priority")
        .annotate(count=Count("id"))
    )

    priority_dict = {
        item["priority"]: item["count"]
        for item in priority_distribution
    }

    return {
        "total": total,
        "blocked_tasks_needing_attention": list(blocked_tasks),
        "priority_distribution": priority_dict,
    }

def calculate_efficiency_score(user):

    completed = Task.objects.filter(
        assigned_to=user,
        status="completed"
    )

    total_completed = completed.count()
    if total_completed == 0:
        return 0

    on_time = completed.filter(
        deadline__gte=F("updated_at")
    ).count()

    base_ratio = on_time / total_completed

    avg_hours = completed.aggregate(
        avg_actual=Avg("actual_hours"),
        avg_estimated=Avg("estimated_hours"),
    )

    if (
        avg_hours["avg_actual"]
        and avg_hours["avg_estimated"]
        and avg_hours["avg_actual"] <= avg_hours["avg_estimated"]
    ):
        bonus = 1.2
    else:
        bonus = 0.8

    score = round(base_ratio * bonus * 100, 2)
    return score
