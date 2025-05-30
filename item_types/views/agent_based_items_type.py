# views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from item_types.models import AgentMonitoringItemType
from item_types.serializers import AgentMonitoringItemTypeSerializer


class AgentMonitoringItemTypesListView(APIView):
    def get(self, request):
        items = AgentMonitoringItemType.objects.all()
        if not items.exists():
            return Response(
                {"status": "error", "message": "No data found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AgentMonitoringItemTypeSerializer(items, many=True)
        if not serializer.data:
            return Response(
                {"status": "error", "message": "No data found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {
                "status": "success",
                "message": "Data retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
