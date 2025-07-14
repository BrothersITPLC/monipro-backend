import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

django_logger = logging.getLogger("django")
from utils import ServiceErrorHandler
from zabbixproxy.models import Host, HostLifecycle
from zabbixproxy.serializers import HostSerializer


class HostAPIView(APIView):
    """
    API view for managing hosts in the Zabbix proxy.
    This view allows authenticated users to create, retrieve, update, and delete hosts.
    It handles errors gracefully and logs them for debugging purposes.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            # Ensure the organization and host group exist
            host_group = user.organization.organization_hostgroup.first()
            if not host_group:
                django_logger.error(
                    "No host group associated with the user's organization."
                )
                return Response(
                    {
                        "status": "error",
                        "message": "No host group found for your organization.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get hosts in the user's host group
            hosts = Host.objects.filter(host_group=host_group).select_related(
                "host_group"
            )
            if not hosts.exists():
                django_logger.warning("No hosts found in the host group.")
                return Response(
                    {"status": "error", "message": "No hosts found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get lifecycle entries (linked via foreign key)
            lifecycle_host_ids = set(
                HostLifecycle.objects.filter(host__in=hosts).values_list(
                    "host_id", flat=True
                )
            )

            hosted_hosts = []
            local_hosts = []

            for host in hosts:
                serialized = HostSerializer(host).data
                if host.id in lifecycle_host_ids:
                    hosted_hosts.append(serialized)
                else:
                    local_hosts.append(serialized)

            return Response(
                {
                    "status": "success",
                    "message": "Hosts list retrieved successfully.",
                    "data": {
                        "hosted_hosts": hosted_hosts,
                        "local_hosts": local_hosts,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            django_logger.exception("An error occurred while retrieving hosts.")
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred while retrieving hosts.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        user = request.user
        try:
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

            if Host.objects.filter(host=data["host"]).exists():
                django_logger.error("Host name %s is already taken.", data["host"])
                return Response(
                    {
                        "status": "error",
                        "message": "Host name is taken please choose another name.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

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
                    "status": "error",
                    "message": "Failed to create host",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ServiceErrorHandler as e:
            django_logger.error("Service error: %s", str(e))
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            django_logger.error("Unexpected error: %s", str(e))
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, pk):
        try:
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
        except ServiceErrorHandler as e:
            django_logger.error("Service error: %s", str(e))
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            django_logger.error("Unexpected error: %s", str(e))
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
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
        except Exception as e:
            django_logger.error("Unexpected error: %s", str(e))
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
