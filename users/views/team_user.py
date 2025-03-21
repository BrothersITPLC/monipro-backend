from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import TeamUserSerializer
from utils.team_user_email import send_team_user_creation_email


class TeamUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.role == "is_organization":
            return Response(
                {
                    "status": "error",
                    "message": "Only organization admins can view team members",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = User.objects.filter(
            organization=request.user.organization, role="is_team"
        )
        serializer = TeamUserSerializer(queryset, many=True)
        return Response(
            {
                "status": "success",
                "message": "Team members retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if not request.user.role == "is_organization":
            return Response(
                {
                    "status": "error",
                    "message": "Only organization admins can create team members",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data["organization"] = request.user.organization.id
        data["role"] = "is_team"

        serializer = TeamUserSerializer(data=data)
        if serializer.is_valid():
            default_password = User.objects.make_random_password()
            success, message = send_team_user_creation_email(
                email=serializer.validated_data["email"],
                name=serializer.validated_data["name"],
                organization_name=request.user.organization.name,
                default_password=default_password,
            )

            if success:
                user = serializer.save(default_password=default_password)
                return Response(
                    {
                        "status": "success",
                        "message": "Team member created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "status": "error",
                        "message": f"Failed to create team member: {message}",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {
                "status": "error",
                "message": "Invalid data provided",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
