# serializers.py
from rest_framework import serializers

from zabbixproxy.models import HostLifecycle


class ActiveHostSerializer(serializers.ModelSerializer):
    host = serializers.CharField(source="host.host")
    host_id = serializers.IntegerField(source="host.host_id")

    class Meta:
        model = HostLifecycle
        fields = ["host", "host_id"]
