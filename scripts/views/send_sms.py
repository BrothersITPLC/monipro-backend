from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils import send_single_sms


class SendSMSView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Send a single SMS message to a specified phone number.
        """
        try:
            phone_number = request.data.get("phone_number")
            message = request.data.get("message")

            if not phone_number or not message:
                return Response(
                    {"error": "Phone number and message are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response = send_single_sms(phone_number, message)

            if response["staus"] == "error":
                return Response(
                    response,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return Response(
                response,
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
