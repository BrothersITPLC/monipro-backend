# views.py
import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

django_logger = logging.getLogger("django")
from users.serializers import UserProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserProfileSerializer(
                request.user, context={"request": request}
            )

            return Response(
                {
                    "status": "success",
                    "message": "User profile retrieved successfully",
                    "user_data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except AttributeError as e:
            django_logger.error(f"Attribute error retrieving user profile: {e}")
            print(f"Error: {e}")
            return Response(
                {
                    "status": "error",
                    "message": "User profile not found",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            django_logger.error(f"Unexpected error retrieving user profile: {e}")
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred while retrieving the profile",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
