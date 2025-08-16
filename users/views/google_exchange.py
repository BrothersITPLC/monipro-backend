# google_exchange.py
import logging

import requests
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from django.core.files.base import ContentFile
import os

User = get_user_model()
django_logger = logging.getLogger("django")


class GoogleExchangeView(APIView):
    def post(self, request):
        code = request.data.get("code")
        if not code:
            django_logger.error("Authorization code is missing in the request.")
            return Response(
                {"status": "error", "message": "Authorization code missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            app = SocialApp.objects.get(provider="google")
            client_id = app.google_client_id
            client_secret = app.google_client_secret

        except SocialApp.DoesNotExist:
            client_id = settings.SOCIALACCOUNT_PROVIDERS["google"]["app"][
                "google_client_id"
            ]
            client_secret = settings.SOCIALACCOUNT_PROVIDERS["google"]["app"][
                "google_client_secret"
            ]

        redirect_uri = settings.SOCIALACCOUNT_PROVIDERS["google"]["google_redirect_url"]

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

            django_logger.info(f"Token response: {token_data}")

            if "error" in token_data:
                django_logger.error(f"Error in token response: {token_data['error']}")
                return Response(
                    {
                        "status": "error",
                        "message": "somthing went wrong while autenticating with google please try again",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            access_token = token_data.get("access_token")
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            user_info_response = requests.get(
                user_info_url, headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info = user_info_response.json()
            print(user_info)

            email = user_info.get("email")
            if not email:
                return Response(
                    {
                        "status": "error",
                        "message": "user information is not provided by Google,please try again",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_data_for_checking = User.objects.filter(email=email).first()
            if user_data_for_checking and not user_data_for_checking.is_from_social:
                return Response(
                    {
                        "status": "error",
                        "message": "Email already registered, please try with another Google account.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get name from Google response
            full_name = user_info.get("name", "")
            first_name = user_info.get("given_name", "")
            last_name = user_info.get("family_name", "")

            profile_picture_url = user_info.get("picture", "")


            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": full_name,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                    "is_admin": True,
                    "is_verified": True,
                    "is_from_social": True
                },
            )

            
            if created and profile_picture_url:
                img_response = requests.get(profile_picture_url)
                if img_response.status_code == 200:
                    file_name = f"{first_name}_{last_name}_{email}.jpg"
                    user.profile_picture.save(file_name, ContentFile(img_response.content), save=True)


            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            action = "signup" if created else "login"

            # Get CSRF token
            from django.middleware.csrf import get_token

            csrf_token = get_token(request)

            # Prepare user data similar to login.py

            response = Response(
                {
                    "status": "success",
                    "message": f"Google {action} successful",
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
            django_logger.error(f"Error during Google token exchange: {e}")
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
