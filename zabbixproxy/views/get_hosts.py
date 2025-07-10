from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.models import HostLifecycle
from zabbixproxy.serializers import ActiveHostSerializer


class GetZabbixHostes(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_hosts = HostLifecycle.objects.filter(status="active")

        if not active_hosts:
            return Response(
                {
                    "status": "error",
                    "message": "No hosts found for the user.",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ActiveHostSerializer(active_hosts, many=True)

        return Response(
            {
                "status": "success",
                "message": "Hosts retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
