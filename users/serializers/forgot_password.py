from rest_framework import serializers

from users.models import User


class PasswordForgotSerializer(serializers.Serializer):  # Fixed typo in class name
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
            # Store the user in validated_data
            self.context["user"] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "User with this email does not exist.",
                }
            )
        return value
