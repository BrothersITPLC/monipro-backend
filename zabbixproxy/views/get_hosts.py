from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.models import ZabbixHost
from zabbixproxy.serializers import ZabbixHostSerializer


class GetZabixHostes(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hosts = cast(Any, ZabbixHost).objects.filter(hostgroup__created_by=request.user)

        if not hosts:
            return Response(
                {
                    "status": "error",
                    "message": "No hosts found for the user.",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ZabbixHostSerializer(hosts, many=True)

        return Response(
            {
                "status": "success",
                "message": "Hosts retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
