from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import VerifyRegistrationOtpSerializer


class VerifyRegistrationOtp(APIView):
    def post(self, request):
        serializer = VerifyRegistrationOtpSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            otp_instance = serializer.validated_data["otp_instance"]

            otp_instance.is_used = True
            otp_instance.save()

            user.is_verified = True
            user.save()

            otp_instance.refresh_from_db()
            user.refresh_from_db()

            if otp_instance.is_used and user.is_verified:
                return Response(
                    {
                        "status": "success",
                        "message": "OTP verified successfully.",
                    },
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                return Response(
                    {
                        "status": "error",
                        "message": "Failed to update OTP or user status. Please try again.",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(
            {
                "status": "error",
                "message": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
