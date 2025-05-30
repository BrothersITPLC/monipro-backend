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
from zabbixproxy.tasks import simple_check_host_create_workflow

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

    def post(self, request, pk):
        """Creates a Zabbix Host for the authenticated user."""
        user = request.user
        request_data = request.data

        ip = ""
        dns = ""
        useip = 0
        port = 10050
        tags = "install"

        host = Host.objects.get(pk=pk)
        if not host:
            return Response(
                {"status": "error", "message": "Host not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if host.ip is None:
            dns = host.dns
            ip = ""
            useip = 0
        else:
            dns = ""
            ip = host.ip
            useip = 1

        host = host.host
        host_group = host.host_group

        try:
            auth_token = self.get_zabbix_auth_token()
            workflow_task = simple_check_host_create_workflow.delay(
                user_id=user.id,
                host=host,
                ip=ip,
                port=port,
                dns=dns,
                useip=useip,
                api_url=self.api_url,
                auth_token=auth_token.auth,
                hostgroup=host_group,
                tags=tags,
                item_list=request_data,
            )

            return Response(
                {
                    "status": "success",
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
