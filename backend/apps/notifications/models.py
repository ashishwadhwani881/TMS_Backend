from django.db import models
from django.conf import settings
from apps.tasks.models import Task


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
