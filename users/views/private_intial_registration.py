from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.otp_send_email import send_otp_via_email

from ..models import OTP, RegistrationAttempt, User, generate_unique_otp
from ..serializers import PrivateIntialRegistrationSerializer


class PrivateInitialRegistrationView(APIView):
    serializer_class = PrivateIntialRegistrationSerializer

    def post(self, request):
        # success = True
        serializer = PrivateIntialRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]

            # Check rate limiting - 5 attempts in 2 hours
            two_hours_ago = timezone.now() - timedelta(hours=2)
            recent_attempts = RegistrationAttempt.objects.filter(
                email=email, attempt_time__gte=two_hours_ago
            ).count()

            if recent_attempts >= 5:
                return Response(
                    {
                        "status": "error",
                        "message": "Too many registration attempts. Please try again later.",
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Record this attempt
            attempt = RegistrationAttempt.objects.create(email=email)

            user_exists = User.objects.filter(email=email)
            # Check if user exists and is verified
            if user_exists.exists() and user_exists.first().is_verified:
                return Response(
                    {
                        "status": "error",
                        "message": "User with this email already exists",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if user exists but is not verified
            if user_exists.exists() and not user_exists.first().is_verified:
                user = user_exists.first()
                existing_otp = OTP.objects.filter(user=user, is_used=False).first()

                try:
                    # Generate new OTP code
                    otp_code = generate_unique_otp(user)

                    # Try to send email first
                    success, message = send_otp_via_email(email, otp_code)

                    if success:
                        # Update or create OTP
                        if existing_otp:
                            existing_otp.otp_code = otp_code
                            existing_otp.save()
                        else:
                            # Create new OTP if none exists
                            OTP.objects.create(user=user, otp_code=otp_code)

                        attempt.successful = True
                        attempt.save()

                        return Response(
                            {
                                "status": "success",
                                "message": "OTP sent successfully",
                            },
                            status=status.HTTP_201_CREATED,
                        )
                    else:
                        return Response(
                            {
                                "status": "error",
                                "message": "Failed to send OTP: Please try again. ",
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                except Exception as e:
                    return Response(
                        {
                            "status": "error",
                            "message": f"Error generating OTP: {str(e)}. Please try again.",
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            # New user registration - don't save user until email is sent
            try:
                # Generate OTP code directly without user instance
                otp_code = generate_unique_otp(None)  # Modified to handle unsaved user
                # Try to send email first
                success, message = send_otp_via_email(email, otp_code)

                if success:
                    # Only save user if email was sent successfully
                    user = serializer.save()

                    OTP.objects.create(user=user, otp_code=otp_code)

                    # Mark attempt as successful
                    attempt.successful = True
                    attempt.save()

                    return Response(
                        {
                            "status": "success",
                            "message": "User registered successfully",
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {
                            "status": "error",
                            "message": "Failed to send OTP: Please try again. ",
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            except Exception as e:
                return Response(
                    {
                        "status": "error",
                        "message": f"Error during registration: {str(e)}. Please try again.",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"status": "error", "message": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
