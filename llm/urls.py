from django.urls import path
from llm.views import DailyPlanView

app_name = "llm"

urlpatterns = [

    path("daily-plan/", DailyPlanView.as_view(), name="daily-plan"),
]
