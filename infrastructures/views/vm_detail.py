from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import VM
from infrastructures.serializers import VMSerializer


class VMDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return VM.objects.get(pk=pk, belong_to=self.request.user)
        except VM.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Get VM details",
        operation_description="Retrieve details of a specific VM by ID",
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="VM ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "VM retrieved successfully",
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
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "VM not found",
                        "data": {},
                    }
                },
            ),
        },
    )
    def get(self, request, pk, format=None):
        vm = self.get_object(pk)
        if vm is None:
            return Response(
                {
                    "status": "error",
                    "message": "VM not found",
                    "data": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = VMSerializer(vm)
        return Response(
            {
                "status": "success",
                "message": "VM retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Update VM",
        operation_description="Update an existing VM by ID",
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="VM ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
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
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "VM updated successfully",
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
                        "message": "Error updating VM",
                        "data": {"field_name": ["error message"]},
                    }
                },
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "VM not found",
                        "data": {},
                    }
                },
            ),
        },
    )
    def put(self, request, pk, format=None):
        vm = self.get_object(pk)
        if vm is None:
            return Response(
                {
                    "status": "error",
                    "message": "VM not found",
                    "data": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = VMSerializer(vm, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "VM updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Error updating VM",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        operation_summary="Delete VM",
        operation_description="Delete a specific VM by ID",
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="VM ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "VM deleted successfully",
                        "data": {},
                    }
                },
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "VM not found",
                        "data": {},
                    }
                },
            ),
        },
    )
    def delete(self, request, pk, format=None):
        vm = self.get_object(pk)
        if vm is None:
            return Response(
                {
                    "status": "error",
                    "message": "VM not found",
                    "data": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        vm.delete()
        return Response(
            {
                "status": "success",
                "message": "VM deleted successfully",
                "data": {},
            },
            status=status.HTTP_200_OK,
        )
