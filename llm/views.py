from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated  
from llm.planners.daily_plan import generate_daily_plan_for_user

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
      