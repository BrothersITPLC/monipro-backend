from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import Network
from infrastructures.serializers import NetworkSerializer


class NetworkDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Network.objects.get(pk=pk, belong_to=self.request.user)
        except Network.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Get network details",
        operation_description="Retrieve details of a specific network by ID",
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="Network ID",
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
                        "message": "Network retrieved successfully",
                        "data": {
                            "id": 1,
                            "networkType": "private",
                            "deviceType": "router",
                            "ipAddress": "192.168.1.1",
                            "subnetMask": "255.255.255.0",
                            "gateway": "192.168.1.1",
                            "name": "Main Router",
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
                        "message": "Network not found",
                        "data": {},
                    }
                },
            ),
        },
    )
    def get(self, request, pk, format=None):
        network = self.get_object(pk)
        if network is None:
            return Response(
                {
                    "status": "error",
                    "message": "Network not found",
                    "data": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = NetworkSerializer(network)
        return Response(
            {
                "status": "success",
                "message": "Network retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Update network",
        operation_description="Update an existing network by ID",
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="Network ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "networkType": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["private", "public"],
                    description="Network type",
                ),
                "deviceType": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["router", "firewall", "switch", "load_balancer"],
                    description="Device type",
                ),
                "ipAddress": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="ipv4",
                    description="IPv4/IPv6 address",
                ),
                "subnetMask": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Subnet mask (e.g., 255.255.255.0)",
                ),
                "gateway": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="ipv4",
                    description="Gateway IPv4/IPv6 address",
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Network device name"
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Network updated successfully",
                        "data": {
                            "id": 1,
                            "networkType": "private",
                            "deviceType": "router",
                            "ipAddress": "192.168.1.1",
                            "subnetMask": "255.255.255.0",
                            "gateway": "192.168.1.1",
                            "name": "Main Router",
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
                        "message": "Error updating Network",
                        "data": {"field_name": ["error message"]},
                    }
                },
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Network not found",
                        "data": {},
                    }
                },
            ),
        },
    )
    def put(self, request, pk, format=None):
        network = self.get_object(pk)
        if network is None:
            return Response(
                {
                    "status": "error",
                    "message": "Network not found",
                    "data": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = NetworkSerializer(network, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Network updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Error updating Network",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        operation_summary="Delete network",
        operation_description="Delete a specific network by ID",
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="Network ID",
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
                        "message": "Network deleted successfully",
                        "data": {},
                    }
                },
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Network not found",
                        "data": {},
                    }
                },
            ),
        },
    )
    def delete(self, request, pk, format=None):
        network = self.get_object(pk)
        if network is None:
            return Response(
                {
                    "status": "error",
                    "message": "Network not found",
                    "data": {},
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        network.delete()
        return Response(
            {
                "status": "success",
                "message": "Network deleted successfully",
                "data": {},
            },
            status=status.HTTP_200_OK,
        )
