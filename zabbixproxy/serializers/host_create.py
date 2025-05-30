from rest_framework import serializers

from utils import ServiceErrorHandler
from zabbixproxy.models import Host


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = "__all__"

    def validate(self, data):
        device_type = data.get(
            "device_type", getattr(self.instance, "device_type", None)
        )
        network_device_type = data.get(
            "network_device_type", getattr(self.instance, "network_device_type", None)
        )

        if device_type == "network" and not network_device_type:
            raise ServiceErrorHandler(
                "network device type required when device_type is 'network'."
            )

        return data
