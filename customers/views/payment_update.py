from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.models import OrganizationInfo
from customers.serializers import OrganizationPaymentUpdateSerializer


class OrganizationPaymentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            organization = OrganizationInfo.objects.get(pk=pk)
            serializer = OrganizationPaymentUpdateSerializer(
                organization, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Payment plan updated successfully",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "status": "error",
                    "message": "Invalid data provided",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except OrganizationInfo.DoesNotExist:
            return Response(
                {"status": "error", "message": "Organization not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "An error occurred while updating payment plan",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
