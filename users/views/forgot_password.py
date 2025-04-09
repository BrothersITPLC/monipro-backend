from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import PasswordResetOTP, generate_password_reset_otp
from users.serializers import PasswordForgotSerializer
from utils import ServiceErrorHandler
from utils.password_reset_email import password_reset_email


class ForgotPasswordView(APIView):
    def post(self, request):
        try:
            # Validate input data
            serializer = PasswordForgotSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.context['user']
            
            # Check rate limit (5 minutes between requests)
            if PasswordResetOTP.objects.filter(
                user=user, 
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).exists():
                raise ServiceErrorHandler("Please wait 5 minutes before requesting another OTP")

            # Generate and send OTP
            otp_code = generate_password_reset_otp(user)
            success, message = password_reset_email(otp_code, user.email)
            
            if not success:
                raise ServiceErrorHandler(f"Email sending failed: {message}")

            # Create OTP record only after successful email send
            PasswordResetOTP.objects.create(user=user, otp_code=otp_code)
            
            return Response(
                {
                    "status": "success",
                    "message": "Password reset instructions sent to your email"
                },
                status=status.HTTP_200_OK
            )

        except ServiceErrorHandler as e:
            # Message-based status code mapping
            message = str(e)
            status_code = status.HTTP_400_BAD_REQUEST
            
            if "wait 5 minutes" in message:
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif "email failed" in message:
                status_code = status.HTTP_502_BAD_GATEWAY
                
            return Response(
                {"status": "error", "message": message},
                status=status_code
            )
            
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred. Please try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )