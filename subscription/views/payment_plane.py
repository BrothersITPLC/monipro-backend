from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from subscription.models import PaymentPlan
from subscription.serializers import PaymentPlanSerializer


class PaymentPlanListView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of all available payment plans with their features and pricing details",
        operation_summary="List all payment plans",
        responses={
            200: openapi.Response(
                description="List of payment plans",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='Unique identifier for the payment plan'
                            ),
                            'name': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='Name of the payment plan'
                            ),
                            'price': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='Starting price of the plan (integer value)'
                            ),
                            'description': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description='Detailed description of the payment plan'
                            ),
                            'features': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                description='List of features included in this plan',
                                items=openapi.Schema(
                                    type=openapi.TYPE_STRING
                                )
                            ),
                            'popular': openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                description='Indicates if this is a popular/recommended plan'
                            ),
                            'deduction': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                description='Available duration options with pricing deductions',
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'duration_id': openapi.Schema(
                                            type=openapi.TYPE_INTEGER,
                                            description='ID of the duration option'
                                        ),
                                        'duration': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            description='Name of the duration (monthly, quarterly, yearly)',
                                            enum=['monthly', 'quarterly', 'yearly']
                                        ),
                                        'percentage': openapi.Schema(
                                            type=openapi.TYPE_NUMBER,
                                            format='float',
                                            description='Discount percentage for this duration'
                                        )
                                    }
                                )
                            )
                        }
                    )
                )
            )
        }
    )
    def get(self, request):
        plans = PaymentPlan.objects.prefetch_related(
            'durations__duration',
            'plan_features__feature_value__feature'
        ).all()
        serialized_plans = PaymentPlanSerializer(plans, many=True).data
        return Response(serialized_plans)
