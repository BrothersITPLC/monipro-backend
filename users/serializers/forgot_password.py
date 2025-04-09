from rest_framework import serializers

from users.models import User
from utils import ServiceErrorHandler


class PasswordForgotSerializer(serializers.Serializer):  # Fixed typo in class name
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.is_from_social and not user.social_and_local_is_linked:
                raise ServiceErrorHandler("This email is associated with a social account.")
            if not user.is_active:
                raise ServiceErrorHandler("This account is inactive.")
            self.context["user"] = user
        except User.DoesNotExist:
            raise ServiceErrorHandler("User with this email does not exist.")
        return value
