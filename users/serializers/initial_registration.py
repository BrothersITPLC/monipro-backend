# serializers.py
from rest_framework import serializers

from users.models import User
from utils import ServiceErrorHandler


class InitialRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}, "id": {"read_only": True}}

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            raise ServiceErrorHandler("Password and Confirm Password do not match")

        return attrs

    def create(self, validated_data):
        validated_data["is_admin"] = True
        return User.objects.create_user(**validated_data)
