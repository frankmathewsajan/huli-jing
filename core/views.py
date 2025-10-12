from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Prompt
from .serializers import PromptSerializer
import hashlib
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .llm import generate_daily_plan_for_user

class DailyPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Generate and return the daily plan for the authenticated user.
        """
        try:
            plan = generate_daily_plan_for_user(request.user)
            return Response(plan.model_dump(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class PromptCreateView(generics.ListCreateAPIView):
    """
    POST: Create or retrieve a cached prompt for the authenticated user.
    GET:  List all prompts belonging to the authenticated user.
    """
    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only this user's prompts
        return Prompt.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Compute deterministic hash of (type + text)
        hash_key = hashlib.sha256(
            f"{data.get('type','other')}::{data.get('text','')}".encode("utf-8")
        ).hexdigest()

        data["hash"] = hash_key
        data["user"] = request.user.id

        # Check cache for *this user*
        cached_prompt = Prompt.objects.filter(user=request.user, hash=hash_key).first()
        if cached_prompt:
            cached_prompt.used_count += 1
            cached_prompt.save()
            serializer = self.get_serializer(cached_prompt)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Otherwise create a new prompt
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)