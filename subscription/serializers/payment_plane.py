from rest_framework import serializers

from subscription.models import PaymentPlan


class PaymentPlanSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    deduction = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = [
            "id",
            "name",
            "price",
            "description",
            "features",
            "popular",
            "deduction",
        ]

    def get_price(self, obj):
        return int(obj.starting_price)

    def get_features(self, obj):
        features = obj.plan_features.select_related("feature_value__feature").all()
        return [pf.feature_value.value for pf in features]

    def get_deduction(self, obj):
        deductions = obj.durations.select_related("duration").all()
        return [
            {
                "duration_id": duration.duration.id,
                "duration": duration.duration.name,
                "percentage": float(duration.deduction_percentage),
            }
            for duration in deductions
        ]
