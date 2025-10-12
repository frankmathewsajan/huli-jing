from django.urls import path
from .views import PromptCreateView

app_name = "core"

urlpatterns = [
    path("prompts/", PromptCreateView.as_view(), name="prompt-create"),
]
