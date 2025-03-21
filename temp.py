from django.conf import settings
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers import LoginSerializer


class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data.get("user")

            if user is not None:
                # Generate tokens using Simple JWT
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                # Get CSRF token
                csrf_token = get_token(request)

                response = Response(
                    {
                        "status": "success",
                        "message": "User Login Successfully",
                        "user_id": user.id,
                        "csrf_token": csrf_token,
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

                # Set access and refresh tokens in cookies
                response.set_cookie(
                    cookie_settings.get("ACCESS_TOKEN_NAME", "access_token"),
                    access_token,
                    httponly=cookie_settings.get("HTTPONLY", True),
                    secure=cookie_settings.get("SECURE", True),
                    samesite=cookie_settings.get("SAMESITE", "Lax"),
                    max_age=cookie_settings.get("ACCESS_MAX_AGE", 300),
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
