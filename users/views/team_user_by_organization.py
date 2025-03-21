from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import TeamUserByOrganizationSerializer


class TeamUserByOrganizationView(APIView):
    """
    API View to get team users by organization ID
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get team users by organization ID
        """
        organization_id = request.query_params.get("organization_id")
        if not organization_id:
            return Response(
                {
                    "status": "error",
                    "message": "Organization ID is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user has permission to view this organization's team members
        if (
            request.user.role != "is_organization"
            or str(request.user.organization.id) != organization_id
        ):
            return Response(
                {
                    "status": "error",
                    "message": "You don't have permission to view these team members",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = User.objects.filter(organization_id=organization_id, role="is_team")
        serializer = TeamUserByOrganizationSerializer(queryset, many=True)

        return Response(
            {
                "status": "success",
                "message": "Team members retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
