from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaymentPlan
from .serializers import PaymentPlanSerializer


class PaymentPlanListView(APIView):
    def get(self, request):
        monthly_plans = PaymentPlan.objects.filter(
            price__duration__name__iexact="Monthly"
        )
        yearly_plans = PaymentPlan.objects.filter(
            price__duration__name__iexact="Yearly"
        )

        data = {
            "monthly": PaymentPlanSerializer(monthly_plans, many=True).data,
            "yearly": PaymentPlanSerializer(yearly_plans, many=True).data,
        }
        return Response(data)
