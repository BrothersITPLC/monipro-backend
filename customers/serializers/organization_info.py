# serializers.py
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from rest_framework import serializers

from customers.models import OrganizationInfo
from utils import ServiceErrorHandler

User = get_user_model()

class OrganizationInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True, required=True)

    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    is_private = serializers.BooleanField(required=False)
    organization_description = serializers.CharField(required=False, allow_blank=True)
    organization_website = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = OrganizationInfo
        fields = [
            "id",
            "organization_name",
            "organization_phone",
            "organization_website",
            "organization_description",
            "payment_provider",
            "organization_payment_plan",
            "organization_payment_duration",
            "user_id",
            "is_private",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id"]
        # Removed required=True from extra_kwargs to handle manually

    def validate(self, attrs):
        # Required field checks with specific messages
        required_errors = []
        if not attrs.get("organization_phone"):
            required_errors.append("Organization phone is required")
        if not attrs.get("payment_provider"):
            required_errors.append("Payment provider is required")
        if not attrs.get("organization_payment_plan"):
            required_errors.append("Payment plan is required")
        if not attrs.get("organization_payment_duration"):
            required_errors.append("Payment duration is required")
        if required_errors:
            raise ServiceErrorHandler(", ".join(required_errors))

        # Phone validation
        organization_phone = attrs.get("organization_phone", "").strip()
        if not organization_phone:
            raise ServiceErrorHandler("Phone number cannot be empty")

        # Privacy-based validation
        is_private = attrs.get("is_private")
        first_name = attrs.get("first_name", "").strip()
        last_name = attrs.get("last_name", "").strip()

        if is_private:
            if not first_name:
                raise ServiceErrorHandler("First name is required for private organizations")
            if not last_name:
                raise ServiceErrorHandler("Last name is required for private organizations")
            attrs["organization_name"] = f"{first_name} {last_name}"
        else:
            if not attrs.get("organization_name"):
                raise ServiceErrorHandler("Organization name is required")

        return attrs

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        is_private = validated_data.pop("is_private")
        first_name = validated_data.pop("first_name", "").strip()
        last_name = validated_data.pop("last_name", "").strip()

        # Clean optional fields
        for field in ["organization_website", "organization_description"]:
            if validated_data.get(field) == "":
                validated_data[field] = None

        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ServiceErrorHandler(f"User with id {user_id} does not exist")

        # Create organization with DB error handling
        try:
            organization = OrganizationInfo.objects.create(**validated_data)
        except DatabaseError as e:
            raise ServiceErrorHandler("Database error occurred please try again")

        # Update user
        try:
            user.organization = organization
            user.phone = validated_data["organization_phone"]
            user.is_private = is_private

            if is_private:
                user.first_name = first_name or None
                user.last_name = last_name or None
                user.username= f"{first_name} {last_name}"
            else:
                user.username = validated_data["organization_name"]

            user.save()
        except DatabaseError as e:
            # Rollback organization creation if user update fails
            organization.delete()
            raise ServiceErrorHandler("Database error occurred please try again")

        return organization
