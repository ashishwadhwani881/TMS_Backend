from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import uuid

class User(AbstractUser):

    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Manager"
        DEVELOPER = "DEVELOPER", "Developer"
        AUDITOR = "AUDITOR", "Auditor"
    
    id=models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices
    )

    email = models.EmailField(unique=True)

    is_email_verified = models.BooleanField(default=False)

    timezone = models.CharField(
        max_length=50,
        default="Asia/Kolkata"
    )

    REQUIRED_FIELDS = ["email", "role"]

    def __str__(self):
        return f"{self.username} ({self.role})"
    


class UserSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    refresh_jti = models.CharField(max_length=255, unique=True)
    device = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]