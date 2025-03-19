import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from jwt import ExpiredSignatureError
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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

        # CSRF check for non-safe HTTP methods
        if request.method not in ("GET", "HEAD", "OPTIONS", "TRACE"):
            csrf_token = request.headers.get("X-CSRFToken") or request.COOKIES.get(
                "csrftoken"
            )
            if (
                not csrf_token
                or not request.META.get("CSRF_COOKIE")
                or csrf_token != request.META.get("CSRF_COOKIE")
            ):
                return JsonResponse(
                    {"error": "CSRF verification failed. Request aborted."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        access_token = request.COOKIES.get(self.access_token_name)
        refresh_token = request.COOKIES.get(self.refresh_token_name)
        new_access_token = None

        if access_token:
            try:
                # Decode to check expiration, but let Simple JWT validate fully
                jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
            except ExpiredSignatureError:
                if refresh_token:
                    try:
                        # Validate refresh token and generate new access token
                        refresh = RefreshToken(refresh_token)
                        user_id = refresh.payload.get("user_id")
                        user = User.objects.get(id=user_id)
                        new_access_token = str(refresh.access_token)
                        request.META["HTTP_AUTHORIZATION"] = (
                            f"Bearer {new_access_token}"
                        )
                    except Exception:
                        return JsonResponse(
                            {"error": "Invalid refresh token"},
                            status=status.HTTP_401_UNAUTHORIZED,
                        )
                else:
                    return JsonResponse(
                        {"error": "Access token expired and no refresh token provided"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            except Exception:
                return JsonResponse(
                    {"error": "Invalid authentication credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        response = self.get_response(request)

        # Update access token if refreshed
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
