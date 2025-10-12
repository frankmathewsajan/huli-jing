from django.urls import path
from .views import PromptCreateView, DailyPlanView

app_name = "core"

urlpatterns = [
    path("prompts/", PromptCreateView.as_view(), name="prompt-create"),

    path("daily-plan/", DailyPlanView.as_view(), name="daily-plan"),
]
