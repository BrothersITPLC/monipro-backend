from django.utils import timezone
from rest_framework import serializers

from ..models import PasswordResetOTP, User


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(style={"input_type": "password"})
    password2 = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        email = data.get("email")
        otp_code = data.get("otp")
        password = data.get("password")
        password2 = data.get("password2")

        if password != password2:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "New password and confirmation password don't match.",
                }
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "User with this email does not exist.",
                }
            )

        try:
            otp_instance = PasswordResetOTP.objects.get(
                user=user, otp_code=otp_code, is_used=False
            )
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "Invalid OTP.",
                }
            )

        if timezone.now() > otp_instance.expires_at:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "OTP has expired.",
                }
            )

        data["user"] = user
        data["otp_instance"] = otp_instance
        return data
