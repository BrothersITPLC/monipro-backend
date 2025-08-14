import logging
import hashlib
import hmac
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
django_logger = logging.getLogger("django")


class Telegram_Auth(APIView):
    permission_classes = []  # Public endpoint

    def post(self, request):
        try:
            data = request.data
            if not data:
                return Response(
                    {"status": "error", "message": "No data provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract hash & validate
            auth_data = dict(data)
            received_hash = auth_data.pop("hash", None)

            # Hash validation (must use original values including "id")
            secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
            check_string = "\n".join(f"{k}={v}" for k, v in sorted(auth_data.items()))
            calculated_hash = hmac.new(
                secret_key, check_string.encode(), hashlib.sha256
            ).hexdigest()

            if calculated_hash != received_hash:
                return Response(
                    {"status": "error", "message": "Invalid Telegram data"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Expiry check
            auth_date = int(data.get("auth_date", 0))
            if time.time() - auth_date > 86400:  # 24 hours
                return Response(
                    {"status": "error", "message": "Login request too old"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Telegram fields
            telegram_id = data.get("id")
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            username = data.get("username", "")
            photo_url = data.get("photo_url")

            if not telegram_id:
                return Response(
                    {"status": "error", "message": "Missing Telegram ID"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get/create user
            user, created = User.objects.get_or_create(
                telegram_id=str(telegram_id),
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "name": f"{first_name} {last_name}".strip() or username,
                    "is_from_social": True,
                    "is_verified": True,
                    "profile_photo_url": photo_url,
                },
            )

            if not created and photo_url and user.profile_photo_url != photo_url:
                user.profile_photo_url = photo_url
                user.save()

            action = "signup" if created else "login"

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Get CSRF token
            csrf_token = get_token(request)

            # Prepare response
            response = Response(
                {
                    "status": "success",
                    "message": f"Telegram {action} successful",
                    "csrf_token": csrf_token,
                },
                status=status.HTTP_200_OK,
            )

            # Cookie settings (same as Google/GitHub)
            cookie_settings = settings.JWT_AUTH.get("COOKIE_SETTINGS", {})

            # CSRF cookie
            response.set_cookie(
                "csrftoken",
                csrf_token,
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                secure=cookie_settings.get("SECURE", False),
            )

            # Access & refresh cookies
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
            django_logger.error(f"Error during Telegram login: {e}", exc_info=True)
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
