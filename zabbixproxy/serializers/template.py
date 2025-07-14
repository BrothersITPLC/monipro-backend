from rest_framework import serializers

from zabbixproxy.models import TemplateMirror


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateMirror
        fields = "__all__"
