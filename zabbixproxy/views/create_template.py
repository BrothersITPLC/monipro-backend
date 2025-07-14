import logging

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from zabbixproxy.functions.credentials_functions import zabbix_login

django_logger = logging.getLogger("django")

from utils import ServiceErrorHandler
from zabbixproxy.models import TemplateGroupMirror, TemplateMirror
from zabbixproxy.serializers import TemplateSerializer
from zabbixproxy.tasks.template_creation import template_creation_workflow


class TemplateView(APIView):
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
        """Creating a template in zabbix and the in local database"""
        template_data = request.data

        required_fields = ["template_description", "template_name", "template_group_id"]
        missing = [field for field in required_fields if not template_data.get(field)]
        if missing:
            return Response(
                {
                    "status": "error",
                    "message": f"The following fields are required: {', '.join(missing)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if TemplateMirror.objects.filter(
            template_name=template_data["template_name"]
        ).exists():
            return Response(
                {
                    "status": "error",
                    "message": "Template with this name already exists, please try again using a different name",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            template_group_instance = TemplateGroupMirror.objects.get(
                template_group_id=template_data["template_group_id"]
            )
        except TemplateGroupMirror.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Template group with this id does not exists, please tray again",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer = TemplateSerializer(
                data={
                    "template_name": template_data["template_name"],
                    "template_description": template_data["template_description"],
                    "template_group": template_group_instance.pk,
                }
            )

            if not serializer.is_valid():
                return Response(
                    {"status": "error", "message": "Invalid data provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            auth_token = self.get_zabbix_auth_token()
            workflow_task = template_creation_workflow.delay(
                api_url=self.api_url,
                auth_token=auth_token,
                template_group_id=template_data["template_group_id"],
                template_name=template_data["template_name"],
            )
            return Response(
                {
                    "status": "success",
                    "message": "Template creation started, you will get notified after 2 minutes",
                },
                status=status.HTTP_202_ACCEPTED,
            )
        except ServiceErrorHandler as e:
            django_logger.error(f"Error creating Zabbix Template: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": f"somthing went wrong, please try again",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            django_logger.exception(f"Error creating Zabbix Template: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": f"somthing went wrong, please try again",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
