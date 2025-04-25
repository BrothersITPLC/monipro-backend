import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import TeamUserSerializer

django_logger = logging.getLogger("django")


class GetTeamUsersView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamUserSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_admin:
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to view team users.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if not user.organization:
            return Response(
                {
                    "status": "error",
                    "message": "You are not part of any organization to make this request.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            team_users = User.objects.filter(organization=user.organization).exclude(
                id=user.id
            )
            serializer = self.serializer_class(team_users, many=True)
            return Response(
                {
                    "status": "success",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            django_logger.error(f"Error fetching team users: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": "somthing went wrong while fetching team users please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
