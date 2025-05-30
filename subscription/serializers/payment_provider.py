from rest_framework import serializers

from subscription.models import PaymentProvider


class PaymentProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProvider
        fields = [
            "id",
            "name",
        ]
