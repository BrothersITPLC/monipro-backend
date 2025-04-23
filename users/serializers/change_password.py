from rest_framework import serializers

from utils import ServiceErrorHandler


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context["request"].user
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if not user.social_and_local_is_linked and user.is_from_social:
            raise ServiceErrorHandler(
                "You cannot change your password because you signed up using a social account."
            )

        if not user.check_password(old_password):
            raise ServiceErrorHandler("Old password is incorrect.")

        if new_password != confirm_password:
            raise ServiceErrorHandler("Passwords do not match.")

        if old_password == new_password:
            raise ServiceErrorHandler(
                "New password cannot be the same as the old password."
            )

        return attrs

    def save(self, **kwargs):
        try:
            user = self.context["request"].user
            new_password = self.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            return user
        except Exception as e:
            raise ServiceErrorHandler("Failed to update password.")
