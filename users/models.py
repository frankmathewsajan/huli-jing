from django.db import models

from django.contrib.auth.models import AbstractUser
from django.conf import settings
import hashlib


class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=100, default="UTC")

    def __str__(self):
        return self.username


class UserPattern(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    pattern_text = models.TextField()  # from daily_plan.user_behaviour_patterns
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pattern for {self.user.username} on {self.date}"


class Goal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals"
    )
    llm_response = models.JSONField()  # store refined goal text, priority, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hash = models.CharField(max_length=64, unique=True, editable=False)

    def save(self, *args, **kwargs):
        # Use the serialized llm_response to compute a hash
        self.hash = hashlib.sha256(
            f"{self.user_id}::goal::{self.llm_response}".encode("utf-8")
        ).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.llm_response)[:50] + (
            "..." if len(str(self.llm_response)) > 50 else ""
        )


class Commitment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commitments"
    )
    llm_response = models.JSONField()  # store refined commitment details
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hash = models.CharField(max_length=64, unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.hash = hashlib.sha256(
            f"{self.user_id}::commitment::{self.llm_response}".encode("utf-8")
        ).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.llm_response)[:50] + (
            "..." if len(str(self.llm_response)) > 50 else ""
        )
