from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import OrganizationInfo
from .serializers import OrganizationInfoSerializer


class OrganizationInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrganizationInfoSerializer(data=request.data)

        if serializer.is_valid():
            # Get the user_id from the validated data
            user_id = serializer.validated_data.pop("user_id")

            try:
                # Get the user
                user = User.objects.get(id=user_id)

                serializer.organization_name = user.name
                # Create the organization
                organization = serializer.save()

                # Update the user's organization field
                user.organization = organization
                user.is_organization = True

                # If the organization info is complete, update the flag
                if organization.organization_name and organization.organization_phone:
                    user.is_organization_completed_information = True

                user.save()

                return Response(
                    {
                        "organization": serializer.data,
                        "message": "Organization created and user updated successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            except User.DoesNotExist:
                return Response(
                    {"error": f"User with id {user_id} does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        # Get organization_id from query params if provided
        organization_id = request.query_params.get("id")

        if organization_id:
            try:
                organization = OrganizationInfo.objects.get(id=organization_id)
                serializer = OrganizationInfoSerializer(organization)
                return Response(serializer.data)
            except OrganizationInfo.DoesNotExist:
                return Response(
                    {"error": f"Organization with id {organization_id} does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # If no id provided, return all organizations
        organizations = OrganizationInfo.objects.all()
        serializer = OrganizationInfoSerializer(organizations, many=True)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        organization_id = request.data.get("id")

        if not organization_id:
            return Response(
                {"error": "Organization ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            organization = OrganizationInfo.objects.get(id=organization_id)
        except OrganizationInfo.DoesNotExist:
            return Response(
                {"error": f"Organization with id {organization_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationInfoSerializer(
            organization, data=request.data, partial=True
        )

        if serializer.is_valid():
            # Check if user_id is in the data
            user_id = serializer.validated_data.pop("user_id", None)

            # Save the organization
            organization = serializer.save()

            # If user_id is provided, update the user's organization
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    user.organization = organization
                    user.is_organization = True

                    # If the organization info is complete, update the flag
                    if (
                        organization.organization_name
                        and organization.organization_phone
                    ):
                        user.is_organization_completed_information = True

                    user.save()
                except User.DoesNotExist:
                    return Response(
                        {"error": f"User with id {user_id} does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
