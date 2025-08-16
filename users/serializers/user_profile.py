# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

from payment.models import Transaction
from users.serializers import ProfilePictureUpdateSerializer
from zabbixproxy.models import ZabbixHostGroup, ZabbixUser, ZabbixUserGroup

User = get_user_model()
import logging

django_logger = logging.getLogger("django")


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source="id")
    user_name = serializers.CharField(source="name")
    user_email = serializers.EmailField(source="email")
    organization_info_completed = serializers.SerializerMethodField()
    user_have_zabbix_credentials = serializers.SerializerMethodField()
    user_have_zabbix_user = serializers.SerializerMethodField()
    user_have_completed_payment = serializers.SerializerMethodField()

    # Organization fields (conditionally included)
    organization_id = serializers.IntegerField(
        source="organization.id", allow_null=True
    )
    organization_name = serializers.CharField(
        source="organization.organization_name", allow_null=True
    )
    organization_phone = serializers.CharField(
        source="organization.organization_phone", allow_null=True
    )
    organization_website = serializers.URLField(
        source="organization.organization_website", allow_null=True
    )
    organization_description = serializers.CharField(
        source="organization.organization_description", allow_null=True
    )
    organization_payment_plan = serializers.SerializerMethodField()
    organization_payment_duration = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "user_name",
            "user_email",
            "first_name",
            "last_name",
            "phone",
            "profile_picture",
            "is_private",
            "is_admin",
            "phone",
            "organization_info_completed",
            "user_have_zabbix_credentials",
            "user_have_zabbix_user",
            "organization_id",
            "organization_name",
            "organization_phone",
            "organization_website",
            "organization_description",
            "organization_payment_plan",
            "organization_payment_duration",
            "user_have_completed_payment",
        ]

    def get_organization_info_completed(self, obj):
        return hasattr(obj, "organization") and obj.organization is not None

    def get_user_have_zabbix_credentials(self, obj):
        return (
            ZabbixHostGroup.objects.filter(created_by=obj).exists()
            and ZabbixUserGroup.objects.filter(created_by=obj).exists()
        )

    def get_user_have_zabbix_user(self, obj):
        return ZabbixUser.objects.filter(user=obj).exists()

    def get_organization_payment_plan(self, obj):
        if not hasattr(obj, "organization") or not obj.organization:
            return None
        return (
            obj.organization.organization_payment_plan.name
            if obj.organization.organization_payment_plan
            else None
        )

    def get_user_have_completed_payment(self, obj):
        organization = getattr(obj, "organization", None)
        if not organization:
            return None
        transaction = (
            Transaction.objects.filter(customer=organization).order_by("-id").first()
        )
        return transaction.status if transaction else None

    def get_organization_payment_duration(self, obj):
        if not hasattr(obj, "organization") or not obj.organization:
            return None
        return (
            obj.organization.organization_payment_duration.name
            if obj.organization.organization_payment_duration
            else None
        )

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get("request")
            if request is not None:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None