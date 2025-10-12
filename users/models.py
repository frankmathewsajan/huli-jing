from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=100, default="UTC")

    def __str__(self):
        return self.username
