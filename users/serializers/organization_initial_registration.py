from rest_framework import serializers

from users.models import User


class OrganizationInitialRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "name", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}, "id": {"read_only": True}}

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError(
                {
                    "status": "error",
                    "Message": "Password and Confirm Password Doesn't Match",
                }
            )
        return attrs

    def create(self, validated_data):
        validated_data["is_organization"] = True
        user = User.objects.create_user(**validated_data)
        if not user.is_organization:
            user.is_organization = True
            user.save(update_fields=["is_organization"])
        return user
