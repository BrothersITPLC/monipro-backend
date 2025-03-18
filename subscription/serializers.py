from rest_framework import serializers

from .models import PaymentPlan, PaymentPlanFeature, Price


class PaymentPlanDetailSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = PaymentPlan
        fields = ["name", "price", "description", "features", "popular"]

    def get_features(self, obj):
        plan_features = PaymentPlanFeature.objects.filter(payment_plan=obj)
        features_list = []
        for plan_feature in plan_features:
            if plan_feature.value:
                features_list.append(plan_feature.value)
            else:
                features_list.append(plan_feature.feature.name)
        return features_list

    def get_price(self, obj):
        duration_id = self.context.get("duration_id")
        if duration_id:
            price_obj = Price.objects.filter(
                payment_plan=obj, duration_id=duration_id
            ).first()
            if price_obj:
                return float(price_obj.price)
        return float(obj.price)  # Fallback to default price
