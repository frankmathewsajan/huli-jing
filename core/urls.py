from django.urls import path

from .views import PromptCreateView, OnboardUserView, DailyPlanView

app_name = "core"

urlpatterns = [
    path("prompts/", PromptCreateView.as_view(), name="prompt-create"),

    path("onboard/", OnboardUserView.as_view(), name="onboard-user"),
    path("daily-plan/", DailyPlanView.as_view(), name="daily-plan"),
]
