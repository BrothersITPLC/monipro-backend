import logging
import os
import textwrap
from decimal import Decimal
from uuid import uuid4

from dotenv import load_dotenv
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.models import OrganizationInfo
from payment.functions import initialize_chapa_payment
from payment.models import Status, Transaction
from subscription.models import PaymentPlanDuration
from utils import ServiceErrorHandler

load_dotenv()

django_logger = logging.getLogger("django")
CHAPA_REDIRECT_URL = os.getenv("CHAPA_REDIRECT_URL")


class ChapaPaymentInitialization(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        payment_provide = request.data.get("payment_provider")
        if not payment_provide:
            return Response(
                {
                    "status": "error",
                    "message": "Please select a payment provider.",
                },
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        if not user.organization:
            return Response(
                {
                    "status": "error",
                    "message": "you need to finish the organization setup before making payments.",
                },
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        try:
            transaction_record = Transaction.objects.create(
                id=uuid4(),
                status=Status.CREATED,
                customer=user.organization,
            )

            organization = OrganizationInfo.objects.filter(
                id=user.organization.id,
            )

            organization.update(
                payment_provider=payment_provide,
            )

            try:
                selected_plan = user.organization.organization_payment_plan
                selected_duration = user.organization.organization_payment_duration
                plan_duration_record = PaymentPlanDuration.objects.get(
                    payment_plan=selected_plan,
                    duration=selected_duration,
                )
            except PaymentPlanDuration.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "The subscription duration you chose isn’t available. Please pick a different option.",
                    },
                    status=http_status.HTTP_400_BAD_REQUEST,
                )

            gross_price = selected_plan.starting_price
            net_price = gross_price * (
                Decimal("1.0")
                - plan_duration_record.deduction_percentage / Decimal("100")
            )

            plane_description = textwrap.shorten(
                selected_plan.description, width=45, placeholder="..."
            )

            payment_payload = {
                "amount": net_price,
                "currency": "ETB",
                "email": user.email,
                "first_name": user.organization.organization_name,
                "phone_number": user.organization.organization_phone,
                "tx_ref": str(transaction_record.id),
                "callback_url": os.getenv("CHAPA_CALLBACK_URL", ""),
                "return_url": f"{CHAPA_REDIRECT_URL}/{transaction_record.id}/",
                "customization": {
                    "title": selected_plan.name,
                    "description": plane_description,
                },
            }

            initialization_response = initialize_chapa_payment(payment_payload)

            if initialization_response.get(
                "status"
            ) == "success" and initialization_response.get("data", {}).get(
                "checkout_url"
            ):
                transaction_record.checkout_url = initialization_response["data"][
                    "checkout_url"
                ]
                transaction_record.status = Status.PENDING
                transaction_record.response_dump = initialization_response
                transaction_record.save()

                return Response(
                    {
                        "status": "success",
                        "message": "Great! We’ve set up your payment link.",
                        "redirect_url": transaction_record.checkout_url,
                    },
                    status=http_status.HTTP_200_OK,
                )

            transaction_record.status = Status.FAILED
            transaction_record.response_dump = initialization_response
            transaction_record.save()
            django_logger.error(
                f"Chapa init failed: {initialization_response.get('message','<no message>')}"
            )
            return Response(
                {
                    "status": "error",
                    "message": "We couldn’t start your payment. Please check your details and try again.",
                },
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        except ServiceErrorHandler:
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
