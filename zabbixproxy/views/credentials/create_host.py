from typing import Any, cast

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.models import ZabbixHost, ZabbixHostGroup
from zabbixproxy.views.credentials.host_creat_function import (
    ZabbixServiceError,
    create_host,
)
from zabbixproxy.views.credentials.zabbiz_login_function import zabbix_login


class ZabbixHostCreationView(APIView):
    api_url = settings.ZABBIX_API_URL
    username = settings.ZABBIX_ADMIN_USER
    password = settings.ZABBIX_ADMIN_PASSWORD
    default_password = settings.ZABBIX_DEFAULT_PASSWORD
    permission_classes = [IsAuthenticated]

    def get_zabbix_auth_token(self):
        try:
            return zabbix_login(
                api_url=self.api_url, username=self.username, password=self.password
            )
        except ZabbixServiceError as e:
            # Re-raise with more context
            raise ZabbixServiceError(
                f"Failed to obtain Zabbix authentication token: {str(e)}"
            )

    def post(self, request):
        """Creates a Zabbix Host for the authenticated user."""
        user = request.user
        request_data = request.data

        # Initialize default values
        ip = ""
        dns = ""
        host_template = 10001
        port = 10050

        # Get values from request data properly
        if "ip" in request_data:
            ip = request_data.get("ip")
        if "dns" in request_data:
            dns = request_data.get("dns")
        if "host_template" in request_data:
            host_template = request_data.get("host_template")
        if "port" in request_data:
            port = request_data.get("port")

        # Get host from request data
        host = request_data.get("host")
        if not host:
            return Response(
                {"error": "Host name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get hostgroup from database
        hostgroup_obj = (
            cast(Any, ZabbixHostGroup).objects.filter(created_by=user).first()
        )
        if not hostgroup_obj:
            return Response(
                {"error": "No host group found for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hostgroup = hostgroup_obj.hostgroupid

        # Check if host already exists with proper filter conditions
        filter_conditions = {}
        if "ip" in request_data and request_data.get("ip"):
            filter_conditions["ip"] = request_data.get("ip")
        if "host" in request_data and request_data.get("host"):
            filter_conditions["host"] = request_data.get("host")
        if "domainName" in request_data and request_data.get("domainName"):
            filter_conditions["domainName"] = request_data.get("domainName")

        if filter_conditions:
            existing_host = (
                cast(Any, ZabbixHost).objects.filter(**filter_conditions).first()
            )
            if existing_host:
                return Response(
                    {
                        "status": "error",
                        "message": "Host with this IP, name, or domain name already exists",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            # Get auth token
            auth_token = self.get_zabbix_auth_token()

            # Fix for transaction.atomic() type issue
            atomic_context = cast(Any, transaction.atomic())
            # Use transaction to ensure database consistency
            with atomic_context:
                # Create host in Zabbix
                hostid = create_host(
                    self.api_url,
                    auth_token,
                    hostgroup=hostgroup,
                    host=host,
                    ip=ip,
                    port=port,
                    dns=dns,
                    host_template=host_template,
                )

                # Create host record in our database
                zabbix_host = cast(Any, ZabbixHost).objects.create(
                    hostgroup=hostgroup_obj,
                    hostid=hostid,
                    host=host,
                    ip=ip,
                    port=port,
                    dns=dns,
                    host_template=host_template,
                    device_type=request_data.get("device_type", ""),
                    network_device_type=request_data.get("network_device_type", ""),
                    username=request_data.get("username", ""),
                    password=request_data.get("password", ""),
                    network_type=request_data.get("network_type", ""),
                )

            # Return success response
            return Response(
                {
                    "status": "success",
                    "message": "Host created successfully",
                    "host_id": hostid,
                },
                status=status.HTTP_201_CREATED,
            )

        except ZabbixServiceError as e:
            return Response(
                {"status": "error", "message": f"Zabbix service error: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
