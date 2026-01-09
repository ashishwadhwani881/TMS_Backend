from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
import csv

from django.http import HttpResponse
from django.db import models
from django.contrib.auth import get_user_model

from apps.tasks.models import Task, TaskHistory

def generate_weekly_report(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="weekly_task_report.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "Task ID",
        "Title",
        "Status",
        "Priority",
        "Assigned To",
        "Created By",
        "Deadline",
    ])

    one_week_ago = timezone.now() - timedelta(days=7)
    tasks = queryset.filter(created_at__gte=one_week_ago)

    for task in tasks:
        writer.writerow([
            task.id,
            task.title,
            task.status,
            task.priority,
            task.assigned_to.username,
            task.created_by.username,
            task.deadline,
        ])

    return response

generate_weekly_report.short_description = "Generate Weekly Report"


class TasksNeedingAttentionFilter(admin.SimpleListFilter):
    title = "Tasks Needing Attention"
    parameter_name = "needs_attention"

    def lookups(self, request, model_admin):
        return [("yes", "Yes")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            overdue_date = timezone.now() - timedelta(days=3)
            return queryset.filter(
                models.Q(status="blocked") |
                models.Q(deadline__lt=overdue_date) |
                models.Q(actual_hours__gt=models.F("estimated_hours") * 1.5)
            )
        return queryset


User = get_user_model()

def reassign_tasks(modeladmin, request, queryset):
    if "apply" in request.POST:
        new_user_id = request.POST.get("new_user")
        new_user = User.objects.get(id=new_user_id)

        active_tasks = Task.objects.filter(
            assigned_to=new_user,
            status__in=["pending", "in_progress", "blocked"]
        ).count()

        if active_tasks > 10:
            messages.warning(
                request,
                f"{new_user.username} already has {active_tasks} active tasks!"
            )

        queryset.update(assigned_to=new_user)

        messages.success(
            request,
            f"{queryset.count()} tasks reassigned to {new_user.username}"
        )
        return

reassign_tasks.short_description = "Reassign Tasks"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "colored_status",
        "priority",
        "assigned_to",
        "deadline",
    )

    list_filter = (
        "priority",
        TasksNeedingAttentionFilter,  
    )

    actions = [
        generate_weekly_report,
        reassign_tasks,
    ]

    def colored_status(self, obj):
        colors = {
            "pending": "gray",
            "in_progress": "blue",
            "blocked": "red",
            "completed": "green",
        }
        return format_html(
            '<span style="color:{};">{}</span>',
            colors.get(obj.status, "black"),
            obj.status
        )

    colored_status.short_description = "Status"


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "task",
        "field",
        "old_value",
        "new_value",
        "changed_by",
        "created_at",
    )
