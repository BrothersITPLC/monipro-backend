from rest_framework import serializers

from customers.models import OrganizationInfo
from users.models import User
from utils import ServiceErrorHandler


class UpdateProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)

    organization_name = serializers.CharField(required=False)
    organization_phone = serializers.CharField(required=False)
    organization_website = serializers.URLField(required=False)
    organization_description = serializers.CharField(required=False)

    def validate_phone(self, value):
        user_qs = User.objects.filter(phone=value)
        org_qs = OrganizationInfo.objects.filter(organization_phone=value)

        if self.instance:
            user_qs = user_qs.exclude(id=self.instance.id)
            if hasattr(self.instance, "organization") and self.instance.organization:
                org_qs = org_qs.exclude(id=self.instance.organization.id)

        if user_qs.exists():
            raise ServiceErrorHandler("This phone number is already registered")

        if org_qs.exists():
            raise ServiceErrorHandler("This phone number is already registered")

        return value

    def update(self, instance, validated_data):
        user = instance
        org = getattr(user, "organization", None)

        first_name = validated_data.get("first_name", user.first_name)
        last_name = validated_data.get("last_name", user.last_name)

        for field in ["first_name", "last_name"]:
            if field in validated_data:
                setattr(user, field, validated_data[field])
        cap_first_name = first_name.capitalize()
        cap_last_name = last_name.capitalize()
        user.name = f"{cap_first_name} {cap_last_name}"

        if user.is_private and org:
            org.organization_name = f"{first_name} {last_name}"

        phone = validated_data.get("phone")
        if phone:
            validated_phone = self.validate_phone(phone)
            user.phone = validated_phone

            if user.is_private:
                if org:
                    org.organization_phone = validated_phone
            else:
                if user.is_admin and org:
                    org.organization_phone = validated_phone

        org_fields = ["organization_website", "organization_description"]
        for field in org_fields:
            if field in validated_data:
                if not org:
                    raise ServiceErrorHandler("Organization information not found.")
                setattr(org, field, validated_data[field])

        try:
            user.save()
            if org:
                org.save()
        except Exception as e:
            raise ServiceErrorHandler(f"An error occurred while saving: {str(e)}")
        return user
