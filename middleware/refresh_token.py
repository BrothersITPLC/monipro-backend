from datetime import datetime, timezone

import jwt
from django.conf import settings
from django.urls import resolve
from django.urls.exceptions import Resolver404
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from utils.get_user_from_token import get_user_from_token


class AutoRefreshTokenMiddleware:
    """
    Middleware to automatically refresh the access token when it's expired
    and a valid refresh token is present.
    """

    EXCLUDED_URL_NAMES = {
        "password-reset-confirm",
        "verify-email",
    }

    EXCLUDED_PATHS = {
        "/api/login/",
        "/api/register",
        "/api/verify",
        "/admin/",
        "/redoc/",
        "/swagger/",
        "/api/logout/",
        "/api/organization/",
        "/api/plans/",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            url_name = resolve(request.path).url_name
        except Resolver404:
            url_name = None

        if self._should_exclude_request(request, url_name):
            return self.get_response(request)

        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not (access_token and refresh_token):
            return self.get_response(request)

        try:
            return self._process_token_refresh(request, access_token, refresh_token)
        except Exception:
            return self._create_error_response(
                "Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _should_exclude_request(self, request, url_name):
        if url_name in self.EXCLUDED_URL_NAMES:
            return True
        return any(request.path.startswith(path) for path in self.EXCLUDED_PATHS)

    def _process_token_refresh(self, request, access_token, refresh_token):
        try:
            payload = jwt.decode(
                access_token,
                settings.SIMPLE_JWT["SIGNING_KEY"],
                algorithms=[api_settings.ALGORITHM],
                options={"verify_exp": False},
            )
        except jwt.InvalidTokenError:
            return self._create_error_response(
                "Invalid access token", status.HTTP_401_UNAUTHORIZED
            )

        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            return self._create_error_response(
                "Invalid token payload", status.HTTP_401_UNAUTHORIZED
            )

        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        if exp_datetime > datetime.now(timezone.utc):
            return self.get_response(request)

        return self._refresh_access_token(request, refresh_token)

    def _refresh_access_token(self, request, refresh_token):
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            user = get_user_from_token(access_token)

            if not user:
                return self._create_error_response(
                    "User not found", status.HTTP_401_UNAUTHORIZED
                )

            # Update request with new token
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

            # Get original response
            response = self.get_response(request)

            # Set new cookies with proper expiration
            access_exp = refresh.access_token.payload["exp"]
            self._set_response_cookie(
                response, "access_token", access_token, access_exp
            )
            self._set_response_cookie(
                response, "refresh_token", str(refresh), refresh.payload["exp"]
            )

            return response

        except TokenError:
            return self._create_error_response(
                "Invalid refresh token",
                status.HTTP_401_UNAUTHORIZED,
                clear_cookies=True,
            )

    def _set_response_cookie(self, response, key, value, exp_timestamp):
        expires = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        response.set_cookie(
            key,
            value,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite="Strict",
            expires=expires,
        )

    def _create_error_response(self, message, status_code, clear_cookies=False):
        response = Response(
            {"status": "error", "message": message, "code": status_code},
            status=status_code,
        )

        if clear_cookies:
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

        return response
