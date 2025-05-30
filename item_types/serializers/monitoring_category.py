# serializers.py

from rest_framework import serializers

from item_types.models import MonitoringCategory


class MonitoringCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoringCategory
        fields = ["id", "title", "description", "long_description"]
