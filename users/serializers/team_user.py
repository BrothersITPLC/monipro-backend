from rest_framework import serializers

from users.models import User


class TeamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "organization",
            "role",
            "phone",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["role"]

    def create(self, validated_data):
        default_password = validated_data.pop("default_password", None)
        if not default_password:
            default_password = User.objects.make_random_password()

        user = User.objects.create_user(
            email=validated_data["email"],
            name=validated_data["name"],
            password=default_password,
            password2=default_password,
            role="is_team",
            organization=validated_data["organization"],
            is_verified=True,
        )

        # Add additional fields if provided
        for field in ["phone", "first_name", "last_name"]:
            if field in validated_data:
                setattr(user, field, validated_data[field])

        user.save()
        return user
