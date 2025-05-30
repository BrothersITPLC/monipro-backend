from rest_framework import serializers

from item_types.models import SimpleCheckItemTypes


class SimpleCheckItemTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleCheckItemTypes
        fields = ["id", "name", "description"]
