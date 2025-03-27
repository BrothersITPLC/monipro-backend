# Add this class to the existing file
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import PasswordResetSerializer


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get validated data
        user = serializer.validated_data.get("user")
        otp_instance = serializer.validated_data.get("otp_instance")
        # Fix: Use "password" instead of "new_password"
        password = serializer.validated_data.get("password")

        try:
            # Mark OTP as used
            otp_instance.is_used = True
            otp_instance.save()

            # Set the new password
            user.set_password(password)
            user.save()

            return Response(
                {
                    "status": "success",
                    "message": "Password has been reset successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"Password reset failed due to server error: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
