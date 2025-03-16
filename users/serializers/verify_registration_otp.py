from django.utils import timezone
from rest_framework import serializers

from ..models import OTP, User


class VerifyRegistrationOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get("email")
        otp_code = data.get("otp")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        try:
            otp_instance = OTP.objects.get(user=user, otp_code=otp_code, is_used=False)
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        if timezone.now() > otp_instance.expires_at:
            raise serializers.ValidationError("OTP has expired.")

        data["user"] = user
        data["otp_instance"] = otp_instance
        return data
