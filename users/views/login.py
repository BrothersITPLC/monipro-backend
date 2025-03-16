from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.get_token_for_user import get_token_for_user

from ..serializers import LoginSerializer


class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Get the user from validated_data instead of authenticating again
            user = serializer.validated_data.get("user")

            # Generate token
            token = get_token_for_user(user)

            # Check if token is a dictionary (which seems to be the case)
            refresh_token = (
                token.get("refresh") if isinstance(token, dict) else token.refresh
            )
            access_token = (
                token.get("access") if isinstance(token, dict) else token.access
            )

            response = Response(
                {
                    "status": "success",
                    "message": "User Login Successfully",
                    "user_data": {
                        "user_name": user.name,
                        "user_email": user.email,
                    },
                },
                status=status.HTTP_200_OK,
            )

            # Set cookies
            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=24 * 60 * 60,
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=True,
                samesite="None",
                max_age=24 * 60 * 60,
            )
            return response
