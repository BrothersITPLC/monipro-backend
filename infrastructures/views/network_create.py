from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import Network
from infrastructures.serializers import NetworkSerializer


class NetworkListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List networks",
        operation_description="Returns a list of all networks belonging to the authenticated user",
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Network list retrieved successfully",
                        "data": [
                            {
                                "id": 1,
                                "networkType": "private",
                                "deviceType": "router",
                                "ipAddress": "192.168.1.1",
                                "subnetMask": "255.255.255.0",
                                "gateway": "192.168.1.1",
                                "name": "Main Router",
                                "belong_to": 1,
                            }
                        ],
                    }
                },
            )
        },
    )
    def get(self, request, format=None):
        networks = Network.objects.filter(belong_to=request.user)
        serializer = NetworkSerializer(networks, many=True)
        return Response(
            {
                "status": "success",
                "message": "Network list retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Create network",
        operation_description="Create a new network device for the authenticated user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "networkType",
                "deviceType",
                "ipAddress",
                "subnetMask",
                "gateway",
                "name",
            ],
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
            201: openapi.Response(
                description="Created",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Network created successfully",
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
                        "message": "Error creating Network",
                        "data": {"field_name": ["error message"]},
                    }
                },
            ),
        },
    )
    def post(self, request, format=None):
        serializer = NetworkSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically set belong_to to the current user
            serializer.save(belong_to=request.user)
            return Response(
                {
                    "status": "success",
                    "message": "Network created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status": "error",
                "message": "Error creating Network",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
