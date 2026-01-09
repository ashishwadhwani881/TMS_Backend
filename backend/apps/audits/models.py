from django.db import models
from django.conf import settings


class RateLimitCounter(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    window_start = models.DateTimeField()
    read_count = models.PositiveIntegerField(default=0)
    write_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("user", "window_start")


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    status_code = models.PositiveIntegerField()
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.path}"
