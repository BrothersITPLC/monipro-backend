from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import LogoutSerializer


class Logout(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"status": "success", "message": "User Logout Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "success",
                "message": f"User Logout Was Unsuccessfully{serializer.errors}",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
