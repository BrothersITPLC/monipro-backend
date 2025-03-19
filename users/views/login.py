from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.jwt import generate_access_token, generate_refresh_token

from ..serializers import LoginSerializer


class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data.get("user")
        if user is not None:
            # Get CSRF token
            csrf_token = get_token(request)

            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            if user.is_organization:
                user_data = {
                    "user_id": user.id,
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
                    # Convert PaymentPlan object to its ID or a serializable representation
                    user_data["organization_payment_plane"] = (
                        user.organization.organization_payment_plane.id
                        if user.organization.organization_payment_plane
                        else None
                    )
                    user_data["organization_name"] = user.organization.organization_name
            else:
                user_data = {
                    "user_id": user.id,
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
                    "csrf_token": csrf_token,  # Include CSRF token in response
                },
                status=status.HTTP_200_OK,
            )

            cookie_settings = settings.JWT_AUTH.get("COOKIE_SETTINGS", {})
            # Set CSRF cookie
            response.set_cookie(
                "csrftoken",
                csrf_token,
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                secure=cookie_settings.get("SECURE", False),
            )

            response.set_cookie(
                cookie_settings.get("ACCESS_TOKEN_NAME", "access_token"),
                access_token,
                httponly=cookie_settings.get("HTTPONLY", True),
                secure=cookie_settings.get("SECURE", True),
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                max_age=cookie_settings.get("ACCESS_MAX_AGE", 30),
            )
            response.set_cookie(
                cookie_settings.get("REFRESH_TOKEN_NAME", "refresh_token"),
                refresh_token,
                httponly=cookie_settings.get("HTTPONLY", True),
                secure=cookie_settings.get("SECURE", True),
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                max_age=cookie_settings.get("REFRESH_MAX_AGE", 604800),
            )
            return response
