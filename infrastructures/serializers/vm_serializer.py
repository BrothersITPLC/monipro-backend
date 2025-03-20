from rest_framework import serializers

from infrastructures.models import VM


class VMSerializer(serializers.ModelSerializer):
    class Meta:
        model = VM
        fields = "__all__"
