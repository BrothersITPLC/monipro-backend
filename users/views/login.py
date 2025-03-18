from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.get_token_for_user import get_token_for_user

from ..serializers import LoginSerializer


class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Get the user from validated_data instead of authenticating again
            user = serializer.validated_data.get("user")

            # Generate token
            token = get_token_for_user(user)

            # Check if token is a dictionary (which seems to be the case)
            refresh_token = (
                token.get("refresh") if isinstance(token, dict) else token.refresh
            )
            access_token = (
                token.get("access") if isinstance(token, dict) else token.access
            )
            if user.is_organization:
                user_data = {
                    "user_name": user.name,
                    "user_email": user.email,
                    "is_organization": user.is_organization,
                    "organization_info_completed": user.is_organization_completed_information,
                }
                if user.is_organization_completed_information:
                    user_data["organization_phone"] = (
                        user.organization.organization_phone
                    )
                    user_data["organization_website"] = (
                        user.organization.organization_website
                    )
                    user_data["organization_description"] = (
                        user.organization.organization_description
                    )
                    user_data["organization_payment_plane"] = (
                        user.organization.organization_payment_plane
                    )
                    user_data["organization_name"] = (
                        user.organization.organization_name,
                    )
            else:
                user_data = {
                    "user_name": user.name,
                    "user_email": user.email,
                    "is_organization": user.is_organization,
                    "organization_info_completed": user.is_organization_completed_information,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                }
                if user.is_organization_completed_information:
                    user_data["organization_phone"] = (
                        user.organization.organization_phone
                    )
                    user_data["organization_website"] = (
                        user.organization.organization_website
                    )
                    user_data["organization_description"] = (
                        user.organization.organization_description
                    )
                    user_data["organization_payment_plane"] = (
                        user.organization.organization_payment_plane
                    )
                    user_data["organization_name"] = (
                        user.organization.organization_name,
                    )

            response = Response(
                {
                    "status": "success",
                    "message": "User Login Successfully",
                    "user_data": user_data,
                },
                status=status.HTTP_200_OK,
            )

            # Set cookies
            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=24 * 60 * 60,
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=24 * 60 * 60,
            )
            return response
