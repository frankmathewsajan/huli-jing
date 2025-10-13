from django.db import models


# ======================================================
# Task Model
# ======================================================
class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Highest", "Highest"),
        ("High", "High"),
        ("Urgent", "Urgent"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    task_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    estimated_duration_minutes = models.PositiveIntegerField(default=0)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
    related_goal = models.CharField(max_length=255, blank=True, null=True)
    suggested_time = models.TimeField(blank=True, null=True)
    is_flexible = models.BooleanField(default=True)

    class Meta:
        ordering = ["-priority", "estimated_duration_minutes"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self) -> str:
        return f"{self.task_name} ({self.priority})"


# ======================================================
# Daily Schedule Model
# ======================================================
class DailySchedule(models.Model):
    date = models.DateField(unique=True)
    day_of_week = models.CharField(max_length=20)
    tasks = models.ManyToManyField(Task, related_name="daily_schedules")

    total_committed_hours = models.FloatField(default=0.0)
    total_available_hours = models.FloatField(default=0.0)
    notes = models.TextField(blank=True)

    # 🧠 Adaptive LLM-updated fields
    updated_commitments = models.JSONField(default=list, blank=True)
    updated_goals = models.JSONField(default=list, blank=True)
    user_behaviour_patterns = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]
        verbose_name = "Daily Schedule"
        verbose_name_plural = "Daily Schedules"

    def __str__(self) -> str:
        return f"{self.day_of_week}, {self.date}"

    @property
    def total_tasks(self):
        return self.tasks.count()

    @property
    def high_priority_tasks(self):
        return self.tasks.filter(priority__in=["Highest", "Urgent", "High"]).count()

    def summary(self):
        """Returns a compact text summary (useful for debugging/UI)."""
        return {
            "date": str(self.date),
            "tasks": self.total_tasks,
            "high_priority": self.high_priority_tasks,
            "available_hours": self.total_available_hours,
        }
