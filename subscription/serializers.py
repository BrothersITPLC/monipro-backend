from rest_framework import serializers

from .models import PaymentPlan


class PaymentPlanSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = ["id", "name", "price", "description", "features", "popular"]

    def get_price(self, obj):
        # Return the amount as an integer (or decimal if needed)
        return int(obj.price.amount)

    def get_features(self, obj):
        # Assumes a related_name "plan_features" is set on PaymentPlanFeature
        # and that each PaymentPlanFeature has a "feature_value" with a "value" field.
        return [pf.feature_value.value for pf in obj.plan_features.all()]
