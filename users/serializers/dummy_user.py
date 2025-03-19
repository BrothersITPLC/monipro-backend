from rest_framework import serializers

from users.models import DummyUser


class DummyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DummyUser
        fields = ["id", "first_name", "last_name", "email", "organization"]
        read_only_fields = ["id"]
