from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import VM
from infrastructures.serializers import VMSerializer

User = get_user_model()


class VMInfoAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get all VMs information",
        operation_description="Admin endpoint to retrieve all VMs with their owner details",
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "VM information retrieved successfully",
                        "data": [
                            {
                                "vm_details": {
                                    "id": 1,
                                    "domainName": "example.com",
                                    "username": "admin",
                                    "password": "********",
                                    "ipAddress": "192.168.1.100",
                                    "networkType": "private",
                                },
                                "owner_details": {
                                    "id": 1,
                                    "username": "owner_username",
                                    "email": "owner@example.com",
                                },
                            }
                        ],
                    }
                },
            ),
        },
    )
    def get(self, request, format=None):
        vms = VM.objects.all().select_related("belong_to")

        vm_data = []
        for vm in vms:
            vm_serializer = VMSerializer(vm)
            owner = vm.belong_to
            owner_data = {
                "id": owner.id,
                "username": owner.name,
                "email": owner.email,
            }

            vm_data.append(
                {
                    "vm_details": vm_serializer.data,
                    "owner_details": owner_data,
                }
            )

        return Response(
            {
                "status": "success",
                "message": "VM information retrieved successfully",
                "data": vm_data,
            },
            status=status.HTTP_200_OK,
        )
