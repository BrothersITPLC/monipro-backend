from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import Network
from infrastructures.serializers import NetworkSerializer

User = get_user_model()


class NetworkInfoAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get all Networks information",
        operation_description="Endpoint to retrieve all Networks with their owner details",
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Network information retrieved successfully",
                        "data": [
                            {
                                "network_details": {
                                    "id": 1,
                                    "networkType": "private",
                                    "deviceType": "router",
                                    "ipAddress": "192.168.1.1",
                                    "subnetMask": "255.255.255.0",
                                    "gateway": "192.168.1.1",
                                    "name": "Main Router",
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
        networks = Network.objects.all().select_related("belong_to")

        network_data = []
        for network in networks:
            network_serializer = NetworkSerializer(network)
            owner = network.belong_to
            owner_data = {
                "id": owner.id,
                "username": owner.name,
                "email": owner.email,
            }

            network_data.append(
                {
                    "network_details": network_serializer.data,
                    "owner_details": owner_data,
                }
            )

        return Response(
            {
                "status": "success",
                "message": "Network information retrieved successfully",
                "data": network_data,
            },
            status=status.HTTP_200_OK,
        )
