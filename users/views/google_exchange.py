# google_exchange.py
import requests
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class GoogleExchangeView(APIView):
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Authorization code missing"}, status=400)

        try:
            app = SocialApp.objects.get(provider="google")
            client_id = app.client_id
            client_secret = app.secret
        except SocialApp.DoesNotExist:
            client_id = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"]
            client_secret = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["secret"]

        # Use the frontend redirect URI
        redirect_uri = settings.REDIRECT_URL

        token_url = "https://oauth2.googleapis.com/token"
        token_payload = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        try:
            token_response = requests.post(token_url, data=token_payload)
            token_data = token_response.json()

            if "error" in token_data:
                return Response({"error": token_data["error"]}, status=400)

            access_token = token_data.get("access_token")
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            user_info_response = requests.get(
                user_info_url, headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info = user_info_response.json()

            email = user_info.get("email")
            if not email:
                return Response({"error": "Email not provided by Google"}, status=400)

            # Get name from Google response
            full_name = user_info.get("name", "")
            first_name = user_info.get("given_name", "")
            last_name = user_info.get("family_name", "")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                    "is_verified": True,
                },
            )

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            action = "signup" if created else "login"

            # Get CSRF token
            from django.middleware.csrf import get_token

            csrf_token = get_token(request)

            # Prepare user data similar to login.py
            if user.role == "is_organization":
                user_data = {
                    "user_id": user.id,
                    "user_name": user.name,
                    "user_email": user.email,
                    "is_organization": True,
                    "is_private": user.is_private
                    if user.role == "is_organization"
                    else False,
                    "organization_info_completed": bool(
                        user.is_organization_completed_information
                    ),
                }
                if user.is_organization_completed_information and user.organization:
                    user_data["organization_id"] = user.organization.id
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
                        user.organization.organization_payment_plane.name
                    )
                    user_data["organization_payment_duration"] = (
                        user.organization.organization_payment_duration.name
                    )
                    user_data["organization_name"] = user.organization.organization_name
            else:
                user_data = {
                    "user_id": user.id,
                    "user_name": user.name,
                    "user_email": user.email,
                    "is_organization": True
                    if user.role == "is_organization"
                    else False,
                    "organization_info_completed": user.is_organization_completed_information,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                }
                if user.is_organization_completed_information and user.organization:
                    user_data["organization_id"] = user.organization.id
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
                        user.organization.organization_payment_plane.name
                    )
                    user_data["organization_payment_duration"] = (
                        user.organization.organization_payment_duration.name
                    )
                    user_data["organization_name"] = user.organization.organization_name

            response = Response(
                {
                    "status": "success",
                    "message": f"Google {action} successful",
                    "user_data": user_data,
                    "csrf_token": csrf_token,
                },
                status=status.HTTP_200_OK,
            )

            # Set cookies using the same settings as in login.py
            cookie_settings = settings.JWT_AUTH.get("COOKIE_SETTINGS", {})

            # Set CSRF cookie
            response.set_cookie(
                "csrftoken",
                csrf_token,
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                secure=cookie_settings.get("SECURE", False),
            )

            # Set access and refresh tokens in cookies
            response.set_cookie(
                cookie_settings.get("ACCESS_TOKEN_NAME", "access_token"),
                access_token,
                httponly=cookie_settings.get("HTTPONLY", True),
                secure=cookie_settings.get("SECURE", True),
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                max_age=cookie_settings.get("ACCESS_MAX_AGE", 60480),
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

        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"Error {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
