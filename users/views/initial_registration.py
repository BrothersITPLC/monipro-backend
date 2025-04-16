import logging
from datetime import timedelta

from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import OTP, RegistrationAttempt, User, generate_unique_otp
from users.serializers import InitialRegistrationSerializer
from utils import ServiceErrorHandler
from utils.otp_send_email import send_otp_via_email

django_logger = logging.getLogger("django")


class InitialRegistrationView(APIView):
    """
    API endpoint for initial organization registration with email verification.

    Requires:
    - email (string): Valid organization email
    - name (string): Organization name
    - password (string): Minimum 8 characters
    - password2 (string): Must match password

    Returns:
    - Success: 201 with verification status
    - Error: 4xx/5xx with error details
    """

    serializer_class = InitialRegistrationSerializer

    @swagger_auto_schema(
        operation_id="organization_initial_registration",
        operation_description="Initiate organization registration with email verification",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password", "password2"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password"),
                "password2": openapi.Schema(
                    type=openapi.TYPE_STRING, format="password"
                ),
            },
            example={
                "email": "org@example.com",
                "password": "securepass123",
                "password2": "securepass123",
            },
        ),
        responses={
            201: openapi.Response(
                description="OTP sent successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "OTP sent successfully",
                    }
                },
            ),
            400: openapi.Response(
                description="Validation error",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": {
                            "password": ["This field is required."],
                            "email": ["Enter a valid email address."],
                        },
                    }
                },
            ),
            429: openapi.Response(
                description="Rate limit exceeded",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Too many registration attempts. Please try again later.",
                    }
                },
            ),
            500: openapi.Response(
                description="Server error",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Failed to send OTP email",
                    }
                },
            ),
        },
    )
    def post(self, request):
        serializer = InitialRegistrationSerializer(data=request.data)

        try:
            # Validation
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data["email"]

            # Rate limiting check
            two_hours_ago = timezone.now() - timedelta(hours=2)
            recent_attempts = RegistrationAttempt.objects.filter(
                email=email, attempt_time__gte=two_hours_ago
            ).count()

            if recent_attempts >= 5:
                raise ServiceErrorHandler(
                    "Too many registration attempts. Please try again later."
                )

            # Create attempt record
            attempt = RegistrationAttempt.objects.create(email=email)

            # Check existing users
            user_exists = User.objects.filter(email=email)
            if user_exists.exists():
                user = user_exists.first()
                if user.is_verified:
                    raise ServiceErrorHandler("User with this email already exists")

                # Handle existing unverified user
                existing_otp = OTP.objects.filter(user=user, is_used=False).first()
                otp_code = generate_unique_otp(user)

                # Send OTP
                success, message = send_otp_via_email(email, otp_code)
                if not success:
                    django_logger.info(f"Failed to send OTP email: {message}")
                    raise ServiceErrorHandler("Failed to send OTP: Please try again.")

                # Update/create OTP
                if existing_otp:
                    existing_otp.otp_code = otp_code
                    existing_otp.save()
                else:
                    OTP.objects.create(user=user, otp_code=otp_code)

                attempt.successful = True
                attempt.save()
                return Response(
                    {"status": "success", "message": "OTP sent successfully"},
                    status=status.HTTP_201_CREATED,
                )

            # New user registration
            otp_code = generate_unique_otp(None)  # Pass None for unsaved user
            success, message = send_otp_via_email(email, otp_code)

            if not success:
                raise ServiceErrorHandler("Failed to send OTP: Please try again.")

            # Save user only after successful email send
            user = serializer.save()
            OTP.objects.create(user=user, otp_code=otp_code)

            attempt.successful = True
            attempt.save()

            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully, please check your email for the OTP.",
                },
                status=status.HTTP_201_CREATED,
            )

        except ServiceErrorHandler as e:
            # Determine status code based on message content
            message = str(e)
            status_code = status.HTTP_400_BAD_REQUEST

            if "Too many registration" in message:
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif "already exists" in message:
                status_code = status.HTTP_400_BAD_REQUEST
            elif "Failed to send OTP" in message:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            return Response({"status": "error", "message": message}, status=status_code)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred, please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
