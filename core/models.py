from django.db import models
from django.conf import settings
from django.utils import timezone



class Prompt(models.Model):
    """
    Cache of raw prompt text + the LLM response (structured).
    hash: deterministic hash of (type + text) to allow quick exact-match cache hits.
    is_mock: mark dev-mode mocked responses if using local test data.
    """
    PROMPT_TYPE_CHOICES = [
        ("goal", "Goal Input"),
        ("commitment", "Commitment Input"),
        ("summary", "Summary Request"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prompts"
    )
    type = models.CharField(max_length=32, choices=PROMPT_TYPE_CHOICES, default="other")
    text = models.TextField(help_text="Raw natural language prompt from user or system")
    llm_response = models.JSONField(null=True, blank=True, help_text="Structured JSON returned by LLM")
    hash = models.CharField(max_length=128, unique=True, help_text="sha256(or similar) of type+text")
    used_count = models.PositiveIntegerField(default=0)
    is_mock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Prompt({self.type}, hash={self.hash[:8]})"
