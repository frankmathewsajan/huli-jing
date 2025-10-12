from rest_framework import serializers
from .models import Prompt

class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = [
            "id",
            "user",
            "type",
            "text",
            "llm_response",
            "hash",
            "used_count",
            "is_mock",
            "created_at"
        ]
        read_only_fields = ["id", "llm_response", "used_count", "created_at"]
