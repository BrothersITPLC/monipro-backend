import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

django_logger = logging.getLogger("django")
from zabbixproxy.models import Host
from zabbixproxy.serializers import HostSerializer


class HostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        hosts = Host.objects.filter(
            host_group__id=user.organization.organization_hostgroup.first().id
        )
        if not hosts:
            django_logger.error("No hosts found in the database.")
            return Response(
                {
                    "status": "error",
                    "message": "Hosts not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = HostSerializer(hosts, many=True)
        return Response(
            {
                "status": "success",
                "message": "Hosts list retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        user = request.user
        host_group = user.organization.organization_hostgroup.first()
        if not host_group:
            django_logger.error("User has no associated organization.")
            return Response(
                {
                    "status": "error",
                    "message": "User has no associated organization",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        data["host_group"] = host_group.id

        serializer = HostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Host created successfully",
                },
                status=status.HTTP_201_CREATED,
            )
        django_logger.error("Failed to create host: %s", serializer.errors)
        return Response(
            {
                "status": "error",  # Changed from status: to "status":
                "message": "Failed to create host",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        host = Host.objects.filter(pk=pk).first()
        if not host:
            django_logger.error("Host with ID %s not found.", pk)
            return Response(
                {
                    "status": "error",
                    "message": "Host not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = HostSerializer(instance=host, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Host updated successfully",
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Failed to partially update host",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        host = Host.objects.filter(pk=pk).first()
        if not host:
            django_logger.error("Host with ID %s not found.", pk)
            return Response(
                {
                    "status": "error",
                    "message": "Host not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        host.delete()
        return Response(
            {
                "status": "success",
                "message": "Host deleted successfully",
            },
            status=status.HTTP_200_OK,
        )
