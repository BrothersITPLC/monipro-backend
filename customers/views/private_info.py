from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.serializers import PrivateInfoViewSerializer


class PrivateInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user

        # Use the organization associated with the authenticated user
        organization = getattr(user, "organization", None)
        if not organization:
            return Response(
                {
                    "status": "error",
                    "message": "The authenticated user does not have an associated organization.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PrivateInfoViewSerializer(
            organization, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            # Mark the user as having completed their organization information
            user.is_organization_completed_information = True
            user.save()
            return Response(
                {
                    "status": "success",
                    "message": "Organization updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
