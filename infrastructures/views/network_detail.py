from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import Network
from infrastructures.serializers import NetworkSerializer


class NetworkDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Retrieve, update, or delete a Network instance.
    """

    def get_object(self, pk):
        try:
            return Network.objects.get(pk=pk)
        except Network.DoesNotExist:
            return None

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
