import logging
from typing import Any, cast

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import ServiceErrorHandler
from zabbixproxy.credentials_functions import zabbix_login
from zabbixproxy.models import Host
from zabbixproxy.tasks import host_creation_workflow

django_logger = logging.getLogger("django")


class SimpleCheckZabbixHostCreationView(APIView):
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
        item_template_list = request.data
        local_host_id = item_template_list.get("local_host_id", None)
        if local_host_id is None:
            return Response(
                {"status": "error", "message": "local_host_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ip = ""
        dns = ""
        useip = 0
        port = 10050

        try:
            host = Host.objects.get(pk=local_host_id)
        except Host.DoesNotExist:
            django_logger.error(f"Host with ID {local_host_id} not found")
            return Response(
                {"status": "error", "message": "Host not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            django_logger.exception(f"Database error fetching Host: {str(e)}")
            return Response(
                {"status": "error", "message": "Failed to retrieve host information."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not host.ip:
            dns = host.dns
            useip = 0
        else:
            ip = host.ip
            useip = 1

        host_name = host.host
        host_group = host.host_group.hostgroupid if host.host_group else None
        try:
            auth_token = self.get_zabbix_auth_token()
            workflow_task = host_creation_workflow.delay(
                host_name=host_name,
                ip=ip,
                port=port,
                dns=dns,
                useip=useip,
                api_url=self.api_url,
                auth_token=auth_token,
                hostgroup=host_group,
                item_template_list=item_template_list,
            )

            return Response(
                {
                    "status": "success",
                    "message": "Host creation started, you will get notified after 2 minutes",
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
