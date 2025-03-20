from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import VM
from infrastructures.serializers import VMSerializer


class VMListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List VMs",
        operation_description="Returns a list of all VMs belonging to the authenticated user",
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "VM list retrieved successfully",
                        "data": [
                            {
                                "id": 1,
                                "domainName": "example.com",
                                "username": "admin",
                                "password": "********",
                                "ipAddress": "192.168.1.100",
                                "networkType": "private",
                                "belong_to": 1,
                            }
                        ],
                    }
                },
            )
        },
    )
    def get(self, request, format=None):
        vms = VM.objects.filter(belong_to=request.user)
        serializer = VMSerializer(vms, many=True)
        return Response(
            {
                "status": "success",
                "message": "VM list retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Create VM",
        operation_description="Create a new VM for the authenticated user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["domainName", "username", "password", "ipAddress", "networkType"],
            properties={
                "domainName": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Domain name of the VM",
                    max_length=255,
                ),
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Username for VM access",
                    max_length=150,
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Password for VM access",
                    max_length=128,
                    format="password",
                ),
                "ipAddress": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="ipv4",
                    description="IPv4/IPv6 address of the VM",
                ),
                "networkType": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["private", "public"],
                    description="Network type",
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "VM created successfully",
                        "data": {
                            "id": 1,
                            "domainName": "example.com",
                            "username": "admin",
                            "password": "********",
                            "ipAddress": "192.168.1.100",
                            "networkType": "private",
                            "belong_to": 1,
                        },
                    }
                },
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Error creating VM",
                        "data": {"field_name": ["error message"]},
                    }
                },
            ),
        },
    )
    def post(self, request, format=None):
        serializer = VMSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(belong_to=request.user)
            return Response(
                {
                    "status": "success",
                    "message": "VM created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "error",
                "message": "Error creating VM",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
