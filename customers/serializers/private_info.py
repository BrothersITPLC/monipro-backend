from rest_framework import serializers

from customers.models import OrganizationInfo
from subscription.models import Duration


class PrivateInfoViewSerializer(serializers.ModelSerializer):
    duration_id = serializers.IntegerField(write_only=True, required=False)
    user_id = serializers.IntegerField(write_only=True, required=False)

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
            "organization_payment_duration",
            "duration_id",
            "user_id",
        ]

    def validate_user_id(self, value):
        request = self.context.get("request")
        if request and request.user.id != value:
            raise serializers.ValidationError(
                "Provided user id does not match the authenticated user."
            )
        return value

    def validate(self, data):
        duration_id = data.pop("duration_id", None)
        if duration_id is not None:
            try:
                duration_instance = Duration.objects.get(id=duration_id)
            except Duration.DoesNotExist:
                raise serializers.ValidationError(
                    {"duration_id": "Invalid duration id"}
                )
            data["organization_payment_duration"] = duration_instance
        return data
