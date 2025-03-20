from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from infrastructures.models import VM
from infrastructures.serializers import VMSerializer


class VMDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Retrieve, update, or delete a VM instance.
    """

    def get_object(self, pk):
        try:
            return VM.objects.get(pk=pk)
        except VM.DoesNotExist:
            return None

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
