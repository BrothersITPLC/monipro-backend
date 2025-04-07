from rest_framework import serializers

from zabbixproxy.models import ZabbixHost


class ZabbixHostSerializer(serializers.ModelSerializer):
    hostgroup_name = serializers.CharField(source="hostgroup.name", read_only=True)
    hostgroupid = serializers.CharField(source="hostgroup.hostgroupid", read_only=True)

    class Meta:
        model = ZabbixHost
        fields = [
            "id",
            "host",
            "hostid",
            "ip",
            "dns",
            "port",
            "hostgroup_name",
            "hostgroupid",
            "device_type",
            "dns",
            "network_device_type",
            "network_type",
        ]
