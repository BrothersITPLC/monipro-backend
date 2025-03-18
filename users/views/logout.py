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
        response.delete_cookie(cookie_settings.get("ACCESS_TOKEN_NAME", "access_token"))
        response.delete_cookie(
            cookie_settings.get("REFRESH_TOKEN_NAME", "refresh_token")
        )
        return response
