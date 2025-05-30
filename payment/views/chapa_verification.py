import logging
import os

from dotenv import load_dotenv
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.functions import verify_chapa_payment
from payment.models import Status, Transaction
from utils import ServiceErrorHandler

load_dotenv()

django_logger = logging.getLogger("django")


class ChapaPaymenVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        tx_ref = request.data.get("tx_ref")
        if not tx_ref:
            return Response(
                {
                    "status": "error",
                    "message": "Transaction reference is required.",
                },
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        try:
            transaction_obj = Transaction.objects.get(id=tx_ref)
            if not transaction_obj:
                return Response(
                    {
                        "status": "error",
                        "message": "Transaction not found.",
                    },
                    status=http_status.HTTP_404_NOT_FOUND,
                )

            if (
                transaction_obj.status != Status.CREATED
                and transaction_obj.status != Status.PENDING
            ):
                django_logger.warning(
                    f"Transaction {tx_ref} already processed with status {transaction_obj.status}"
                )
                return Response(
                    {
                        "status": "error",
                        "message": "This transaction has already been processed.",
                    },
                    status=http_status.HTTP_400_BAD_REQUEST,
                )

            try:
                response = verify_chapa_payment(tx_ref)
                if response.get("status") == "success":
                    transaction_obj.status = Status.SUCCESS
                    transaction_obj.response_dump = response
                    transaction_obj.save()
                    return Response(
                        {
                            "status": "success",
                            "message": "Payment successful.",
                            "data": response,
                        },
                        status=http_status.HTTP_200_OK,
                    )
                else:
                    transaction_obj.status = Status.FAILED
                    transaction_obj.response_dump = response
                    transaction_obj.save()
                    django_logger.error(
                        f"Chapa verification failed: {response.get('message', '<no message>')}"
                    )
                    return Response(
                        {
                            "status": "error",
                            "message": "Payment verification failed. Please try again.",
                        },
                        status=http_status.HTTP_400_BAD_REQUEST,
                    )
            except ServiceErrorHandler as e:
                django_logger.exception(
                    f"Service error in ChapaPaymentInitialization - {str(e)}"
                )
                return Response(
                    {
                        "status": "error",
                        "message": "We’re having trouble talking to our payment processor. Please try again in a few minutes.",
                    },
                    status=http_status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                django_logger.exception(
                    f"Unexpected error in ChapaPaymentInitialization - {str(e)}"
                )
                return Response(
                    {
                        "status": "error",
                        "message": "Something went wrong on our end. Please try again later or contact support.",
                    },
                    status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except ServiceErrorHandler as e:
            django_logger.exception(
                f"Service error in ChapaPaymentInitialization - {str(e)}"
            )
            return Response(
                {
                    "status": "error",
                    "message": "We’re having trouble talking to our payment processor. Please try again in a few minutes.",
                },
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        except Exception:
            django_logger.exception("Unexpected error in ChapaPaymentInitialization")
            return Response(
                {
                    "status": "error",
                    "message": "Something went wrong on our end. Please try again later or contact support.",
                },
                status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
