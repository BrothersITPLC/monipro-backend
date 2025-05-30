import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from subscription.models import PaymentProvider
from subscription.serializers import PaymentProviderSerializer

django_logger = logging.getLogger("django")


class PaymentProviderView(APIView):
    def get(self, request):
        try:
            payment_providers = PaymentProviderSerializer(
                PaymentProvider.objects.all(), many=True, context={"request": request}
            )
            return Response(
                {
                    "status": "success",
                    "message": "Payment providers retrieved successfully",
                    "data": payment_providers.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            django_logger.error(f"Error retrieving payment providers: {str(e)}")
            return Response(
                {
                    "status": "error",
                    "message": "An unexpected error occurred: while retrieving payment providers",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
