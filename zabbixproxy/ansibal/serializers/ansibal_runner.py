# ansibal/serializers/ansibal_runner.py

from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers


class AnsibleRequestSerializer(serializers.Serializer):
    ip = serializers.CharField(
        required=False, allow_blank=True, help_text="IP address of the target host"
    )
    dns = serializers.CharField(
        required=False, allow_blank=True, help_text="DNS name of the target host"
    )
    tags = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Tags to be used in the Ansible playbook",
    )
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    port = serializers.IntegerField(
        required=True, validators=[MinValueValidator(1024), MaxValueValidator(65535)]
    )
    hostname = serializers.CharField(required=True)

    def validate(self, data):
        ip = data.get("ip", "").strip()
        dns = data.get("dns", "").strip()
        if not ip and not dns:
            raise serializers.ValidationError("Either 'ip' or 'dns' must be provided.")
        return data
