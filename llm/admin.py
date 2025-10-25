from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import DailySchedule, Task


# ==========================================================
# Inline/Helper functions
# ==========================================================
@admin.register(DailySchedule)
class DailyScheduleAdmin(admin.ModelAdmin):
    list_display = ("date", "day_of_week", "user", "total_tasks", "total_committed_hours", "total_available_hours")
    search_fields = ("user__email", "day_of_week", "date")
    list_filter = ("day_of_week",)
    ordering = ("-date",)
    filter_horizontal = ("tasks",)
    readonly_fields = ("created_at", "updated_at")


# ==========================================================
# Task Admin
# ==========================================================
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "task_name",
        "priority",
        "estimated_duration_minutes",
        "completed",
        "rating",
        "schedule_dates",  # 👈 NEW: shows linked schedule dates
    )
    list_filter = ("priority", "completed", "rating")
    search_fields = ("task_name", "description", "related_goal")
    ordering = ("-priority", "estimated_duration_minutes")
    actions = ["mark_as_completed", "mark_as_incomplete"]

    # -------------------------------
    # Custom display methods
    # -------------------------------
    def schedule_dates(self, obj):
        """Show all schedule dates this task belongs to."""
        schedules = obj.daily_schedules.all().values_list("date", flat=True)
        return ", ".join(str(d) for d in schedules) if schedules else "—"
    schedule_dates.short_description = "Schedule Dates"

    # -------------------------------
    # Custom admin actions
    # -------------------------------
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(completed=True)
        self.message_user(request, f"{updated} task(s) marked as completed.")
    mark_as_completed.short_description = "✅ Mark selected tasks as completed"

    def mark_as_incomplete(self, request, queryset):
        updated = queryset.update(completed=False)
        self.message_user(request, f"{updated} task(s) marked as incomplete.")
    mark_as_incomplete.short_description = "❌ Mark selected tasks as incomplete"
