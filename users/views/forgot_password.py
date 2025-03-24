from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import VerifyPasswordResetSerializer


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = VerifyPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Validation error",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get validated data
        user = serializer.validated_data.get("user")
        otp_instance = serializer.validated_data.get("otp_instance")
        new_password = serializer.validated_data.get("new_password")

        try:
            # Mark OTP as used
            otp_instance.is_used = True
            otp_instance.save()

            # Set the new password
            user.set_password(new_password)
            user.save()

            return Response(
                {
                    "status": "success",
                    "message": "Password has been reset successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "Password reset failed due to server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
