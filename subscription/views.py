from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Duration, PaymentPlan, Price
from .serializers import PaymentPlanDetailSerializer


class PaymentPlanListView(APIView):
    def get(self, request):
        durations = Duration.objects.all()
        result = {}

        for duration in durations:
            # Get all payment plans that have prices for this duration
            payment_plans_ids = Price.objects.filter(duration=duration).values_list(
                "payment_plan_id", flat=True
            )
            payment_plans = PaymentPlan.objects.filter(id__in=payment_plans_ids)

            # Serialize each payment plan with the context of the current duration
            serializer = PaymentPlanDetailSerializer(
                payment_plans, many=True, context={"duration_id": duration.id}
            )

            # Use the duration name (like "monthly" or "yearly") as the key
            duration_key = duration.duration.lower()
            result[duration_key] = serializer.data

        return Response(result, status=status.HTTP_200_OK)
