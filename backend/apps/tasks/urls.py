from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.tasks.views.task_viewset import TaskViewSet
from apps.tasks.views.analytics import TaskAnalyticsView

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("analytics/", TaskAnalyticsView.as_view(), name="task-analytics"),
]

urlpatterns += router.urls
