from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("***** it have reached this stage (stage 1)****")
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(
                {"status": "success", "message": "User Logout Successfully"},
                status=status.HTTP_200_OK,
            )
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            response["Access-Control-Allow-Credentials"] = "true"
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
