from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class Logout(APIView):
    def post(self, request):
        response = Response(
            {"status": "success", "message": "User Logout Successfully"},
            status=status.HTTP_200_OK,
        )
        cookie_settings = settings.JWT_AUTH.get("COOKIE_SETTINGS", {})

        # Delete cookies with proper parameters
        for cookie_name in ["ACCESS_TOKEN_NAME", "REFRESH_TOKEN_NAME"]:
            response.delete_cookie(
                cookie_settings.get(cookie_name, cookie_name.lower()),
                path="/",
                domain=None,
                samesite=cookie_settings.get("SAMESITE", "Lax"),
            )

        return response
