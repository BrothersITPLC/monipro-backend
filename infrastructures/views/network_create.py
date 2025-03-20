from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import Network
from infrastructures.serializers import NetworkSerializer


class NetworkListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """
    List all Networks for the logged-in user or create a new Network.
    """

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
