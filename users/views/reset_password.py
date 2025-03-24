from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.password_reset_email import password_reset_email

from ..models import PasswordResetOTP, User, generate_password_reset_otp
from ..serializers import RequestPasswordResetSerializer


class RequestPasswordResetView(APIView):
    serializer_class = RequestPasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": f"Validation error {serializer.errors}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)

            # Check for existing recent OTPs
            last_otp = PasswordResetOTP.objects.filter(
                user=user, created_at__gte=timezone.now() - timedelta(minutes=5)
            ).first()

            if last_otp:
                return Response(
                    {
                        "status": "error",
                        "message": "Please wait 5 minutes before requesting another OTP.",
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            otp_code = generate_password_reset_otp(user)

            # Try to send email first
            success, message = password_reset_email(otp_code, email)

            if success:
                # Only create OTP if email was sent successfully
                PasswordResetOTP.objects.create(user=user, otp_code=otp_code)
                return Response(
                    {
                        "status": "success",
                        "message": "Password reset instructions sent to your email",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "status": "error",
                        "message": f"Failed to send email: {message}",
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "Password reset request failed due to server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
