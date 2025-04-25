from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import User
from utils import ServiceErrorHandler


class UserActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "is_active"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        try:
            instance.is_active = validated_data.get("is_active", instance.is_active)
            instance.save(update_fields=["is_active"])
            return instance
        except Exception as e:
            raise ServiceErrorHandler("Failed to update user status") from e
