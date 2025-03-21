from rest_framework import serializers

from users.models import User


class TeamUserByOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "organization"]
        read_only_fields = ["id"]
