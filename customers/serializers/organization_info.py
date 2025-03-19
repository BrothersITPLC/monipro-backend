from rest_framework import serializers

from customers.models import OrganizationInfo


class OrganizationInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = OrganizationInfo
        fields = [
            "id",
            "organization_name",
            "organization_phone",
            "organization_website",
            "organization_description",
            "payment_provider",
            "organization_payment_plane",
            "user_id",
        ]
        read_only_fields = ["id"]
