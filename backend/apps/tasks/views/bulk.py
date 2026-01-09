from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.tasks.serializers.bulk_update import BulkTaskStatusUpdateSerializer
from apps.tasks.services.bulk_update import bulk_update_task_status


class BulkUpdateMixin:

    @action(detail=False, methods=["post"], url_path="bulk-update")
    def bulk_update(self, request):
        serializer = BulkTaskStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tasks = bulk_update_task_status(
            task_ids=serializer.validated_data["task_ids"],
            new_status=serializer.validated_data["status"],
        )

        return Response(
            {"updated_count": tasks.count()},
            status=status.HTTP_200_OK
        )
