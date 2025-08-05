import logging
from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

django_logger = logging.getLogger("django")
from utils import ServiceErrorHandler
from zabbixproxy.models import TemplateGroupMirror
from zabbixproxy.serializers import TemplateGroupMirrorSerializer


class GetTemplates(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            try:
                template_groups = TemplateGroupMirror.objects.all()
            except TemplateGroupMirror.DoesNotExist:
                raise ServiceErrorHandler("Template groups not found")

            serializer = TemplateGroupMirrorSerializer(template_groups, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Hosts retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ServiceErrorHandler as e:
            django_logger.error(f"Error retrieving template groups: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": f"An error occurred while retrieving templates",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            django_logger.error(f"Error retrieving template groups: {e}")
            return Response(
                {
                    "status": "error",
                    "message": f"An error occurred while retrieving templates",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
