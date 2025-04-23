from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UpdateProfileSerializer
from utils import ServiceErrorHandler


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        if not user:
            return Response(
                {
                    "status": "error",
                    "message": "User profile not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UpdateProfileSerializer(
            instance=user, data=request.data, partial=True
        )

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "User profile updated successfully",
                    },
                    status=status.HTTP_200_OK,
                )
        except ServiceErrorHandler as e:
            return Response(
                {
                    "status": "error",
                    "message": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"Unexpected error: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
