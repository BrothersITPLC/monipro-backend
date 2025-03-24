from rest_framework import serializers

from infrastructures.models import VM, Network  # Fix the import (vm -> VM)


class VMListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VM
        fields = ["id", "username"]


class NetworkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ["id", "name"]
