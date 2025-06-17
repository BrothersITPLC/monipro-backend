from rest_framework import serializers

from zabbixproxy.models import HostLifecycle


class TemplateSerializer(serializers.Serializer):
    template = serializers.JSONField(source="host_monitoring_category.template")

    class Meta:
        model = HostLifecycle
        fields = ["template"]
