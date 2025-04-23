from django.contrib.auth import authenticate
from rest_framework import serializers

from users.models import User
from utils import ServiceErrorHandler


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "email"]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not user:
            raise ServiceErrorHandler(
                "Email or password doesn't match. Please try again."
            )

        if not user.is_verified:
            raise ServiceErrorHandler("Account not verified.")

        # Return the user object instead of just the attributes
        attrs["user"] = user
        return attrs
