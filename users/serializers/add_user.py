from rest_framework import serializers

from users.models import User
from utils import ServiceErrorHandler


class AddUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_admin",
            "password",
            "organization",
            "phone",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "id": {"read_only": True},
        }

    def create(self, validated_data):
        password = self.context.get("password")
        organization = self.context.get("organization")
        is_verified = self.context.get("is_verified", False)
        is_active = self.context.get("is_active", False)

        if not organization:
            raise ServiceErrorHandler(
                "Organization instance was not provided in context."
            )

        if not password:
            raise ServiceErrorHandler("Password is required but was not provided.")

        validated_data["password"] = password
        validated_data["password2"] = password
        validated_data["organization"] = organization
        validated_data["is_verified"] = is_verified
        validated_data["is_active"] = is_active

        return User.objects.create_user(**validated_data)
