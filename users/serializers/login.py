from django.contrib.auth import authenticate
from rest_framework import serializers

from ..models import User


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
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "message": "Email or password doesn't match. Please try again.",
                }
            )

        if not user.is_verified:
            raise serializers.ValidationError(
                {"status": "error", "message": "Account not verified."}
            )
        
        # Return the user object instead of just the attributes
        attrs["user"] = user
        return attrs
