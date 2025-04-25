from rest_framework import serializers

from utils import ServiceErrorHandler
from zabbixproxy.models import ZabbixUser


class ZabbixUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZabbixUser
        fields = ["user", "userid", "user_group", "username", "password", "roleid"]
        extra_kwargs = {
            "password": {"write_only": True, "required": False},
            "user": {"read_only": True},
            "user_group": {"read_only": True},
            "roleid": {"required": False},
        }

    def create(self, validated_data):
        # Extract user and user_group from context
        user = self.context.get("user")
        user_group = self.context.get("user_group")
        roleid = self.context.get("roleid")

        if not user or not user_group:
            raise ServiceErrorHandler("User or user group missing in context.")

        # Add context data to validated_data
        validated_data.update(
            {
                "user": user,
                "user_group": user_group,
                "roleid": roleid,
            }
        )

        return super().create(validated_data)
