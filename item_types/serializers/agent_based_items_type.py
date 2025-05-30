from rest_framework import serializers

from item_types.models import AgentMonitoringItemType


class AgentMonitoringItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentMonitoringItemType
        fields = ["id", "name", "description"]
