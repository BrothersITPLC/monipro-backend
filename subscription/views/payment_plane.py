from rest_framework.response import Response
from rest_framework.views import APIView

from subscription.models import PaymentPlan
from subscription.serializers import PaymentPlanSerializer


class PaymentPlanListView(APIView):
    def get(self, request):
        plans = PaymentPlan.objects.prefetch_related(
            'durations__duration',
            'plan_features__feature_value__feature'
        ).all()
        serialized_plans = PaymentPlanSerializer(plans, many=True).data
        return Response(serialized_plans)
