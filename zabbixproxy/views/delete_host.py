import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import ServiceErrorHandler
from zabbixproxy.functions.credentials_functions import zabbix_login
from zabbixproxy.models import Host
from zabbixproxy.tasks import host_deletion_workflow

django_logger = logging.getLogger("django")


class HostDeletionView(APIView):
    """
    This endpoint is used to delete a host from the Zabbix proxy.
    """

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

    def delete(self, request):
        """
        This method is used to delete a host from the Zabbix proxy.
        """
        try:
            host_id = request.data.get("host_id")
            local_host_id = request.data.get("id")
            if not host_id or not local_host_id:
                django_logger.error("Host ID not provided")
                return Response(
                    {"status": "error", "message": "Host ID not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                host = Host.objects.get(pk=local_host_id)
                if host.host_id != host_id:
                    django_logger.error("Host ID does not match with local host ID")
                    return Response(
                        {
                            "status": "error",
                            "message": "Host ID does not match with device host ID",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if host_id == 0:
                    host.delete()
                    django_logger.info("Host deleted successfully")
                    return Response(
                        {"status": "success", "message": "Host deleted successfully"},
                        status=status.HTTP_200_OK,
                    )
                auth_token = self.get_zabbix_auth_token()
                workflow_task = host_deletion_workflow.delay(
                    api_url=self.api_url,
                    auth_token=auth_token,
                    host_id=host_id,
                    local_host_id=local_host_id,
                )
                return Response(
                    {
                        "status": "success",
                        "message": "Host deletion workflow started",
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

            except Host.DoesNotExist:
                django_logger.error("Host not found")
                return Response(
                    {"status": "error", "message": "Host not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Exception as e:
            django_logger.error("Error in deleting host: %s", e)
            return Response(
                {"error": "Error in deleting host"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
