from rest_framework import serializers

from zabbixproxy.models import TemplateGroupMirror


class TemplateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateGroupMirror
        fields = "__all__"
