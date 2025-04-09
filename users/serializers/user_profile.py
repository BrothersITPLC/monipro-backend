# serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

from zabbixproxy.models import ZabbixHostGroup, ZabbixUser, ZabbixUserGroup

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id')
    user_name = serializers.CharField(source='name')
    user_email = serializers.EmailField(source='email')
    organization_info_completed = serializers.SerializerMethodField()
    user_have_zabbix_credentials = serializers.SerializerMethodField()
    user_have_zabbix_user = serializers.SerializerMethodField()
    
    # Organization fields (conditionally included)
    organization_id = serializers.IntegerField(source='organization.id', allow_null=True)
    organization_name = serializers.CharField(source='organization.organization_name', allow_null=True)
    organization_phone = serializers.CharField(source='organization.organization_phone', allow_null=True)
    organization_website = serializers.URLField(source='organization.organization_website', allow_null=True)
    organization_description = serializers.CharField(source='organization.organization_description', allow_null=True)
    organization_payment_plane = serializers.SerializerMethodField()
    organization_payment_duration = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id', 'user_name', 'user_email', 'first_name', 'last_name',
            'phone', 'is_private', 'is_admin', 'organization_info_completed',
            'user_have_zabbix_credentials', 'user_have_zabbix_user',
            'organization_id', 'organization_name', 'organization_phone',
            'organization_website', 'organization_description',
            'organization_payment_plane', 'organization_payment_duration'
        ]

    def get_organization_info_completed(self, obj):
        return hasattr(obj, 'organization') and obj.organization is not None

    def get_user_have_zabbix_credentials(self, obj):
        return (ZabbixHostGroup.objects.filter(created_by=obj).exists() and
                ZabbixUserGroup.objects.filter(created_by=obj).exists())

    def get_user_have_zabbix_user(self, obj):
        return ZabbixUser.objects.filter(user=obj).exists()

    def get_organization_payment_plane(self, obj):
        if not hasattr(obj, 'organization') or not obj.organization:
            return None
        return obj.organization.organization_payment_plane.name \
            if obj.organization.organization_payment_plane else None

    def get_organization_payment_duration(self, obj):
        if not hasattr(obj, 'organization') or not obj.organization:
            return None
        return obj.organization.organization_payment_duration.name \
            if obj.organization.organization_payment_duration else None