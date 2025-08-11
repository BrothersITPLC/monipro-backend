import hashlib
import hmac
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware.csrf import get_token

User = get_user_model()
logger = logging.getLogger("django")
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN


class TelegramAuthView(APIView):
    """
    Handles Telegram login authentication using Telegram Login Widget data.
    """

    def post(self, request):
        data = request.data.copy()
        received_hash = data.pop("hash", None)

        if not received_hash:
            return Response(
                {"status": "error", "message": "Missing authentication hash."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build data_check_string per Telegram docs
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

        # Calculate hash using bot token secret key
        secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # Timing-safe comparison
        if not hmac.compare_digest(calculated_hash, received_hash):
            return Response(
                {"status": "error", "message": "Invalid authentication data."},
                status=status.HTTP_403_FORBIDDEN,
            )

        telegram_id = data.get("id")
        username = data.get("username", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        photo_url = data.get("photo_url", "")
        auth_date = data.get("auth_date")

        if not telegram_id or not auth_date:
            return Response(
                {"status": "error", "message": "Missing required Telegram user data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Optional: Check auth_date freshness (e.g., within 1 day)
        import time
        if abs(time.time() - int(auth_date)) > 86400:
            return Response(
                {"status": "error", "message": "Authentication data is too old."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Find or create user
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "name": username,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
                "is_verified": True,
                "is_from_social": True,
                "profile_photo_url": photo_url,  # if you have this field
            },
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        action = "signup" if created else "login"
        csrf_token = get_token(request)

        response = Response(
            {
                "status": "success",
                "message": f"Telegram {action} successful",
                "csrf_token": csrf_token,
            },
            status=status.HTTP_200_OK,
        )

        cookie_settings = settings.JWT_AUTH.get("COOKIE_SETTINGS", {})

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
            max_age=cookie_settings.get("ACCESS_MAX_AGE", 604800),
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
