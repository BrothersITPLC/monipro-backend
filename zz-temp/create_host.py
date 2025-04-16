from typing import Any, cast

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import ServiceErrorHandler

# Import the create_zabbix_agent function
from zabbixproxy.ansibal.functions.ansibal_runner import create_zabbix_agent
from zabbixproxy.models import ZabbixAuthToken, ZabbixHost, ZabbixHostGroup
from zabbixproxy.views.credentials.functions import zabbix_login
from zabbixproxy.views.host_items.functions import create_host


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
        except ServiceErrorHandler as e:
            raise ServiceErrorHandler(f"{str(e)}")

    def post(self, request):
        """Creates a Zabbix Host for the authenticated user."""
        user = request.user
        request_data = request.data

        # Initialize default values
        dns = ""
        host_template = 10001
        port = 10050
        tags = "install"  # Default tag for Ansible
        useip = 1

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
        ip = request_data.get("ip")
        password = request_data.get("password")
        username = request_data.get("username", "")
        network_type = request_data.get("network_type")
        network_device_type = request_data.get("network_device_type")
        device_type = request_data.get("device_type")

        if not host:
            return Response(
                {"status": "error", "message": "Host name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not ip:
            useip = 0
            if not dns:
                return Response(
                    {"status": "error", "message": "Ip and dns are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if not password:
            return Response(
                {"status": "error", "message": "password is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not network_type:
            return Response(
                {"status": "error", "message": "network type is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if device_type != "vm":
            if not network_device_type:
                return Response(
                    {"status": "error", "message": "network device type is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if not device_type:
            return Response(
                {"status": "error", "message": "device type is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get hostgroup from database
        hostgroup_obj = (
            cast(Any, ZabbixHostGroup).objects.filter(created_by=user).first()
        )
        if not hostgroup_obj:
            return Response(
                {"status": "error", "message": "No host group found for this user"},
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
            auth_token = ZabbixAuthToken.objects.first()
            if not auth_token:
                auth_token = ZabbixAuthToken.get_or_create_token(
                    self.get_zabbix_auth_token()
                )

            # Fix for transaction.atomic() type issue
            atomic_context = cast(Any, transaction.atomic())

            # Use transaction to ensure database consistency
            with atomic_context:
                # First, deploy Zabbix agent using Ansible
                agent_response = create_zabbix_agent(
                    port=port,
                    target_host=ip,
                    username=username,
                    hostname=host,
                    password=password,
                    tags=tags,
                )

                # Check if agent deployment was successful
                if not isinstance(
                    agent_response, Response
                ) or not agent_response.data.get("overall_success", False):
                    # If agent deployment failed, raise an error
                    error_message = "Failed to deploy Zabbix agent"
                    if isinstance(agent_response, Response) and agent_response.data.get(
                        "errors"
                    ):
                        error_details = ", ".join(
                            [
                                e.get("error", "")
                                for e in agent_response.data.get("errors", [])
                            ]
                        )
                        error_message += f": {error_details}"
                    raise ServiceErrorHandler(error_message)

                # If agent deployment was successful, proceed with host creation
                hostid = create_host(
                    self.api_url,
                    auth_token,
                    hostgroup=hostgroup,
                    host=host,
                    ip=ip,
                    port=port,
                    dns=dns,
                    useip=useip,
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
                    username=username,
                    password=password,
                    network_type=request_data.get("network_type", ""),
                )

            # Return success response
            return Response(
                {
                    "status": "success",
                    "message": "Host and Zabbix agent created successfully",
                    "host_id": hostid,
                },
                status=status.HTTP_201_CREATED,
            )

        except ServiceErrorHandler as e:
            return Response(
                {"status": "error", "message": f"{str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            # Added error logging
            import logging

            logging.exception(f"Error creating Zabbix host: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong, please try again later",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
