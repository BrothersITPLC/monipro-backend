from django.utils import timezone
from rest_framework import serializers

from customers.models import OrganizationInfo
from subscription.models import Duration, PaymentPlan


class OrganizationPaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInfo
        fields = [
            "organization_payment_plan",  # Fixed typo from "plane" to "plan"
            "organization_payment_duration",
        ]

    def validate(self, data):
        payment_plan = data.get("organization_payment_plan")  # Fixed typo
        duration = data.get("organization_payment_duration")

        if not payment_plan:
            raise serializers.ValidationError(
                {"organization_payment_plan": "Payment plan is required"}  # Fixed typo
            )

        if not duration:
            raise serializers.ValidationError(
                {"organization_payment_duration": "Payment duration is required"}
            )

        # Validate if the payment plan exists
        if not PaymentPlan.objects.filter(id=payment_plan.id).exists():
            raise serializers.ValidationError(
                {"organization_payment_plan": "Invalid payment plan selected"}  # Fixed typo
            )

        # Validate if the duration exists
        if not Duration.objects.filter(id=duration.id).exists():
            raise serializers.ValidationError(
                {"organization_payment_duration": "Invalid duration selected"}
            )

        return data

    def update(self, instance, validated_data):
        instance.payment_start_date = timezone.now().date()
        instance = super().update(instance, validated_data)
        instance.save()
        return instance
