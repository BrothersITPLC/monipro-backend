# myproject/middleware.py
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from jwt import ExpiredSignatureError

from utils.jwt import generate_access_token

User = get_user_model()


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        jwt_settings = getattr(settings, "JWT_AUTH", {})
        self.excluded_url_names = jwt_settings.get("EXCLUDED_URL_NAMES", [])
        self.excluded_paths = jwt_settings.get("EXCLUDED_PATHS", [])
        cookie_settings = jwt_settings.get("COOKIE_SETTINGS", {})
        self.access_token_name = cookie_settings.get(
            "ACCESS_TOKEN_NAME", "access_token"
        )
        self.refresh_token_name = cookie_settings.get(
            "REFRESH_TOKEN_NAME", "refresh_token"
        )

    def __call__(self, request):
        # Skip authentication if URL is excluded by name or exact path.
        if request.path in self.excluded_paths or (
            hasattr(request, "resolver_match")
            and request.resolver_match
            and request.resolver_match.url_name in self.excluded_url_names
        ):
            return self.get_response(request)

        access_token = request.COOKIES.get(self.access_token_name)
        refresh_token = request.COOKIES.get(self.refresh_token_name)
        new_access_token = None

        if access_token:
            try:
                payload = jwt.decode(
                    access_token, settings.SECRET_KEY, algorithms=["HS256"]
                )
                user_id = payload.get("user_id")
                user = User.objects.get(id=user_id)
                request.user = user
            except ExpiredSignatureError:
                # If access token expired, try using the refresh token
                if refresh_token:
                    try:
                        payload = jwt.decode(
                            refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
                        )
                        user_id = payload.get("user_id")
                        user = User.objects.get(id=user_id)
                        new_access_token = generate_access_token(user)
                        request.user = user
                    except ExpiredSignatureError:
                        return JsonResponse(
                            {"error": "Refresh token expired. Please log in again."},
                            status=401,
                        )
                    except Exception:
                        return JsonResponse(
                            {"error": "Invalid refresh token."}, status=401
                        )
                else:
                    return JsonResponse(
                        {
                            "error": "Access token expired and no refresh token provided."
                        },
                        status=401,
                    )
            except Exception:
                return JsonResponse({"error": "Invalid access token."}, status=401)
        else:
            return JsonResponse(
                {"error": "Authentication credentials were not provided."}, status=401
            )

        response = self.get_response(request)

        # If a new access token was generated, set it as an HTTP-only cookie.
        if new_access_token:
            cookie_settings = settings.JWT_AUTH.get("COOKIE_SETTINGS", {})
            response.set_cookie(
                self.access_token_name,
                new_access_token,
                httponly=cookie_settings.get("HTTPONLY", True),
                secure=cookie_settings.get("SECURE", True),
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                max_age=cookie_settings.get("ACCESS_MAX_AGE", 300),
            )
        return response
