from rest_framework import serializers

from zabbixproxy.models import TemplateGroupMirror
from zabbixproxy.serializers.template import TemplateSerializer


class TemplateGroupMirrorSerializer(serializers.ModelSerializer):
    templates = TemplateSerializer(many=True, read_only=True)

    class Meta:
        model = TemplateGroupMirror
        fields = "__all__"
