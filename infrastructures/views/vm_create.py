from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import VM
from infrastructures.serializers import VMSerializer


class VMListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """
    List all VMs for the logged-in user or create a new VM.
    """

    def get(self, request, format=None):
        # Return only VMs belonging to the current user
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

    def post(self, request, format=None):
        serializer = VMSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically set belong_to to the current user
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
