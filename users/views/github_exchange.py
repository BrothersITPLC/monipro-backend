# github_exchange.py
import logging

import requests
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
logger = logging.getLogger("django")


class GitHubExchangeView(APIView):
    def post(self, request):
        code = request.data.get("code")
        if not code:
            logger.error("Authorization code missing in GitHub exchange request.")
            return Response(
                {"status": "error", "message": "Authorization code missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Try SocialApp first (if you use django-allauth admin to store client id/secret)
            try:
                app = SocialApp.objects.get(provider="github")
                client_id = app.github_client_id
                client_secret = app.github_client_secret

            except SocialApp.DoesNotExist:
                # Fallback to settings (if you store in settings.SOCIALACCOUNT_PROVIDERS)
                client_id = settings.SOCIALACCOUNT_PROVIDERS["github"]["app"][
                    "github_client_id"
                ]
                client_secret = settings.SOCIALACCOUNT_PROVIDERS["github"]["app"][
                    "github_client_secret"
                ]

            if not client_id or not client_secret:
                logger.error("GitHub client_id/secret not found.")
                return Response(
                    {
                        "status": "error",
                        "message": "Server misconfigured for GitHub OAuth.",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            redirect_uri = settings.SOCIALACCOUNT_PROVIDERS["github"][
                "github_redirect_url"
            ]

            # Exchange code for access token (request JSON response)
            token_url = "https://github.com/login/oauth/access_token"
            token_payload = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            }
            token_resp = requests.post(
                token_url, data=token_payload, headers={"Accept": "application/json"}
            )
            token_data = token_resp.json()
            logger.info(f"GitHub token response: {token_data}")

            if token_data.get("error"):
                logger.error("GitHub token error: %s", token_data)
                return Response(
                    {
                        "status": "error",
                        "message": "Failed to exchange code for token with GitHub.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            access_token = token_data.get("access_token")
            if not access_token:
                logger.error("No access_token in GitHub token response.")
                return Response(
                    {
                        "status": "error",
                        "message": "No access token received from GitHub.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Fetch user profile
            user_info_url = "https://api.github.com/user"
            headers = {
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github+json",
            }
            user_info_resp = requests.get(user_info_url, headers=headers)
            user_info = user_info_resp.json()
            logger.info(f"GitHub user info: {user_info}")

            email = user_info.get("email")
            # If email is null (common), fetch /user/emails (requires user:email scope)
            if not email:
                emails_resp = requests.get(
                    "https://api.github.com/user/emails", headers=headers
                )
                try:
                    emails = emails_resp.json()
                except Exception:
                    emails = []
                # find primary & verified email first, otherwise first verified
                primary_email = None
                for e in emails:
                    if e.get("primary") and e.get("verified"):
                        primary_email = e.get("email")
                        break
                if not primary_email:
                    for e in emails:
                        if e.get("verified"):
                            primary_email = e.get("email")
                            break
                email = primary_email

            if not email:
                return Response(
                    {
                        "status": "error",
                        "message": "No email provided by GitHub. Ask user to make email available or request user:email scope.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # create or get user
            full_name = user_info.get("name") or ""
            given_name = full_name.split(" ")[0] if full_name else ""
            last_name = (
                " ".join(full_name.split(" ")[1:])
                if full_name and len(full_name.split(" ")) > 1
                else ""
            )

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": full_name,
                    "first_name": given_name,
                    "last_name": last_name,
                    "is_active": True,
                    "is_admin": True,
                    "is_verified": True,
                    "is_from_social": True,
                },
            )

            refresh = RefreshToken.for_user(user)
            access_jwt = str(refresh.access_token)
            refresh_jwt = str(refresh)

            # Prepare response
            from django.middleware.csrf import get_token

            csrf_token = get_token(request)

            response = Response(
                {
                    "status": "success",
                    "message": "GitHub authentication successful",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "organization_info_completed": getattr(
                            user, "organization_info_completed", False
                        ),
                        "user_have_completed_payment": getattr(
                            user, "user_have_completed_payment", None
                        ),
                    },
                },
                status=status.HTTP_200_OK,
            )

            # set cookies (reuse the same JWT_AUTH cookie settings you used for Google)
            cookie_settings = settings.JWT_AUTH.get("COOKIE_SETTINGS", {})

            response.set_cookie(
                "csrftoken",
                csrf_token,
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                secure=cookie_settings.get("SECURE", False),
            )
            response.set_cookie(
                cookie_settings.get("ACCESS_TOKEN_NAME", "access_token"),
                access_jwt,
                httponly=cookie_settings.get("HTTPONLY", True),
                secure=cookie_settings.get("SECURE", True),
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                max_age=cookie_settings.get("ACCESS_MAX_AGE", 60480),
            )
            response.set_cookie(
                cookie_settings.get("REFRESH_TOKEN_NAME", "refresh_token"),
                refresh_jwt,
                httponly=cookie_settings.get("HTTPONLY", True),
                secure=cookie_settings.get("SECURE", True),
                samesite=cookie_settings.get("SAMESITE", "Lax"),
                max_age=cookie_settings.get("REFRESH_MAX_AGE", 604800),
            )

            return response

        except Exception as e:
            logger.exception("Error during GitHub token exchange: %s", e)
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong. Please try again later.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
