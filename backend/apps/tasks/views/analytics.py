from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.tasks.services.analytics import (
    get_my_tasks_analytics,
    get_team_tasks_analytics,
    calculate_efficiency_score,
)


class TaskAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        my_tasks = get_my_tasks_analytics(user)
        team_tasks = get_team_tasks_analytics(user)
        efficiency = calculate_efficiency_score(user)

        return Response({
            "my_tasks": my_tasks,
            "team_tasks": team_tasks,
            "efficiency_score": efficiency,
        })
