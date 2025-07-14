import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.functions.credentials_functions import zabbix_login

django_logger = logging.getLogger("django")

from utils import ServiceErrorHandler
from zabbixproxy.models import TemplateGroupMirror
from zabbixproxy.serializers import TemplateGroupSerializer
from zabbixproxy.tasks.template_group_creation import template_group_creation_workflow


class TemplateGroupView(APIView):
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
        data = request.data

        required_fields = ["template_group_discription", "template_group_name"]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return Response(
                {
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if TemplateGroupMirror.objects.filter(
            template_group_name=data["template_group_name"]
        ).exists():
            return Response(
                {
                    "status": "error",
                    "message": "Template group with this name already exists. Please try again using a different name.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer = TemplateGroupSerializer(data=data)
            if not serializer.is_valid():
                return Response(
                    {
                        "status": "error",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            instance = serializer.save()

            try:
                auth_token = self.get_zabbix_auth_token()
                task = template_group_creation_workflow.delay(
                    api_url=self.api_url,
                    auth_token=auth_token,
                    template_group_name=instance.template_group_name,
                )
                return Response(
                    {
                        "status": "success",
                        "message": "Template group creation started.",
                        "task_id": task.id,
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

            except ServiceErrorHandler as e:
                django_logger.error(f"Zabbix service error: {str(e)}")
                return Response(
                    {
                        "status": "error",
                        "message": "Zabbix service issue. Please try again later.",
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        except Exception as e:
            django_logger.exception(f"Unexpected error: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong. Please try again.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
