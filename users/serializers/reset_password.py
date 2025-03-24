from rest_framework import serializers

from ..models import User


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if not user.is_active:
                raise serializers.ValidationError(
                    {
                        "status": "error",
                        "message": "This account is inactive.",
                    }
                )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "User with this email does not exist.",
                }
            )
        return value
