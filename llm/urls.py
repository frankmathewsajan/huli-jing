from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, DailyScheduleViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"schedules", DailyScheduleViewSet, basename="schedule")
app_name = "llm"
urlpatterns = [
    path("", include(router.urls)),
]
