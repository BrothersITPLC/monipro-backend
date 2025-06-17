from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.models import HostLifecycle
from zabbixproxy.serializers import TemplateSerializer


class GetTemplateNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        host_id = request.GET.get("hostids")

        if not host_id:
            return Response(
                {
                    "status": "error",
                    "message": "Missing 'hostids' query parameter.",
                    "data": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_hosts = HostLifecycle.objects.filter(
            host__host_id=host_id, status="active"
        )

        if not active_hosts.exists():
            return Response(
                {
                    "status": "error",
                    "message": "No active monitoring items found for this host.",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TemplateSerializer(active_hosts, many=True)
        template_names = []
        template = serializer.data[0]["template"]
        for t in template:
            template_names.append(t["name"])

        return Response(
            {
                "status": "success",
                "message": "Hosts retrieved successfully.",
                "data": template_names,
            },
            status=status.HTTP_200_OK,
        )
