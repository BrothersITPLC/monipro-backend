from rest_framework import serializers

from users.models import User


class TeamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_admin",
            "is_active",
            "phone",
        ]
