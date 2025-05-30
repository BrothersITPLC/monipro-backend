import logging
from typing import Any, cast

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import ServiceErrorHandler
from zabbixproxy.credentials_functions import zabbix_login

# Import the create_zabbix_agent function
from zabbixproxy.models import ZabbixHost, ZabbixHostGroup

# Update imports
from zabbixproxy.tasks import create_host_workflow

django_logger = logging.getLogger("django")


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
        port = 10050
        tags = "install"
        useip = 1

        # Get values from request data properly
        if "ip" in request_data:
            ip = request_data.get("ip")
        if "dns" in request_data:
            dns = request_data.get("dns")
        if "port" in request_data:
            port = request_data.get("port")

        # Get host from request data
        host = request_data.get("host")
        ip = request_data.get("ip")
        password = request_data.get(
            "password"
        )  # Fixed: was using ip instead of password
        username = request_data.get("username", "")  # Added username extraction
        network_device_type = request_data.get("network_device_type")
        device_type = request_data.get("device_type")

        # Validate required fields
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

        # In the post method, replace the task creation code with:
        try:
            auth_token = self.get_zabbix_auth_token()

            # Start the workflow task
            workflow_task = create_host_workflow.delay(
                user_id=user.id,
                host=host,
                ip=ip,
                port=port,
                username=username,
                password=password,
                dns=dns,
                useip=useip,
                hostgroup=hostgroup,
                api_url=self.api_url,
                auth_token=auth_token.auth,  # Pass the token string value instead of the object
                device_type=device_type,
                network_device_type=network_device_type or "",
                tags=tags,
            )

            # Return a response immediately with task ID
            return Response(
                {
                    "status": "success",  # Fixed typo: "sucess" -> "success"
                    "message": "Host creation started, you will get notified after 2 minutes",  # Fixed typo: "notfied" -> "notified"
                },
                status=status.HTTP_202_ACCEPTED,
            )

        except Exception as e:
            django_logger.exception(f"Error creating Zabbix host: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong, please try again later",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
