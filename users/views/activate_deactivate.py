from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserActiveSerializer
from utils import ServiceErrorHandler

User = get_user_model()


class SetUserActiveAPIView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, format=None):
        try:
            user_id = request.data.get("id")
            is_active = request.data.get("is_active")

            if user_id is None or is_active is None:
                return Response(
                    {
                        "status": "error",
                        "message": "Both 'id' and 'is_active' are required.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": f"User with id {user_id} does not exist.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = UserActiveSerializer(
                user, data={"is_active": is_active}, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    "status": "success",
                    "message": "User activation status updated successfully.",
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

        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
