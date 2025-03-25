from rest_framework import serializers

from customers.models import OrganizationInfo
from users.models import User


class PrivateIntialRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "password",
            "password2",
        ]
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
        # Remove password2 as it's not needed for user creation
        password2 = validated_data.pop("password2", None)

        # Set organization info
        organization_website = (
            validated_data.get("organization_website") or validated_data["email"]
        )
        organization_info = OrganizationInfo.objects.create(
            organization_name=f"{validated_data['first_name']} {validated_data['last_name']}",
            organization_phone=validated_data["phone"],
            organization_website=organization_website,
            organization_description="Private account managed by Individual user",
        )

        # Create the user with basic fields
        user = User.objects.create_user(
            email=validated_data["email"],
            name=f"{validated_data['first_name']} {validated_data['last_name']}",
            password=validated_data["password"],
            password2=password2,
        )

        # Set additional fields manually
        user.first_name = validated_data["first_name"]
        user.last_name = validated_data["last_name"]
        user.phone = validated_data["phone"]
        user.role = "is_organization"
        user.is_private = True
        user.organization = organization_info
        user.save()

        return user
